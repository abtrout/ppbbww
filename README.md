# `pp-boatwatch` 

Locate large boats (e.g. container ships) as they pass by Pillar Point. 

---

Install the requirements.

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

Accumulate data by sampling the Mavericks cams on Surfline.

```
$ ./scrape.py
2024-02-10 10:19:32,612 cam_name=mavericksov Extracted keyframes from chunk
2024-02-10 10:19:32,612 cam_name=mavericksov delay=52 Sleeping
2024-02-10 10:19:33,157 cam_name=mavericks Extracted keyframes from chunk
2024-02-10 10:19:33,157 cam_name=mavericks delay=77 Sleeping
...
```

Find boats in images with [`BoatFinder`](./detect.py#L12).

```
$ ./detect.py $(find ./data/mavericks/02102024/10/*.jpg | head -n10)
2024-02-10 10:40:43,803 BoatFinder initializing ...
2024-02-10 10:40:44,473 BoatFinder initialized! took 0.6702592820074642 seconds
2024-02-10 10:40:44,477 Searching file ./data/mavericks/02102024/10/1707589172-thumb-0001.jpg...
2024-02-10 10:40:46,057 Searching file ./data/mavericks/02102024/10/1707589172-thumb-0002.jpg...
2024-02-10 10:40:47,474 Searching file ./data/mavericks/02102024/10/1707589172-thumb-0003.jpg...
2024-02-10 10:40:48,865 Searching file ./data/mavericks/02102024/10/1707589172-thumb-0004.jpg...
2024-02-10 10:40:50,264 Searching file ./data/mavericks/02102024/10/1707589172-thumb-0005.jpg...
2024-02-10 10:40:51,669 Searching file ./data/mavericks/02102024/10/1707589250-thumb-0001.jpg...
2024-02-10 10:40:53,074 >> label=boat    score=0.677     box=[431.265, 673.42, 694.994, 719.792]
2024-02-10 10:40:53,076 Searching file ./data/mavericks/02102024/10/1707589250-thumb-0002.jpg...
2024-02-10 10:40:54,760 Searching file ./data/mavericks/02102024/10/1707589250-thumb-0003.jpg...
2024-02-10 10:40:56,160 Searching file ./data/mavericks/02102024/10/1707589250-thumb-0004.jpg...
2024-02-10 10:40:57,594 Searching file ./data/mavericks/02102024/10/1707589250-thumb-0005.jpg...
```
