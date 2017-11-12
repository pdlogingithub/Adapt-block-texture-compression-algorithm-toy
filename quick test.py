import numpy
from PIL import Image
from PIL import ImageFilter

Img = Image.open("input.jpg")

Img = Img.filter(ImageFilter.BLUR)
Img.show()

ImgArray = numpy.arange(Img.width * Img.height * 3, dtype=numpy.uint8).reshape(Img.width, Img.height, 3)

Img.getpixel((120, 120))

for w in range(0, Img.width):
   for h in range(0, Img.height):
       Img.putpixel((w, h), (0,128,0))
Img.save("output.jpg")