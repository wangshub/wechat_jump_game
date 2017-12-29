from PIL import Image
from pylab import *

im = array(Image.open('2.png').convert('L'))

figure()
gray()

contour(im, origin='image')
