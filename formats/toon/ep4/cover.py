"""Couverture de l'épisode 4 (le plan le plus spectaculaire + 3 à 5 mots) : python3 cover.py ASSETS OUT/cover.jpg"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = '/home/claude/studio/assets/fonts/Montserrat-Black.ttf'
im = Image.open(sys.argv[1] + '/I1.png').convert('RGB').resize((1080, 1920), Image.LANCZOS)
ov = Image.new('RGBA', (1080, 1920)); d = ImageDraw.Draw(ov)
for y in range(1150, 1920): d.line([(0, y), (1080, y)], fill=(5, 4, 12, int(230 * ((y - 1150) / 770) ** 1.1)))
im = Image.alpha_composite(im.convert('RGBA'), ov); g = Image.new('RGBA', (1080, 1920)); gd = ImageDraw.Draw(g); items = []
for y, s, sz, col, glow in ((1420, 'UNE SEULE ATTAQUE', 92, (255, 255, 255), (255, 42, 42)), (1540, 'A SUFFI ?!', 120, (255, 224, 102), (255, 170, 0)), (1680, 'FROMAGISTAN', 64, (255, 224, 102), (122, 63, 209))):
    f = ImageFont.truetype(F, sz); gd.text((540, y), s, font=f, fill=glow + (255,), anchor='mm', stroke_width=10, stroke_fill=glow + (255,)); items.append((y, s, f, col))
g = g.filter(ImageFilter.GaussianBlur(14)); im = Image.alpha_composite(im, g); d = ImageDraw.Draw(im)
for y, s, f, col in items: d.text((540, y), s, font=f, fill=col, anchor='mm', stroke_width=5, stroke_fill=(20, 10, 40))
im.convert('RGB').save(sys.argv[2], quality=92)
