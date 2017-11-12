import numpy
from PIL import Image,ImageFilter
import sys

Img = Image.open("input.jpg")
ImgBlur=Img.filter(ImageFilter.BLUR)

BlockSizeX = 12
BlockSizeY = 12

ImgArray = numpy.arange(Img.width * Img.height * 3, dtype=numpy.uint8).reshape(Img.width, Img.height, 3)
ImgArrayBlur= numpy.arange(Img.width * Img.height * 3, dtype=numpy.uint8).reshape(Img.width, Img.height, 3)

for w in range(0, Img.width):
    for h in range(0, Img.height):
        ImgArray[w][h] = Img.getpixel((w, h))
        ImgArrayBlur[w][h] = ImgBlur.getpixel((w, h))

BlockCountX = (int)(Img.width / BlockSizeX) if Img.width % BlockSizeX == 0 else (int)(Img.width / BlockSizeX) + 1
BlockCountY = (int)(Img.height / BlockSizeY) if Img.height % BlockSizeY == 0 else (int)(Img.height / BlockSizeY) + 1

OutputArray=numpy.array([[[[0,0,0],[0,0,0],[[[False,False] for i in range(BlockSizeY)] for i in range(BlockSizeX)]] for i in range(BlockCountX)] for i in range(BlockCountX)])
print(sys.getsizeof(OutputArray))

for BlockX in range(0, BlockCountX):
    for BlockY in range(0, BlockCountY ):
        ColorA = numpy.arange(3,dtype=numpy.uint8)
        ColorB = numpy.arange(3,dtype=numpy.uint8)
        ColorDistance = 0.0
        for PixelX1 in range(0, BlockSizeX ):
            for PixelY1 in range(0, BlockSizeY):
                for PixelX2 in range(0, BlockSizeX):
                    for PixelY2 in range(0, BlockSizeY):
                        X1 = BlockX * BlockSizeX + PixelX1
                        Y1 = BlockY * BlockSizeY + PixelY1
                        X2 = BlockX * BlockSizeX + PixelX2
                        Y2 = BlockY * BlockSizeY + PixelY2
                        if X1 > Img.width-1 or Y1 > Img.height-1 or X2 > Img.width-1 or Y2 > Img.height-1:
                            continue
                        ColorOffset = [(int)(ImgArrayBlur[X1][Y1][i]) - (int)(ImgArrayBlur[X2][Y2][i]) for i in range(3)]
                        NewColorDistance = (ColorOffset[0] ** 2 + ColorOffset[1] ** 2 + ColorOffset[2] ** 2) ** 0.5
                        if ColorDistance < NewColorDistance:
                            ColorDistance = NewColorDistance
                            ColorA=ImgArrayBlur[X1][Y1]
                            ColorB=ImgArrayBlur[X2][Y2]
        OutputArray[BlockX][BlockY][0] = ColorA
        OutputArray[BlockX][BlockY][1] = ColorB
        for PixelX in range(0, BlockSizeX ):
            for PixelY in range(0, BlockSizeY):
                X = BlockX * BlockSizeX + PixelX
                Y = BlockY * BlockSizeY + PixelY
                if X > Img.width - 1 or Y > Img.height - 1:
                    continue
                ColorOffsetA = [(int)(ImgArray[X][Y][i]) - (int)(ColorA[i]) for i in range(3)]
                ColorOffsetB = [(int)(ImgArray[X][Y][i]) - (int)(ColorB[i]) for i in range(3)]
                ColorDistanceA = (ColorOffsetA[0] ** 2 + ColorOffsetA[1] ** 2 + ColorOffsetA[2]**2) ** 0.5
                ColorDistanceB = (ColorOffsetB[0] ** 2 + ColorOffsetB[1] ** 2 + ColorOffsetB[2]**2) ** 0.5
                ColorWeight=ColorDistanceA/(ColorDistanceA+ColorDistanceB)
                if 0.25<ColorWeight < 0.5:
                    OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[False,True]
                elif 0.5 < ColorWeight < 0.75:
                    OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[True,False]
                elif 0.75 < ColorWeight:
                    OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[True,True]

for w in range(0, Img.width):
   for h in range(0, Img.height):
        BlockX = (int)(w / BlockSizeX)
        BlockY = (int)(h / BlockSizeY)
        PixelX=w-BlockX*BlockSizeX
        PixelY=h-BlockY*BlockSizeY
        if OutputArray[BlockX][BlockY][2][PixelX][PixelY]==[False,False]:
            Img.putpixel((w,h), tuple( OutputArray[BlockX][BlockY][0]))
        if OutputArray[BlockX][BlockY][2][PixelX][PixelY] == [False, True]:
            OutputColor=OutputArray[BlockX][BlockY][0]*0.75+OutputArray[BlockX][BlockY][1]*0.25
            Img.putpixel((w,h), tuple(  (int)(OutputColor[i]) for i in range(3)))
        if OutputArray[BlockX][BlockY][2][PixelX][PixelY] == [True, False]:
            OutputColor = OutputArray[BlockX][BlockY][0] * 0.5 + OutputArray[BlockX][BlockY][1] * 0.5
            Img.putpixel((w, h), tuple(  (int)(OutputColor[i]) for i in range(3)))
        if OutputArray[BlockX][BlockY][2][PixelX][PixelY] == [True, True]:
            Img.putpixel((w, h), tuple(OutputArray[BlockX][BlockY][1]))



Img.save("output.jpg")

f=open("D:\\1.b", 'br+')
f.write(bytes(OutputArray))









