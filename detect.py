#!/usr/bin/env python3

import logging
import sys
import torch

from PIL import Image
from time import perf_counter
from transformers import DetrImageProcessor, DetrForObjectDetection


class BoatFinder:
    def __init__(self):
        logging.info(f"BoatFinder initializing ...") 
        t0 = perf_counter()
        # https://huggingface.co/facebook/detr-resnet-50
        self.processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
        self.model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
        logging.info(f"BoatFinder initialized! took {perf_counter() - t0} seconds")

    def find(self, img):
        res = self.__match_results(img)
        for score, label, box in zip(res["scores"], res["labels"], res["boxes"]):
            label = self.model.config.id2label[label.item()]
            if label == "boat":
                score = round(score.item(), 3)
                box = [round(i, 3) for i in box.tolist()]
                yield (score, label, box)

    def __match_results(self, image):
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)
        target_sizes = torch.tensor([image.size[::-1]])
        return self.processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.5)[0]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"USAGE: {sys.argv[0]} /path/to/file_that_might_have_boats.jpg")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

    bf = BoatFinder()
    for img_file in sys.argv[1:]:
        image = Image.open(img_file)
        logging.info(f"Searching file {img_file}...")
        for score, label, box in bf.find(image):
            logging.info(f">> label={label}\t score={score}\t box={box}\t")
