import logging
import os

from PIL import Image, ImageDraw
from .boat_finder import BoatFinder


def main():
    logging.basicConfig(level=logging.WARN, format="%(asctime)s %(message)s")
    bf = BoatFinder()
    find_dir = "./data"  # TODO: argparse.
    for base, _, fs in os.walk(find_dir):
        for f in fs:
            # TODO: Ignore _boats.jpg files!
            img_file = f"{base}/{f}"
            image = Image.open(img_file)
            res = list(bf.find(image))
            if len(res) > 0:
                draw = ImageDraw.Draw(image)
                for score, label, box in res: 
                    draw.rectangle(box, outline="#ff0000")
                out_file = img_file.removesuffix(".jpg") + "_boats.jpg"
                image.save(out_file)
                logging.warning(f"Found {len(res)} matches in {img_file}")
            else:
                logging.warning(f"No matches in {img_file}")
