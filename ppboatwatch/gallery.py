import aiohttp_jinja2
import jinja2
import os
import shutil
import sys

from aiohttp import web
from datetime import datetime
from itertools import groupby

from .archive import Archive


class Curator:
    def __init__(self, db_file):
        self.archive = Archive(db_file)
        self.app = web.Application()
        self.app.add_routes(
            [
                web.get("/", self.redirect_latest),
                web.get("/gallery/{ts}", self.display_match),
                web.put("/gallery/{ts}", self.set_gallery),
                web.delete("/gallery/{ts}", self.unset_gallery),
                web.static("/data", "./data"),
            ]
        )
        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader("./ppboatwatch/"))

    def run(self):
        web.run_app(self.app)

    async def redirect_latest(self, request):
        ts, _, _, _, _, _, _, _, _ = self.archive.list_matches()[0]
        raise web.HTTPFound(f"/gallery/{ts}")

    async def display_match(self, request):
        ts = int(request.match_info["ts"])
        (ts, filename, label, score, x0, y0, x1, y1, gallery, previous_ts, next_ts) = (
            self.archive.get_match_page(ts)
        )
        dt = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %I:%M:%S")
        context = {
            "date_time": dt,
            "prev_ts": previous_ts,
            "ts": ts,
            "next_ts": next_ts,
            "filename": filename,
            "label": label,
            "score": score,
            "x0": x0,
            "y0": y0,
            "x1": x1,
            "y1": y1,
            "gallery": True if gallery else False,
        }
        return aiohttp_jinja2.render_template("gallery.html", request, context)

    async def set_gallery(self, request):
        ts = request.match_info["ts"]
        try:
            self.archive.set_gallery(int(ts))
            return web.Response(status=200)
        except Exception as ex:
            logging.error(f"Failed to set_gallery: {ex}")
            return web.Response(status=500)

    async def unset_gallery(self, request):
        ts = request.match_info["ts"]
        try:
            self.archive.unset_gallery(int(ts))
            return web.Response(status=200)
        except Exception as ex:
            logging.error(f"Failed to set_gallery: {ex}")
            return web.Response(status=500)


# Entry point for gallery curation web UI.
def curate():
    curator = Curator("archive.db")
    curator.run()


# Entry point for static gallery generation; produces _layouts and
# assets/img folders for jekyll gh-pages site, based on the `gallery`
# column in an Archive.
def generate():
    if not os.path.exists("gallery"):
        os.makedirs("gallery")
    if not os.path.exists("_posts"):
        os.makedirs("_posts")

    rows = Archive("archive.db").list_gallery_matches()
    all_matches = list(groupby(rows, key=lambda cols: (cols[0], cols[1])))
    for i, ((ts, f), matches) in enumerate(all_matches):
        # Copy frame file to gallery.
        shutil.copyfile(f, f"gallery/{ts}.jpg")
        # Make a new post.
        ymd = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d")
        with open(f"_posts/{ymd}-{ts}.md", "w") as post_file:
            dt = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %I:%M:%S")
            # TODO: Could add lag/lead to LIST_GALLERY_MATCHES_SQL query instead.
            next_ts = all_matches[i - 1][0][0] if i > 0 else None
            prev_ts = all_matches[i + 1][0][0] if i < len(all_matches) - 1 else None
            post_file.writelines(
                [
                    "---\n",
                    "layout: default\n",
                    f"ts: {ts}\n",
                    f"prev_ts: {prev_ts}\n" if prev_ts else "",
                    f"next_ts: {next_ts}\n" if next_ts else "",
                    f'date_time: "{dt}"\n',
                    "---\n",
                ]
            )
