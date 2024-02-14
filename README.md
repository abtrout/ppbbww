# `pp-boatwatch` 

Locate large boats as they pass by Pillar Point. 

![](https://i.imgur.com/uSNPctj.jpeg)

Install the requirements.

```
$ sudo apt install ffmpeg               # for extracing keyframes
$ sudo apt install nvidia-cuda-toolkit  # for GPU support
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

Accumulate data by sampling the Mavericks cams on Surfline.

```
$ ./streamsampler.py
2024-02-11 20:36:15,997 cam_name=mavericksov num_frames=4 Extracted frames
2024-02-11 20:36:15,998 cam_name=mavericksov delay=12 Sleeping
2024-02-11 20:36:16,583 cam_name=mavericks num_frames=5 Extracted frames
2024-02-11 20:36:16,583 cam_name=mavericks delay=11 Sleeping
2024-02-11 20:36:28,261 cam_name=mavericks num_frames=5 Extracted frames
2024-02-11 20:36:28,261 cam_name=mavericks delay=14 Sleeping
2024-02-11 20:36:28,949 cam_name=mavericksov num_frames=4 Extracted frames
2024-02-11 20:36:28,949 cam_name=mavericksov delay=14 Sleeping
...
```

Find boats in images with [`BoatFinder`](./boatfinder.py#L12).

```
$ ./boatfinder.py ./data/mavericksov/02142024/11/1707939852-thumb-0003.jpg
2024-02-14 13:56:06,022 BoatFinder initializing ...
2024-02-14 13:56:08,380 BoatFinder initialized (for cuda:0); took 2.3576930790004553 seconds
2024-02-14 13:56:08,384 Searching file ./data/mavericksov/02142024/11/1707939852-thumb-0003.jpg...
2024-02-14 13:56:09,939 Finished search in 1.5548269860009896 seconds
2024-02-14 13:56:09,939 >> label=boat    score=0.994     box=[517, 81, 910, 147]
2024-02-14 13:56:09,944 Outlined matches and saved to file ./data/mavericksov/02142024/11/1707939852-thumb-0003_boats.jpg
```
