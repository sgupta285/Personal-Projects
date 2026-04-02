from pathlib import Path
from PIL import Image, ImageDraw

root = Path('samples/images')
root.mkdir(parents=True, exist_ok=True)

samples = [
    ('invoice.png', 'Invoice 1042\nTotal: $912.44'),
    ('id_card.png', 'Employee Badge\nID 99817'),
    ('lab_report.png', 'Lab Report\nObservation: stable'),
]

for filename, text in samples:
    image = Image.new('RGB', (1280, 720), color=(245, 245, 245))
    draw = ImageDraw.Draw(image)
    draw.rectangle((80, 80, 1200, 640), outline=(40, 40, 40), width=4)
    draw.text((120, 120), text, fill=(20, 20, 20))
    image.save(root / filename)

print(f'Wrote {len(samples)} sample images to {root}')
