import argparse
import logging
import os

from PIL import Image, ImageDraw
from .boat_finder import BoatFinder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    parser.add_argument("-t", "--thresh", type=float, default=0.9)
    parser.add_argument("-l", "--labels", type=str, nargs="+", action="extend")
    parser.add_argument(
        "-o",
        "--outdir",
        type=str,
        help="Save annotated matches to given folder, if set.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARN,
        format="%(asctime)s %(message)s",
    )

    bf = BoatFinder(thresh=args.thresh, labels=args.labels)
    for base, _, fs in os.walk(args.filepath):
        for f in fs:
            img_file = f"{base}/{f}"
            image = Image.open(img_file)
            matches = list(bf.find(image))
            if len(matches) == 0:
                logging.info(f"No matches in {img_file}.")
                continue

            logging.warn(f"Found {len(matches)} in {img_file}.")
            draw = ImageDraw.Draw(image)
            for label, score, box in matches:
                logging.warn(f" >> {label} ({score})")
                if args.outdir:
                    # TODO: Add label text. Align top/left.
                    draw.rectangle(list(box), outline="#a6e22e", width=2)

            if args.outdir:
                out_file = f.removesuffix(".jpg") + "_matches.jpg"
                image.save(f"{args.outdir}/{out_file}")
