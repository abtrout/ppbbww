import argparse
import logging
import os

from PIL import Image, ImageDraw

from .archive import Archive
from .object_detector import ObjectDetector
from .ppbw import filter_matches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    parser.add_argument("-t", "--thresh", type=float, default=0.9)
    parser.add_argument("-l", "--labels", type=str, nargs="+", action="extend")
    parser.add_argument("-f", "--db-file", default="./archive.db", type=str)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    level = logging.INFO if args.verbose else logging.WARN
    logging.basicConfig(level=level, format="%(asctime)s %(message)s")

    archive = Archive(args.db_file)
    detector = ObjectDetector(thresh=args.thresh, labels=args.labels)
    for base, _, fs in os.walk(args.filepath):
        for f in fs:
            detect_and_save(f"{base}/{f}", detector, archive)


def detect_and_save(img_file, detector, archive):
    image = Image.open(img_file)
    matches = list(filter_matches(detector.find(image)))
    if len(matches) == 0:
        logging.info(f"No matches in {img_file}.")
        return

    logging.warn(f"Found {len(matches)} in {img_file}.")
    for label, score, box in matches:
        logging.warn(f" >> {label} ({score})")
        box = list(box)
        ts = img_file.split("/")[-1].split("-")[0]
        archive.add_match(ts=ts, filename=img_file, label=label, score=score, box=box)
