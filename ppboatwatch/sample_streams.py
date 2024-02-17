import asyncio
import logging
import random

from .stream_sampler import StreamSampler


async def sample_stream(cam_name, data_dir):
    ss = StreamSampler(cam_name, data_dir)
    while True:
        try:
            frames = await ss.get_recent_frames()
            logging.info(f"cam_name={cam_name} num_frames={len(frames)} Extracted frames")
        except Exception as ex:
            logging.error(f"cam_name={cam_name} Failed to get_recent_frames: {ex}")
        # TODO: Decrease delay but only keep 1 frame?
        delay = random.randint(5, 20)  # seconds!
        logging.info(f"cam_name={cam_name} delay={delay} Sleeping")
        await asyncio.sleep(delay)


async def main_task(cams, data_dir):
    async with asyncio.TaskGroup() as tg:
        for cam in cams:
            tg.create_task(sample_stream(cam, data_dir))


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    cams = ["mavericks", "mavericksov"]  # TODO: argparse.
    data_dir = "./data"                  # TODO: argparse
    asyncio.run(main_task(cams, data_dir))
