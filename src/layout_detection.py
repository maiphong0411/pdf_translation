from huggingface_hub import hf_hub_download
import cv2
from doclayout_yolo import YOLOv10
import os
from src.utils.pdf2img import convert_pdf_to_images
from src.utils.config_utils import get_config, get_env
from src.utils.log_utils import get_logger

logger = get_logger(__file__)


def load_model():
    # os.environ["HUGGINGFACEHUB_API_TOKEN"] = get_env("HUGGINGFACE_TOKEN")
    filepath = hf_hub_download(
        repo_id=get_config("layout_detection_model", "model_path"),
        filename=get_config("layout_detection_model", "model_name"),
    )
    model = YOLOv10(filepath)
    # model = YOLOv10.from_pretrained("juliozhao/DocLayout-YOLO-DocStructBench")
    return model


def detect(model: YOLOv10, image_path: str):
    # Perform prediction
    det_res = model.predict(
        image_path,  # Image to predict
        imgsz=1024,  # Prediction image size
        conf=0.9,  # Confidence threshold
        device="cuda:0",  # Device to use (e.g., 'cuda:0' or 'cpu')
    )
    annotated_frame = det_res[0].plot(pil=True, line_width=5, font_size=20)
    cv2.imwrite("result.jpg", annotated_frame)


if __name__ == "__main__":
    model = load_model()
    detect(
        model,
        "/home/phongmt1/phongmt1/project/pdf_translation/output_images/page_1.png",
    )
