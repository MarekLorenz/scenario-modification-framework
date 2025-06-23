import math
from PIL import Image
from PIL import ImageSequence

gif = Image.open("CHN_Qingdao-15_2_T-1.gif")

frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(gif)]

frame_width, frame_height = frames[0].size
columns = 5  # Or however many per row you want
rows = math.ceil(len(frames) / columns)

sprite_sheet = Image.new("RGBA", (frame_width * columns, frame_height * rows))

for index, frame in enumerate(frames):
    x = (index % columns) * frame_width
    y = (index // columns) * frame_height
    sprite_sheet.paste(frame, (x, y))
sprite_sheet.save("sprite_sheet.png")