from huggingface_hub import hf_hub_download
import cv2
from doclayout_yolo import YOLOv10
import os
import json
from PIL import Image, ImageDraw
from abc import ABC, abstractmethod

from src.utils.pdf2img import convert_pdf_to_images
from src.utils.config_utils import get_config, get_env
from src.utils.log_utils import get_logger

logger = get_logger(__file__)

class BaseLayoutDetection(ABC):
    @abstractmethod
    def load_model():
        pass


    @abstractmethod
    def detect_text_bbox(model, image_path: str) -> list[dict]:
        pass


    @abstractmethod
    def create_mask_from_bboxes(image_path: str, text_bbox: list[dict]) -> Image.Image:
        pass


class YOLOLayoutDetection(BaseLayoutDetection):
    def load_model(self):
        # os.environ["HUGGINGFACEHUB_API_TOKEN"] = get_env("HUGGINGFACE_TOKEN")
        filepath = hf_hub_download(
            repo_id=get_config("layout_detection_model", "model_path"),
            filename=get_config("layout_detection_model", "model_name"),
        )
        model = YOLOv10(filepath)
        # model = YOLOv10.from_pretrained("juliozhao/DocLayout-YOLO-DocStructBench")
        return model


    def detect_text_bbox(self, model: YOLOv10, image_path: str) -> list[dict]:
        # Perform prediction
        det_res = model.predict(
            image_path,  # Image to predict
            imgsz=1024,  # Prediction image size
            conf=0.9,  # Confidence threshold
            device="cuda:0",  # Device to use (e.g., 'cuda:0' or 'cpu')
        )
        # annotated_frame = det_res[0].plot(pil=True, line_width=5, font_size=20)
        # cv2.imwrite("result.jpg", annotated_frame)
        det_res[0].save_crop("./")
        bbox_info = det_res[0].tojson()
        bbox_info = json.loads(bbox_info)
        text_bbox = []
        for box in bbox_info:
            # TODO: check more box type
            if box["name"] == "plain text" or box["name"] == "title":
                text_bbox.append(box)

        return text_bbox

    def create_mask_from_bboxes(self, image_path: str, text_bbox: list[dict]) -> Image.Image:
        """
        Creates a mask image from bounding boxes.
        
        Parameters:
            image_path (str): Path to the input image.
            text_bbox (dict): Dictionary with keys as IDs and values as (x1, y1, x2, y2) tuples.
            
        Returns:
            PIL.Image.Image: A grayscale ("L") mask image with white boxes on black background.
        """
        # Load the original image to get size
        with Image.open(image_path) as img:
            width, height = img.size

        # Create a black mask
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)

        # Draw each bounding box in white
        for bbox in text_bbox:
            draw.rectangle(
                (
                    bbox["box"]["x1"],
                    bbox["box"]["y1"],
                    bbox["box"]["x2"], 
                    bbox["box"]["y2"]
                ), fill=255)
        
        return mask


if __name__ == "__main__":
    instance = YOLOLayoutDetection()
    model = instance.load_model()
    text_bbox = instance.detect_text_bbox(
        model,
        "/home/phongmt1/phongmt1/project/pdf_translation/output_images/page_1.png",
    )
    mask = instance.create_mask_from_bboxes(
        "/home/phongmt1/phongmt1/project/pdf_translation/output_images/page_1.png",
        text_bbox,
    )
    mask.save("mask.png")
