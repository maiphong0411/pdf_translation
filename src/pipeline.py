import fitz
import io
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
from pypdf import PdfReader, PdfWriter, PageObject


from src.text_extraction import TextExtractor
from src.redact_text import Redactor
from src.translator import OpenAITranslator


def int_to_rgb(color_int: int) -> tuple:
    """
    Convert an integer to an (R, G, B) tuple.

    Args:
        color_int (int): Integer representing the color.

    Returns:
        tuple: (R, G, B)
    """
    r = (color_int >> 16) & 0xFF
    g = (color_int >> 8) & 0xFF
    b = color_int & 0xFF
    return (r / 255, g / 255, b / 255)


class Pipeline:
    def __init__(self, pdf_path: str, output_path: str):
        self.pdf_path = pdf_path
        self.output_path = output_path
        self.text_extractor = TextExtractor(pdf_path)
        self.redactor = Redactor()
        self.translator = OpenAITranslator()

    def invoke(self):
        # Step 1: Extract text from the PDF
        pdf_info = self.text_extractor.extract_text()

        # Step 2: Redact the text
        redacted_pdf_path = self.redactor.redact(
            pdf_info, self.pdf_path, self.output_path
        )

        # Step 3: Translate the text
        for page_num, page_info in pdf_info.items():
            for block in page_info:
                text = block["text"]

                result: str = self.translator.translate(
                    text,
                    source_language="english",
                    target_language="vietnamese",
                )
                block["translated_text"] = result
        return pdf_info, redacted_pdf_path

    def draw_pdf(
        self,
        pdf_info,
        redacted_pdf_path,
        font_path: str,
        font_name: str,
        output_path: str = "output_pdf.pdf",
    ):
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        # Read original PDF
        reader = PdfReader(redacted_pdf_path)
        writer = PdfWriter()

        # For each page, create a transparent canvas with text

        # Process each page
        for page_number, page in enumerate(reader.pages):
            block = pdf_info[page_number]
            print(block)
            # Get original page size
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)

            # Create a transparent PDF with the same size
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(width, height))

            for text_item in block:
                print(text_item["translated_text"])
                print("====")
                # Get the bounding box and text
                bbox = text_item["bbox"]
                x0, y0, x1, y1 = bbox
                y_position = height - y0

                can.setFont(font_name, text_item["font_size"])
                can.setFillColor(
                    int_to_rgb(text_item["font_color"])  # Convert int to RGB tuple
                )
                # Draw the text on the canvas line by line
                for line in text_item["translated_text"].split('\n'):
                    can.drawString(x0, y_position, line)
                    y_position -= 15  # Decrease y position for next line

                # can.drawString(x0, height - y0, text_item["translated_text"])
                break

            can.save()
            packet.seek(0)

            # Read the overlay PDF
            overlay_pdf = PdfReader(packet)
            overlay_page = overlay_pdf.pages[0]

            # Merge the overlay onto the original page
            page.merge_page(overlay_page)
            writer.add_page(page)

        # Save the final PDF
        with open(output_path, "wb") as f:
            writer.write(f)

        return output_path


if __name__ == "__main__":
    # Example usage
    pdf_path = "1st.pdf"
    output_path = "redacted_1st.pdf"
    font_path = (
        "/home/phongmt1/phongmt1/project/pdf_translation/font_family/Roboto-Regular.ttf"
    )
    font_name = "Roboto-Regular"
    pipeline = Pipeline(pdf_path, output_path)
    pdf_info, redacted_pdf_path = pipeline.invoke()

    # print(f"PDF Info: {pdf_info}")
    # print(f"Redacted PDF saved at: {redacted_pdf_path}")
    # Draw the translated text on the redacted PDF
    output_path = pipeline.draw_pdf(pdf_info, redacted_pdf_path, font_path, font_name)
