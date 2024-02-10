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


async def get_recent_chunk_url(session, cam_name):
    base_url = f"https://cams.cdn-surfline.com/cdn-wc/wc-{cam_name}"
    async with session.get(f"{base_url}/chunklist.m3u8") as res:
        chunklist = await res.text()
        chunk = next(filter(lambda x: not x.startswith('#'), chunklist.splitlines()))
        return f"{base_url}/{chunk}"


def split_keyframes(chunk_url, data_dir, cam_name):
    dt = datetime.datetime.now()
    day, hour, ts = dt.strftime("%m%d%Y"), dt.strftime("%H"), dt.strftime("%s")

    keyframes_dir = f"{data_dir}/{cam_name}/{day}/{hour}"
    if not os.path.exists(keyframes_dir):
        os.makedirs(keyframes_dir)

    subprocess.run(["ffmpeg",
        "-hide_banner", "-loglevel", "0",
        "-i", chunk_url,
        "-vf", "select=eq(pict_type\,I)",
        "-vsync", "vfr",
        f"{keyframes_dir}/{ts}-thumb-%04d.jpg"])


async def save_keyframes_from_chunk(cam_name, data_dir):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        chunk_url = await get_recent_chunk_url(session, cam_name)
        split_keyframes(chunk_url, data_dir, cam_name)
        logging.info(f"cam_name={cam_name} Extracted keyframes from chunk")


async def sample_stream(cam_name, data_dir):
    while True:
        try:
            await save_keyframes_from_chunk(cam_name, data_dir)
        except Exception as ex:
            logging.error(f"cam_name={cam_name} Failed to extract keyframes from chunk: {ex}")

        delay = random.randint(30, 90)  # seconds.
        logging.info(f"cam_name={cam_name} delay={delay} Sleeping")
        await asyncio.sleep(delay)


async def main():
    data_dir = os.environ.get("DATA_DIR", "./data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    async with asyncio.TaskGroup() as tg:
        tg.create_task(sample_stream("mavericks", data_dir))
        tg.create_task(sample_stream("mavericksov", data_dir))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    asyncio.run(main())
