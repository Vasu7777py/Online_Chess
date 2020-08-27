
from PIL import Image

White = Image.open("default/WhiteCell.png")
Black = Image.open("default/BlackCell.png")

Board = Image.new("RGB", (512, 512))

# White.show()
# Black.show()

PresentColor = 1
PresentCordRow = 0
PresentCordCol = 0

# Board.show()

for col in range(8):
    for row in range(8):
        if (PresentColor == 1):
            # print("White", (PresentCordRow, PresentCordCol, PresentColor))
            Board.paste(White, (PresentCordRow, PresentCordCol))
            PresentColor = 0
        else:
            # print("Black", (PresentCordRow, PresentCordCol, PresentColor))
            Board.paste(Black, (PresentCordRow, PresentCordCol))
            PresentColor = 1
        PresentCordRow += 64
    if PresentColor == 1:
        PresentColor = 0
    else:
        PresentColor = 1
    PresentCordRow = 0
    PresentCordCol += 64

# Board.show()
Board.save("default/Board.png")
