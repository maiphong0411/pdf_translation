import os
import shutil
from typing import List
from pdf2image import convert_from_path
from PIL.Image import Image

from src.utils.config_utils import get_config
from src.utils.log_utils import get_logger

logger = get_logger(__file__)

def convert_pdf_to_images(
    pdf_path: str,
    output_dir: str = "output_images",
    output_prefix: str = "page",
    dpi: int = 300,
) -> List[str]:
    """
    Converts a PDF file into PNG images, one per page, and saves them in a specified directory.

    If the output directory exists, it will be deleted before saving new images.

    Args:
        pdf_path (str): The path to the PDF file to convert.
        output_dir (str): Directory where images will be saved (default is 'output_images').
        output_prefix (str): The prefix for output image filenames.
        dpi (int): Resolution in DPI for the conversion (default is 300).

    Returns:
        List[str]: A list of file paths to the saved PNG images.
    """
    # Remove existing directory if it exists
    if os.path.exists(output_dir):
        logger.info("The folder exsisted ... Removing ....")
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    logger.info("Converting PDFs to images ")
    images: List[Image] = convert_from_path(pdf_path, dpi=dpi)
    output_paths: List[str] = []

    for i, img in enumerate(images):
        output_path = os.path.join(output_dir, f"{output_prefix}_{i + 1}.png")
        img.save(output_path, "PNG")
        output_paths.append(output_path)

    return output_paths

if __name__ == "__main__":
    path = "/home/phongmt1/phongmt1/project/pdf_translation/tmp/1st.pdf"
    convert_pdf_to_images(path)