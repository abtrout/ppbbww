import argparse
import asyncio
import logging
import random
import tempfile
import os

from slack_sdk.web.async_client import AsyncWebClient
from PIL import Image, ImageDraw, ImageFont

from .stream_sampler import StreamSampler
from .object_detector import ObjectDetector


async def sample_stream(frames_q, tmp_dir):
    ss = StreamSampler("mavericksov", tmp_dir)
    while True:
        try:
            frames = await ss.get_recent_frames()
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


async def find_matches(frames_q, matches_q):
    detector = ObjectDetector(thresh=0.80)
    while True:
        # Get filenames from the queue and run object detector.
        frame_file = await frames_q.get()
        image = Image.open(frame_file)
        matches = list(filter_matches(detector.find(image)))
        if len(matches) == 0:
            os.remove(frame_file)
            logging.warning(f"[find_matches]: No matches; cleaned up")
            continue
        # Draw bounding boxes and labels for all matches.
        ImageFont.load_default(size=13)
        draw = ImageDraw.Draw(image)
        for label, score, box in matches:
            #draw.text((box[0], box[1]-20), f"{label} {score}", fill="#ffffff", font_size=13)
            draw.rectangle(box, outline="#ffffff", width=2)
        # Save file and put in queue; post_matches job will handle cleanup.
        out_file = frame_file.removesuffix(".jpg") + "_matches.jpg"
        image.save(out_file)
        await matches_q.put(out_file)


def filter_matches(matches):
    for label, score, box in matches:
        box = list(box)
        # Skip matches at the bottom of the image area (rocks).
        if box[1] > 640:
            continue
        # Skip common but uninteresting cases based on size and label.
        box_size = (box[2] - box[0]) * (box[3] - box[1])
        if box_size < 500:
            logging.debug(f"Skipping small box (box_size={box_size})")
            continue
        if label == "boat" and box_size < 1500:
            logging.debug(f"Skipping small boat (box_size={box_size})")
            continue
        if label == "bird" and box_size < 1000:
            logging.debug(f"Skipping small bird (box_size={box_size})")
            continue
        # Return everything else.
        yield (label, score, box)


async def post_matches(matches_q, client):
    while True:
        matches_path = await matches_q.get()
        await post_match(client, matches_path)


async def post_match(client, frame_file):
    with open(frame_file, "rb") as f:
        res = await client.files_upload_v2(file=f, channel="C06LMBRNV8U")
    if not res["ok"]:
        logging.error(f"Failed to post_match: {res}")


async def main_task():
    client = AsyncWebClient(token=os.environ["SLACK_API_TOKEN"])
    frames_q, matches_q = asyncio.Queue(), asyncio.Queue()
    tmp_dir = tempfile.TemporaryDirectory(dir=".")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(sample_stream(frames_q, tmp_dir.name))
        tg.create_task(find_matches(frames_q, matches_q))
        tg.create_task(post_matches(matches_q, client))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.WARN
    logging.basicConfig(level=level, format="%(asctime)s %(message)s")

    asyncio.run(main_task())
