_Pillar Point boats, birds, [~~and waves~~](https://github.com/abtrout/ppbbww/issues/8) watcher_.

[`ppbw`](/ppboatwatch/ppbw.py) is a Python project that samples frames from the [Mavericks](https://en.wikipedia.org/wiki/Mavericks,_California) Surfline cam and runs [facebook/detr-resnet-50](https://huggingface.co/facebook/detr-resnet-50) on them to detect various objects, e.g. boats and birds. Matches are archived in a SQLite database and announced to a shared Slack channel to be enjoyed with friends.

#### Getting started

```
$ apt install ffmpeg               # for web stream frame extraction
$ apt install nvidia-cuda-toolkit  # for Nvidia GPU support
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -e .
```

Check out the available [commands](pyproject.toml#L54-L59) as good places to start.
