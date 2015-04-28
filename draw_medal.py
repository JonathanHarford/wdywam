import time

from wand.drawing import Drawing
from wand.image import Image
from wand.display import display
from wand.color import Color
from wand.font import Font

UNAME_Y = 320
TEXT_SIZE = 35
TEXT_Y = 440
TEXT_WRAP_AT = 24
YEAR_SIZE = 60
YEAR_Y = 680

font_stamp = Image()

def draw_medal(uname, text):

    def draw_text(color, offset):
        draw.fill_color = color
        draw.font_size = 700/(len(uname)+1)
        draw.text(im.width // 2 + offset[0], UNAME_Y + offset[1], '@'+uname)

        draw.font_size = TEXT_SIZE
        draw.text_interline_spacing = -4
        draw.text(im.width // 2 + offset[0], TEXT_Y + offset[1], text)

        draw.font_size = YEAR_SIZE
        draw.text(im.width // 2 + offset[0], YEAR_Y + offset[1], time.strftime('%Y'))

    # Inserting linebreaks!
    last_linebreak = last_space = 0
    text = list(text.upper())  # Let's get mutable!
    for i in range(len(text)):
        if text[i] == ' ':
            last_space = i
        if i - last_linebreak > TEXT_WRAP_AT:
            text[last_space] = '\n'
            last_linebreak = last_space
    text = ''.join(text)

    with Image(filename='medal.jpeg') as im:
        with Drawing() as draw:
            # draw.font = "DejaVu-Sans-Mono-Bold"
            draw.text_alignment = 'center'
            draw.text_antialias = True
            draw_text(Color('#730'), (1, 3))
            draw_text(Color('#eda'), (-1 ,-3))
            draw_text(Color('#da2'), (0, 0))




            draw(im)
            filename=time.strftime('%Y%m%d-%H%M%S' + uname) + '.jpg'
            im.save(filename=filename)
            # display(im)
    return filename