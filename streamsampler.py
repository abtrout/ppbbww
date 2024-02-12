#!/usr/bin/env python3

import aiohttp
import asyncio
import datetime
import logging
import os
import random
import subprocess
import tempfile
import time


class StreamSampler:
    def __init__(self, cam_name, data_dir="./data"):
        self.base_url = f"https://cams.cdn-surfline.com/cdn-wc/wc-{cam_name}"
        self.cam_name = cam_name
        self.data_dir = data_dir

    async def get_recent_frames(self):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            chunk_url = await self.__get_recent_chunk_url(session)
            return self.__extract_frames(chunk_url)

    async def __get_recent_chunk_url(self, session):
        async with session.get(f"{self.base_url}/chunklist.m3u8") as res:
            chunklist = await res.text()
            chunk = next(l for l in chunklist.splitlines() if not l.startswith("#"))
            return f"{self.base_url}/{chunk}"

    def __extract_frames(self, chunk_url):
        dt = datetime.datetime.now()
        day, hour, ts = dt.strftime("%m%d%Y"), dt.strftime("%H"), dt.strftime("%s")
        frames_dir = f"{self.data_dir}/{self.cam_name}/{day}/{hour}"
        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir)
        subprocess.run(["ffmpeg",
            "-hide_banner", "-loglevel", "0",
            "-i", chunk_url,
            "-vf", "select=eq(pict_type\,I)",
            "-vsync", "vfr",
            f"{frames_dir}/{ts}-thumb-%04d.jpg"])

        return [f for f in os.scandir(frames_dir) if f.name.startswith(f"{ts}")]


async def sample_stream(cam_name):
    ss = StreamSampler(cam_name)
    while True:
        try:
            frames = await ss.get_recent_frames()
            logging.info(
                f"cam_name={cam_name} num_frames={len(frames)} Extracted frames"
            )
        except Exception as ex:
            logging.error(f"cam_name={cam_name} Failed to get_recent_frames: {ex}")
        delay = random.randint(5, 20)  # seconds.
        logging.info(f"cam_name={cam_name} delay={delay} Sleeping")
        await asyncio.sleep(delay)


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(sample_stream("mavericks"))
        tg.create_task(sample_stream("mavericksov"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    asyncio.run(main())
