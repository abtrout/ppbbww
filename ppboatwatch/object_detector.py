import logging
import sys
import torch

from PIL import Image, ImageDraw
from time import perf_counter
from transformers import DetrImageProcessor, DetrForObjectDetection
from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, thresh=0.95, labels=None):
        self.thresh = thresh
        self.filter_labels = labels

        t0 = perf_counter()
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.processor = DetrImageProcessor.from_pretrained(
            "facebook/detr-resnet-50", revision="no_timm"
        )
        self.model = DetrForObjectDetection.from_pretrained(
            "facebook/detr-resnet-50", revision="no_timm"
        ).to(self.device)
        logging.info(
            f"ObjectDetector initialized DETR for device {self.device}; took {perf_counter() - t0} seconds."
        )

        t0 = perf_counter()
        self.yolo = YOLO("yolo11s.pt")
        logging.info(
            f"ObjectDetector initialized YOLO; took {perf_counter() - t0} seconds."
        )

    def find(self, img):
        detr_results = list(self._find_detr(img))
        yield from detr_results

        # compare YOLO11s to DETR
        yolo_results = list(self._find_yolo(img))
        detr_labels = sorted(label for label, _, _ in detr_results)
        yolo_labels = sorted(label for label, _, _ in yolo_results)
        if detr_labels != yolo_labels:
            logging.warning(
                f"[dark_launch] Models differ — DETR: {detr_labels}  YOLO11s: {yolo_labels}"
            )

    def _find_detr(self, img):
        res = self.__match_results(img)
        for label, score, box in zip(res["labels"], res["scores"], res["boxes"]):
            label = self.model.config.id2label[label.item()]
            if (not self.filter_labels) or (label in self.filter_labels):
                yield (label, round(score.item(), 2), map(int, box.tolist()))

    def _find_yolo(self, img):
        for result in self.yolo(img, conf=self.thresh, verbose=False):
            for box in result.boxes:
                label = self.yolo.names[int(box.cls)]
                if (not self.filter_labels) or (label in self.filter_labels):
                    yield (label, round(float(box.conf), 2), map(int, box.xyxy[0].tolist()))

    def __match_results(self, image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        outputs = self.model(**inputs)
        target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
        return self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=self.thresh
        )[0]
