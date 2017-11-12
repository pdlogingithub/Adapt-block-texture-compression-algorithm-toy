'''
This program demostrates the main ideal of "ASTC" algorithm
by yangxiangyun
2017.11.12
'''

import numpy
from PIL import Image,ImageFilter
import sys
import os
import time

# input image
Img = Image.open("input.png")
# blur the input image for deciding color pallette later,should use per block blur,but just to keep things simple.
ImgBlur=Img.filter(ImageFilter.BLUR)

print("Image format:",Img.format)
print("Image mode:",Img.mode)
print("Image size:",Img.size)
print("Preparing...")

# block size,can be any arbitary integar number,larger block size means smaller file size,
# when becomes too large,image quality will drops HARD.
BlockSizeX = 12
BlockSizeY = 12
# same as end points for ASTC,core feature of ASTC,I use fixed size of 2 just to keep things simple.
PalleteCapacity=2

# enable debug will cause program to crush if image is too large,because save file function sometime just throw error.
debug_showblock = False

# convert image to numpy array for more advanced control and performance
ImgArray = numpy.arange(Img.width * Img.height * 3, dtype=numpy.uint8).reshape(Img.width, Img.height, 3)
ImgArrayBlur= numpy.arange(Img.width * Img.height * 3, dtype=numpy.uint8).reshape(Img.width, Img.height, 3)

for w in range(0, Img.width):
    for h in range(0, Img.height):
        ImgArray[w][h] = Img.getpixel((w, h))
        ImgArrayBlur[w][h] = ImgBlur.getpixel((w, h))

# calculate block counts
BlockCountX = (int)(Img.width / BlockSizeX) if Img.width % BlockSizeX == 0 else (int)(Img.width / BlockSizeX) + 1
BlockCountY = (int)(Img.height / BlockSizeY) if Img.height % BlockSizeY == 0 else (int)(Img.height / BlockSizeY) + 1

# store the data after the compression,"two pellate colors plus block pixels' color weight" per block.
OutputArray=numpy.array([[[[0,0,0],[0,0,0],[[[False,False] for i in range(BlockSizeY)] for i in range(BlockSizeX)]] for i in range(BlockCountX)] for i in range(BlockCountX)])

StartTime=time.asctime(time.localtime(time.time()))

