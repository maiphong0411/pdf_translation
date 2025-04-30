import fitz  # PyMuPDF
from PIL import Image
import io
from collections import Counter


class BaseTextExtractor:
    """
    Base class for text extraction from PDF files.
    """

    def __init__(self, input_pdf_path: str):
        self.input_pdf_path = input_pdf_path
        self.DPI = 300

    def extract_text(self) -> dict:
        """
        Extract text from the PDF file.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class TextExtractor(BaseTextExtractor):
    """
    Text extractor for PDF files using PyMuPDF.
    """

    def consensus(self, items: list):
        item_count = Counter(items)
        most_common_item, _ = item_count.most_common(1)[0]
        return most_common_item

    def extract_text(self) -> dict:
        """
        Extract text from the PDF file using PyMuPDF.
        """
        # Open the PDF
        doc = fitz.open(self.input_pdf_path)

        # Initialize a dictionary to hold text data
        text_data = {}

        # Iterate through the pages
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Extract text block-level data
            text_blocks = page.get_text("dict")["blocks"]

            # Initialize a list to hold block data
            blocks_data = []

            # Iterate through each block and extract text and bounding box
            for block_num, block in enumerate(text_blocks):
                print(block)
                if block["type"] == 0:
                    # Extract text and bounding box
                    block_text = ""
                    font_size, font_color, font_family = [], [], []

                    for line in block["lines"]:
                        for span in line["spans"]:
                            block_text += span["text"] + "\n"
                            font_size.append(span["size"])
                            font_color.append(span["color"])
                            font_family.append(span["font"])

                    # get image
                    x0, y0, x1, y1 = block["bbox"]
                    print(block["bbox"])
                    rect = fitz.Rect(x0, y0, x1, y1)
                    cropped_page = page.get_pixmap(
                        matrix=fitz.Matrix(self.DPI / 72, self.DPI / 72), clip=rect
                    )
                    image_bytes = cropped_page.tobytes("png")

                    # Wrap bytes in a BytesIO object (so PIL can read it like a file)
                    image_stream = io.BytesIO(image_bytes)
                    image = Image.open(image_stream)

                    blocks_data.append(
                        {
                            "block_num": block_num + 1,
                            "text": block_text,
                            "bbox": block["bbox"],
                            "image": image,
                            "font_size": self.consensus(font_size),
                            "font_color": self.consensus(font_color),
                            "font_family": self.consensus(font_family),
                        }
                    )
            text_data[page_num] = blocks_data
        return text_data


if __name__ == "__main__":
    input_pdf_path = "/home/phongmt1/phongmt1/project/pdf_translation/1st.pdf"
    extractor = TextExtractor(input_pdf_path)
    text_data = extractor.extract_text()

    # Print extracted text data
    for page_num, blocks in text_data.items():
        print(f"Page {page_num}:")
        for block in blocks:
            print(f"Block {block['block_num']}:")
            print(block["font_size"])
            # Save the image if needed
            # block["image"].save(f"block_{page_num}_{block['block_num']}.png")
