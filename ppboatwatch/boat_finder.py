import logging
import sys
import torch

from PIL import Image, ImageDraw
from time import perf_counter
from transformers import DetrImageProcessor, DetrForObjectDetection


class BoatFinder:
    def __init__(self):
        logging.info(f"BoatFinder initializing ...")
        t0 = perf_counter()
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        # https://huggingface.co/facebook/detr-resnet-50
        self.processor = DetrImageProcessor.from_pretrained(
            "facebook/detr-resnet-50", revision="no_timm")
        self.model = DetrForObjectDetection.from_pretrained(
            "facebook/detr-resnet-50", revision="no_timm").to(self.device)
        logging.info(f"BoatFinder initialized (for {self.device}); took {perf_counter() - t0} seconds")

    def find(self, img):
        t0 = perf_counter()
        res = self.__match_results(img)
        for score, label, box in zip(res["scores"], res["labels"], res["boxes"]):
            label = self.model.config.id2label[label.item()]
            if label == "boat":
                score = round(score.item(), 3)
                box = [int(i) for i in box.tolist()]
                yield (score, label, box)
        logging.info(f"Finished search in {perf_counter() - t0} seconds")

    def __match_results(self, image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        outputs = self.model(**inputs)
        target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
        return self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.5
        )[0]

