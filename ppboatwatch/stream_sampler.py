import aiohttp
import asyncio
import datetime
import logging
import os
import random
import subprocess
import tempfile
import time

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Origin": "https://www.surfline.com",
    "Referer": "https://www.surfline.com/",
    "DNT": "1",
}


class StreamSampler:
    def __init__(self, cam_name, data_dir="./data"):
        self.base_url = f"https://cams.cdn-surfline.com/cdn-wc/wc-{cam_name}"
        self.cam_name = cam_name
        self.data_dir = data_dir

    async def get_recent_frames(self):
        async with aiohttp.ClientSession(
            raise_for_status=True,
            skip_auto_headers=list(DEFAULT_HEADERS.keys()),
            headers=DEFAULT_HEADERS,
        ) as session:
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
        # Return filenames of (ffmpeg generated) frames to caller.
        return [f for f in os.scandir(frames_dir) if f.name.startswith(f"{ts}-thumb")]
