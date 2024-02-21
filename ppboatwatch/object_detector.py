import logging
import sys
import torch

from PIL import Image, ImageDraw
from time import perf_counter
from transformers import DetrImageProcessor, DetrForObjectDetection


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
            f"ObjectDetector initialized for device {self.device}; took {perf_counter() - t0} seconds."
        )

    def find(self, img):
        res = self.__match_results(img)
        for label, score, box in zip(res["labels"], res["scores"], res["boxes"]):
            label = self.model.config.id2label[label.item()]
            if (not self.filter_labels) or (label in self.filter_labels):
                yield (label, round(score.item(), 2), map(int, box.tolist()))

    def __match_results(self, image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        outputs = self.model(**inputs)
        target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
        return self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=self.thresh
        )[0]
