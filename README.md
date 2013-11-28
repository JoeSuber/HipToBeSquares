HipToBeSquares
==============

Square objects (ie. blobs, contours) in camera feed are picked out using some parameters you may adjust on-the-fly.

Based on squares.py sample from opencv, this program lets you find out what values of some params

are best for your image segmentation task - assuming that it will involve some square-ish

objects.  Uses the 'defaultdict' to generate and track a bunch of open windows so that you can see 

which levels capture which parts of whatever is in the cam-feed - and estimate the reliability through

different lighting conditions.  Docstring has adjustment keys.

Todo: Refine the destruction of laggard windows to give a more 'stable' selection / view
