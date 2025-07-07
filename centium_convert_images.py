import os
from PIL import Image

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}


def is_target_file(filename):
    name, ext = os.path.splitext(filename)
    if ext.lower() == '.png':
        return False
    if ext.lower() not in ALLOWED_EXTENSIONS:
        return False
    if len(name) == 2 and name.isdigit():
        return True
    return False

def crop_center_square(img):
    width, height = img.size
    if width == height:
        return img
    elif width > height:
        left = (width - height) // 2
        right = left + height
        return img.crop((left, 0, right, height))
    else:
        top = (height - width) // 2
        bottom = top + width
        return img.crop((0, top, width, bottom))

def convert_and_resize(filepath, outpath):
    with Image.open(filepath) as img:
        img = crop_center_square(img)
        img = img.resize((256, 256), Image.LANCZOS)
        img.save(outpath, 'PNG')
        print(f"Converted and resized: {filepath} -> {outpath}")

def main():
    for filename in os.listdir(IMG_DIR):
        if is_target_file(filename):
            name, _ = os.path.splitext(filename)
            src_path = os.path.join(IMG_DIR, filename)
            dst_path = os.path.join(IMG_DIR, f"{name}.png")
            convert_and_resize(src_path, dst_path)

if __name__ == "__main__":
    main()