# starting compression.
# iterate all blocks.
for BlockX in range(0, BlockCountX):
    for BlockY in range(0, BlockCountY ):
        sys.stdout.write('\r'+"progress:{}/{} Blocks".format(BlockX*BlockCountY+BlockY,BlockCountX*BlockCountY))
        # declare the two pellate colors for this block,
        # assign a color to them in case this block is filled with only one color.
        ColorA = ColorB = ImgArrayBlur[BlockX * BlockSizeX][BlockY * BlockSizeY]
        # the ideal of the block is block consists similar color,
        # and can be represented by interpolation of two most different colors in it,
        # I use colorDistance to find most diferent two colors to keep things simple,
        # more advanced calculations can be done here.
        ColorDistance = 0.0
        ColorWeight = 0.0
        # compare every pixels in this block with each others to find most different color.
        for PixelX1 in range(0, BlockSizeX ):
            for PixelY1 in range(0, BlockSizeY):
                for PixelX2 in range(0, BlockSizeX):
                    for PixelY2 in range(0, BlockSizeY):
                        X1 = BlockX * BlockSizeX + PixelX1
                        Y1 = BlockY * BlockSizeY + PixelY1
                        X2 = BlockX * BlockSizeX + PixelX2
                        Y2 = BlockY * BlockSizeY + PixelY2
                        # if image's size can not divides block size,there will be block pixels outsides image,
                        # so skip it.
                        if X1 > Img.width-1 or Y1 > Img.height-1 or X2 > Img.width-1 or Y2 > Img.height-1:
                            continue
                        # use colors from blured image is to prevent situation
                        #  where two noise colors will be picked rather than most numbered colors in the block.
                        ColorOffset = [(int)(ImgArrayBlur[X1][Y1][i]) - (int)(ImgArrayBlur[X2][Y2][i]) for i in range(3)]
                        NewColorDistance = (ColorOffset[0] ** 2 + ColorOffset[1] ** 2 + ColorOffset[2] ** 2) ** 0.5
                        # if two pixels' different is greater than before,use these two color as pallete colors.
                        if ColorDistance < NewColorDistance:
                            ColorDistance = NewColorDistance
                            ColorA=ImgArrayBlur[X1][Y1]
                            ColorB=ImgArrayBlur[X2][Y2]
        # put pallete colors to output
        OutputArray[BlockX][BlockY][0] = ColorA
        OutputArray[BlockX][BlockY][1] = ColorB
        for PixelX in range(0, BlockSizeX ):
            for PixelY in range(0, BlockSizeY):
                X = BlockX * BlockSizeX + PixelX
                Y = BlockY * BlockSizeY + PixelY
                if X > Img.width - 1 or Y > Img.height - 1:
                    continue
                # each pixel has 2 bit weights,so it can be one of 4 colors in between two palletes colors.
                # calculate distance between the two pallette colors to decide weights.
                ColorOffsetA = [(int)(ImgArray[X][Y][i]) - (int)(ColorA[i]) for i in range(3)]
                ColorOffsetB = [(int)(ImgArray[X][Y][i]) - (int)(ColorB[i]) for i in range(3)]
                ColorDistanceA = (ColorOffsetA[0] ** 2 + ColorOffsetA[1] ** 2 + ColorOffsetA[2]**2) ** 0.5
                ColorDistanceB = (ColorOffsetB[0] ** 2 + ColorOffsetB[1] ** 2 + ColorOffsetB[2]**2) ** 0.5
                if ColorDistanceA+ColorDistanceB == 0:
                    ColorWeight=0
                else:
                    ColorWeight=ColorDistanceA/(ColorDistanceA+ColorDistanceB)
                if 0.0 <= ColorWeight < 1/6:
                    ColorWeight=0
                    OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[False,False]
                elif 1/6 <= ColorWeight < 3/6:
                    ColorWeight=1/3
                    OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[False,True]
                elif 3/6 <= ColorWeight < 5/6:
                    ColorWeight=2/3
                    OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[True,False]
                elif 5/6 <= ColorWeight <= 1:
                    ColorWeight=1
                    OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[True,True]
                # debug
                if debug_showblock:
                    # draw red line if its margin.
                    if PixelX == 0 or PixelX == BlockSizeX - 1 or PixelY == 0 or PixelY == BlockSizeY - 1:
                        UnPackColor = [255, 0, 0]
                    else:
                        UnPackColor = OutputArray[BlockX][BlockY][0] * (1.0 - ColorWeight) + OutputArray[BlockX][BlockY][1] * ColorWeight
                    Img.putpixel((X,Y), tuple((int)(UnPackColor[i]) for i in range(3)))
        # debug
        if debug_showblock:
            if os.access("debug_view.jpg", os.R_OK):
                Img.save("debug_view.jpg")
            for PixelX in range(0, BlockSizeX ):
                for PixelY in range(0, BlockSizeY):
                    X = BlockX * BlockSizeX + PixelX
                    Y = BlockY * BlockSizeY + PixelY
                    if X > Img.width - 1 or Y > Img.height - 1:
                        continue
                        # remove the red line.
                    if PixelX != 0 and PixelX != BlockSizeX - 1 and PixelY != 0 and PixelY != BlockSizeY - 1:
                        continue
                    ColorOffsetA = [(int)(ImgArray[X][Y][i]) - (int)(ColorA[i]) for i in range(3)]
                    ColorOffsetB = [(int)(ImgArray[X][Y][i]) - (int)(ColorB[i]) for i in range(3)]
                    ColorDistanceA = (ColorOffsetA[0] ** 2 + ColorOffsetA[1] ** 2 + ColorOffsetA[2]**2) ** 0.5
                    ColorDistanceB = (ColorOffsetB[0] ** 2 + ColorOffsetB[1] ** 2 + ColorOffsetB[2]**2) ** 0.5
                    if ColorDistanceA + ColorDistanceB == 0:
                        ColorWeight = 0
                    else:
                        ColorWeight = ColorDistanceA / (ColorDistanceA + ColorDistanceB)

                    if 0.0 <= ColorWeight < 1/6:
                        ColorWeight=0
                        OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[False,False]
                    elif 1/6 <= ColorWeight < 3/6:
                        ColorWeight=1/3
                        OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[False,True]
                    elif 3/6 <= ColorWeight < 5/6:
                        ColorWeight=2/3
                        OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[True,False]
                    elif 5/6 <= ColorWeight <= 1:
                        ColorWeight=1
                        OutputArray[BlockX][BlockY][2][PixelX][PixelY]=[True,True]
                    UnPackColor = OutputArray[BlockX][BlockY][0] * (1.0 - ColorWeight) + OutputArray[BlockX][BlockY][1] * ColorWeight
                    Img.putpixel((X, Y), tuple((int)(UnPackColor[i]) for i in range(3)))

# uncompress data to image
if not debug_showblock:
    for w in range(0, Img.width):
        for h in range(0, Img.height):
            BlockX = (int)(w / BlockSizeX)
            BlockY = (int)(h / BlockSizeY)
            PixelX=w-BlockX*BlockSizeX
            PixelY=h-BlockY*BlockSizeY
            if OutputArray[BlockX][BlockY][2][PixelX][PixelY]==[False,False]:
                Img.putpixel((w,h), tuple( OutputArray[BlockX][BlockY][0]))
            if OutputArray[BlockX][BlockY][2][PixelX][PixelY] == [False, True]:
                UnPackColor=OutputArray[BlockX][BlockY][0]*(2/3)+OutputArray[BlockX][BlockY][1]*(1/3)
                Img.putpixel((w,h), tuple((int)(UnPackColor[i]) for i in range(3)))
            if OutputArray[BlockX][BlockY][2][PixelX][PixelY] == [True, False]:
                UnPackColor = OutputArray[BlockX][BlockY][0] * (1/3) + OutputArray[BlockX][BlockY][1] * (2/3)
                Img.putpixel((w, h), tuple((int)(UnPackColor[i]) for i in range(3)))
            if OutputArray[BlockX][BlockY][2][PixelX][PixelY] == [True, True]:
                Img.putpixel((w, h), tuple(OutputArray[BlockX][BlockY][1]))

Img.save("output.png")
Img.save("output.jpg")

f=open("Output.binary", 'br+')
f.write(bytes(OutputArray))

EndTime=time.asctime(time.localtime(time.time()))

print(" ")
print("Complete")
print(" ")
print("Final raw size:",BlockCountX*BlockCountY*(BlockSizeX*BlockSizeY*2+24)/8/1024,"in KB")
print("Start time:",StartTime)
print("End time:",EndTime)
input("Press the <ENTER> key to exit...")









