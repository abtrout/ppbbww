import argparse
import logging
import os

from PIL import Image, ImageDraw
from .object_detector import ObjectDetector


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

    level = logging.INFO if args.verbose else logging.WARN
    logging.basicConfig(level=level, format="%(asctime)s %(message)s")

    detector = ObjectDetector(thresh=args.thresh, labels=args.labels)
    for base, _, fs in os.walk(args.filepath):
        for f in fs:
            detect_and_save(f"{base}/{f}", detector, args.outdir)


def detect_and_save(img_file, detector, outdir):
    image = Image.open(img_file)
    matches = list(detector.find(image))
    if len(matches) == 0:
        logging.info(f"No matches in {img_file}.")
        return

    logging.warn(f"Found {len(matches)} in {img_file}.")
    draw = ImageDraw.Draw(image)
    for label, score, box in matches:
        logging.warn(f" >> {label} ({score})")
        if outdir:
            box = list(box)
            draw.text((box[0], box[1] - 15), label, (166, 226, 46))
            draw.rectangle(box, outline="#a6e22e", width=2)

    if outdir:
        out_file = img_file.split("/")[-1].removesuffix(".jpg") + "_matches.jpg"
        image.save(f"{outdir}/{out_file}")
