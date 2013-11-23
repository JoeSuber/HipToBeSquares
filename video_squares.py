#!/usr/bin/env python

'''
Video "Square Detector" program.
explore effects of various settings use
+ -     change acceptable angles in corner vertexes,
w q     change the aperture of the binarizing Canny function
a s     change the window winnowing cut-point (start at .85)
        (only used when thrs=0)
<space> clear the windows
camera images are dissected for contours & squares - see what cpu sees
when you are trying to segment an image from your camera feed.  typical fps = 3 - 4
'''

import numpy as np
import cv2
from collections import defaultdict

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def find_squares(img, app, ang):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = defaultdict(list)
    for screen, gray in enumerate(cv2.split(img)):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                binar = cv2.Canny(gray, 0, 50, apertureSize=app)
                binar = cv2.dilate(binar, None)
            else:
                retval, binar = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            binar, contours, hierarchy = cv2.findContours(binar, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            HAS_SQUARE = False
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    if max_cos < ang/float(10000):
                        squares[(screen, thrs, app, ang)].append(cnt)
                        HAS_SQUARE = True
            if HAS_SQUARE:
                squares[(screen, thrs, app, ang)].append(binar.copy())
    return squares

if __name__ == '__main__':
    ch = ''
    cut = 0.85
    PAUSE = True
    sqr_list = []
    app, ang, count = 5, 1700, 0
    cam = cv2.VideoCapture(-1)
    #cv2.accumulate()
    window_track = defaultdict(int)
    ret, frame = cam.read()

    # get camera going
    while not ret:
        ret, frame = cam.read()
        count += 1
        if not count % 100:
            print('waiting for cam to fire up')
        elif not count % 5000:
            print('exit because cam is taking too long to start')
            exit(0)

    # loop until no cam feed or break
    while ret:
        ret, frame = cam.read()
        img = frame.copy()
        squares = find_squares(img, app, ang )
        cv2.imshow('main output ', img)
        window_roster = []

        # draw the windows that have something

        for kk, vv in squares.viewitems():
            king_window = 0
            if window_track[kk] > king_window:
                king_window = window_track[kk]


        for kk in window_track.viewkeys():
            if isinstance(vv[-1], np.ndarray):
                disp = cv2.cvtColor(vv.pop(), cv2.COLOR_GRAY2BGR)
                cv2.drawContours(disp, vv, -1, (0,255,255), 3)
                window_roster.append(kk)
                window_track[kk] += 1
            if window_track[kk] > (king_window * cut):
                cv2.putText(disp, 'frames= {}'.format(window_track[kk]), (20, disp.shape[1]/3),
                            cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.imshow('spl={} thr={} aptr={} ang={} '.format(*kk), disp)

        # destroy the laggards

        for label in window_track.viewkeys():
            if label not in window_roster and window_track[label] < (cut * king_window):
                cv2.destroyWindow('spl={} thr={} aptr={} ang={} '.format(*label))

        # get user key inputs

        ch = 0xFF & cv2.waitKey(PAUSE)q
        if ch != (0xFF & -1):
            if ch == 27:
                break
            elif ch == ord('+'):
                if app < 7:
                    app += 2
            elif ch == ord('-'):
                if app > 1:
                    app -= 2
            elif ch == ord('w'):
                ang += 15
            elif ch == ord('q'):
                ang -= 15
            elif ch == ord('a'):
                cut -= .01
            elif ch == ord('s'):
                cut += .01
            elif ch == ord('p'):
                PAUSE = not PAUSE
            elif ch == ord(' '):
                cv2.destroyAllWindows()
                window_track.clear()
            print('aperture= {}   max vertex cos(angle)= {}   win-cutoff= {}'.format(app, ang, cut))
    cv2.destroyAllWindows()
