import numpy
from PIL import Image,ImageFilter

#Input image
Img = Image.open("input.jpg")
Img.show()

for w in range(0, 100):
   for h in range(0, 100):
       Img.putpixel((w,h), tuple([255,0,0]))

Img.show()
