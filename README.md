_Pillar Point boats, birds, [~~and waves~~](https://github.com/abtrout/ppbbww/issues/8) watcher_.

[`ppbw`](/ppboatwatch/ppbw.py) is a Python project that samples frames from the [Mavericks](https://en.wikipedia.org/wiki/Mavericks,_California) Surfline cam and runs [facebook/detr-resnet-50](https://huggingface.co/facebook/detr-resnet-50) on them to detect various objects, e.g. boats and birds. Matches are archived in a SQLite database and announced to a shared Slack channel to be enjoyed with friends.

After running this for a while, _many neat images_ were captured, which lead to the creation of the gallery. There's a small [`curator`](/ppboatwatch/gallery.py#L77-L80) web app for hand picking gallery-worthy images from the matches database, and a script to [`generate`](/ppboatwatch/gallery.py#L83-L114) a static Jekyll site that's suitable to be deployed on my [`gh-pages`](https://github.com/abtrout/ppbbww/tree/gh-pages) branch. I curate by hand and manually push updates sometimes, ¯\\\_(ツ)_/¯.

__[Check out the gallery here!](https://abtrout.github.io/ppbbww)__

#### Getting started

```
$ apt install ffmpeg               # for web stream frame extraction
$ apt install nvidia-cuda-toolkit  # for Nvidia GPU support
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -e .
```

Check out the available [commands](pyproject.toml#L54-L59) as good places to start.
