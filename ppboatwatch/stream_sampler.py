import aiohttp
import asyncio
import datetime
import logging
import os
import random
import subprocess
import time

from tempfile import mkstemp

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Origin": "https://www.surfline.com",
    "DNT": "1",
    "Referer": "https://www.surfline.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "TE": "trailers",
}


class StreamSampler:
    def __init__(self, cam_name, data_dir="./data"):
        self.base_url = f"https://hls.cdn-surfline.com/oregon/wc-{cam_name}"
        self.cam_name = cam_name
        self.data_dir = data_dir

    async def get_recent_frames(self):
        async with aiohttp.ClientSession(
            raise_for_status=True,
            skip_auto_headers=list(DEFAULT_HEADERS.keys()),
            headers=DEFAULT_HEADERS,
        ) as session:
            chunk_url = await self.__get_recent_chunk_url(session)
            chunk_file = await self.__get_recent_chunk(session, chunk_url)
            return self.__extract_frames(chunk_file)

    async def __get_recent_chunk_url(self, session):
        url = f"{self.base_url}/playlist.m3u8"
        async with session.get(url) as res:
            chunklist = await res.text()
            chunk = next(l for l in chunklist.splitlines() if not l.startswith("#"))
            return f"{self.base_url}/{chunk}"

    async def __get_recent_chunk(self, session, chunk_url):
        async with session.get(chunk_url) as res:
            bytes = await res.read()
            fd, chunk_file = mkstemp()
            with os.fdopen(fd, "wb") as f:
                f.write(bytes)
            return chunk_file

    def __extract_frames(self, chunk_file):
        dt = datetime.datetime.now()
        day, hour, ts = dt.strftime("%m%d%Y"), dt.strftime("%H"), dt.strftime("%s")
        frames_dir = f"{self.data_dir}/{self.cam_name}/{day}/{hour}"
        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir)
        subprocess.run(["ffmpeg",
            "-hide_banner", "-loglevel", "3",
            "-i", chunk_file,
            "-vf", "select=eq(pict_type\,I)",
            "-vsync", "vfr",
            f"{frames_dir}/{ts}-thumb-%04d.jpg"])
        os.remove(chunk_file)  # cleanup
        # Return filenames of (ffmpeg generated) frames to caller.
        return [f for f in os.scandir(frames_dir) if f.name.startswith(f"{ts}-thumb")]
