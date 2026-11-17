"""Couverture de l'épisode 3 : python3 cover.py ASSETS OUT/cover.jpg"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = '/home/claude/studio/assets/fonts/Montserrat-Black.ttf'
im = Image.open(sys.argv[1] + '/J4.png').convert('RGB').resize((1080, 1920), Image.LANCZOS)
ov = Image.new('RGBA', (1080, 1920)); d = ImageDraw.Draw(ov)
for y in range(0, 900): d.line([(0, y), (1080, y)], fill=(5, 4, 12, int(215 * (1 - y / 900) ** 1.2)))
im = Image.alpha_composite(im.convert('RGBA'), ov); g = Image.new('RGBA', (1080, 1920)); gd = ImageDraw.Draw(g); items = []
for y, s, sz, col, glow in ((330, 'FROMAGISTAN', 128, (255, 224, 102), (255, 170, 0)), (470, 'ÉPISODE 3', 84, (255, 255, 255), (122, 63, 209)), (600, 'LE VOLEUR EST', 70, (255, 255, 255), (122, 63, 209)), (685, 'DANS LE CHÂTEAU ?', 70, (255, 255, 255), (122, 63, 209))):
    f = ImageFont.truetype(F, sz); gd.text((540, y), s, font=f, fill=glow + (255,), anchor='mm', stroke_width=10, stroke_fill=glow + (255,)); items.append((y, s, f, col))
g = g.filter(ImageFilter.GaussianBlur(14)); im = Image.alpha_composite(im, g); d = ImageDraw.Draw(im)
for y, s, f, col in items: d.text((540, y), s, font=f, fill=col, anchor='mm', stroke_width=4, stroke_fill=(20, 10, 40))
im.convert('RGB').save(sys.argv[2], quality=92)
