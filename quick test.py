import numpy
from PIL import Image,ImageFilter

import sys


a = 0
for x in range (0,3):
    a = a + 1
    b = ("Loading" + "." * a)
    # \r prints a carriage return first, so `b` is printed on top of the previous line.
    sys.stdout.write('\r'+b)
    time.sleep(0.5)


input("Press the <ENTER> key to exit...")