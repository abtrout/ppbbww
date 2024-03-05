import argparse
import asyncio
import logging
import random
import tempfile
import os

from slack_sdk.web.async_client import AsyncWebClient
from PIL import Image, ImageDraw, ImageFont

from .archive import Archive
from .stream_sampler import StreamSampler
from .object_detector import ObjectDetector


async def sample_stream(frames_q, sampler):
    while True:
        try:
            frames = await sampler.get_recent_frames()
            logging.warning(f"[sample_stream]: Extracted {len(frames)} recent frames")
            assert len(frames) > 0
            await frames_q.put(frames[0].path)
            for frame in frames[1:]:  # we only keep 1 frame!
                os.remove(frame)
        except Exception as ex:
            logging.error(f"[sample_stream]: Failed to get_recent_frames: {ex}")

        delay = random.randint(3, 10)  # seconds!
        logging.warning(f"[sample_stream]: Sleeping {delay} seconds")
        await asyncio.sleep(delay)


async def find_matches(frames_q, archive_q, announce_q):
    detector = ObjectDetector(thresh=0.80)
    font = ImageFont.truetype("roboto-regular.ttf", 15)
    while True:
        # Get filenames from the queue and run object detector.
        frame_file = await frames_q.get()
        image = Image.open(frame_file)
        matches = list(filter_matches(detector.find(image)))
        if len(matches) == 0:
            os.remove(frame_file)
            logging.warning(f"[find_matches]: No matches; cleaned up")
            continue
        # Archive the frame and matches.
        await archive_q.put((frame_file, matches))
        # Draw bounding boxes and send to Slack.
        draw = ImageDraw.Draw(image)
        for label, score, box in matches:
            draw.text((box[0], box[1] - 15), label, (255, 255, 255), font=font)
            draw.rectangle(box, outline=(255, 255, 255), width=1)
        out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        image.save(out_file.name)
        await announce_q.put(out_file.name)


def filter_matches(matches):
    for label, score, box in matches:
        box = list(box)
        # Skip matches at the bottom of the image area (rocks).
        if box[1] > 600:
            continue
        # Skip common but uninteresting cases based on size and label.
        box_size = (box[2] - box[0]) * (box[3] - box[1])
        if box_size < 500:
            logging.debug(f"Skipping small box (box_size={box_size})")
            continue
        if label == "boat" and box_size < 3000:
            logging.debug(f"Skipping small boat (box_size={box_size})")
            continue
        if label == "bird" and box_size < 1000:
            logging.debug(f"Skipping small bird (box_size={box_size})")
            continue
        # Return everything else.
        yield (label, score, box)


async def archive_matches(archive_q, archive):
    while True:
        file, matches = await archive_q.get()
        logging.warning(f"[archive_matches] Archiving {file}: {matches}")
        ts = file.split("/")[-1].split("-")[0]
        for label, score, box in matches:
            archive.add_match(ts=ts, filename=file, label=label, score=score, box=box)


async def announce_matches(announce_q, client):
    while True:
        matches_path = await announce_q.get()
        logging.warning(f"[annouce_matches] Posting match {matches_path}")
        await post_match(client, matches_path)


async def post_match(client, frame_file):
    with open(frame_file, "rb") as f:
        res = await client.files_upload_v2(file=f, channel="C06LMBRNV8U")
    if not res["ok"]:
        logging.error(f"Failed to post_match: {res}")


async def main_task(args):
    archive = Archive(args.db_file)
    client = AsyncWebClient(token=os.environ["SLACK_API_TOKEN"])
    sampler = StreamSampler("mavericksov", args.data_dir)

    frames_q = asyncio.Queue()    # frames that should be inspected.
    archive_q = asyncio.Queue()   # matches that should be archived.
    announce_q = asyncio.Queue()  # matches that should be announced in Slack.

    async with asyncio.TaskGroup() as tg:
        tg.create_task(sample_stream(frames_q, sampler))
        tg.create_task(find_matches(frames_q, archive_q, announce_q))
        tg.create_task(archive_matches(archive_q, archive))
        tg.create_task(announce_matches(announce_q, client))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data-dir", default="./data", type=str)
    parser.add_argument("-f", "--db-file", default="./archive.db", type=str)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.WARN
    logging.basicConfig(level=level, format="%(asctime)s %(message)s")

    asyncio.run(main_task(args))
