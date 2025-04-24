from PIL import Image
from pathlib import Path
from typing import Optional
from zipfile import ZipFile
from datetime import datetime
from shutil import copy, rmtree

from constants import *

TRAY_SIZE = 96
STICKER_SIZE = 512
TRAY_IMAGE_FORMAT = 'png'
STICKER_IMAGE_FORMAT = 'webp'

UPLOAD_DIR = Path(UPLOAD_DIR_NAME)
TEMP_OUTPUT_DIR = Path('output')
PACKS_DIR = Path('packs')

# ADD_TRAY_TO_PACK = True


def is_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (AttributeError, FileNotFoundError, OSError, SyntaxError):
        return False


def handle_txt_file(txt_file_name: str, input_name: str, default_name: str) -> str:
    output_txt_file_path = TEMP_OUTPUT_DIR / txt_file_name
    output_txt_file_path.touch()
    output_txt_file_path.write_text(input_name or default_name)
    txt_value = output_txt_file_path.read_text(encoding='utf8')
    print(f'{output_txt_file_path.name} is being used with value of "{txt_value}"')
    return txt_value


def verify_title_and_author(title_name: str, author_name: str) -> str:
    title = handle_txt_file('title.txt', title_name,
                            f'nezorf`s script {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
    handle_txt_file('author.txt', author_name, 'nezorf')
    return title


def check_for_tray_image() -> Optional[Path]:
    result = tray_image_path = next(UPLOAD_DIR.rglob('tray.*'), None)
    if tray_image_path is None or not is_image(tray_image_path):
        print(f'tray image not found, using an image from the pack')
        tray_image_path = next((item for item in UPLOAD_DIR.iterdir() if is_image(item)), None)

    new_name = TEMP_OUTPUT_DIR / f'tray.{TRAY_IMAGE_FORMAT}'
    resize_image(tray_image_path, new_name, TRAY_SIZE, TRAY_SIZE, TRAY_IMAGE_FORMAT)
    return result


def resize_image(image_input_path: Path, image_output_path: Path, new_width: int, new_height: int, file_format: str):
    with Image.open(image_input_path) as img:
        img = img.resize((new_width, new_height), Image.LANCZOS)
        img.save(image_output_path, file_format)


def reformat_stickers(tray_path: Optional[Path], include_tray: bool):
    for i, item in enumerate(UPLOAD_DIR.iterdir()):
        if not is_image(item):
            continue
        if item == tray_path and not include_tray:
            continue
        new_name = TEMP_OUTPUT_DIR / f'sticker_{i}.{STICKER_IMAGE_FORMAT}'
        resize_image(item, new_name, STICKER_SIZE, STICKER_SIZE, STICKER_IMAGE_FORMAT)
        print(new_name)
        if i == MAX_FILE_COUNT:
            print('maximum number of images reached!')
            break


def zip_and_format_pack(pack_name: str = None):
    Path.mkdir(PACKS_DIR, exist_ok=True)
    zip_file_path = PACKS_DIR / f'{pack_name}.zip'
    with ZipFile(zip_file_path, 'w') as zip_file:
        for file in TEMP_OUTPUT_DIR.iterdir():
            file_path = Path(file)
            zip_file.write(file_path, file_path.name)

    wastickers_file_type = zip_file_path.with_suffix('.wastickers')
    zip_file_path.rename(wastickers_file_type)
    print('Done! your sticker pack is at', zip_file_path)
    rmtree(TEMP_OUTPUT_DIR)


def make_sticker_pack(title_name: str, author_name: str, include_tray: bool):
    Path.mkdir(TEMP_OUTPUT_DIR, exist_ok=True)
    pack_title = verify_title_and_author(title_name, author_name)
    tray_path = check_for_tray_image()
    reformat_stickers(tray_path, include_tray)
    zip_and_format_pack(pack_title)
