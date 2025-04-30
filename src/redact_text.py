from PIL import Image
from collections import Counter
import fitz  # PyMuPDF

from src.text_extraction import TextExtractor


class BaseRedactor:
    def redact(self, pdf_info: dict) -> str:
        raise NotImplementedError("Subclasses should implement this method.")


class Redactor(BaseRedactor):
    def _get_background_color(self, image: Image):
        """
        Get the background color of the image.
        """
        # Get image dimensions
        width, height = image.size

        # Extract colors from the 4 corners
        top_left = image.getpixel((0, 0))
        top_right = image.getpixel((width - 1, 0))
        bottom_left = image.getpixel((0, height - 1))
        bottom_right = image.getpixel((width - 1, height - 1))

        # Convert to HEX
        top_left_hex = self.rgb_to_hex(top_left)
        top_right_hex = self.rgb_to_hex(top_right)
        bottom_left_hex = self.rgb_to_hex(bottom_left)
        bottom_right_hex = self.rgb_to_hex(bottom_right)

        final_color = self.consensus(
            [top_left_hex, top_right_hex, bottom_left_hex, bottom_right_hex]
        )
        return final_color

    def consensus(self, colors: list):
        color_count = Counter(colors)
        most_common_color, _ = color_count.most_common(1)[0]
        return most_common_color

    def rgb_to_hex(self, rgb):
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    def hex_to_rgb(self, hex_color):
        """
        Convert a hex color string to an RGB tuple.

        Args:
            hex_color (str): Hex color string, e.g., '#FFAABB' or 'FFAABB'.

        Returns:
            tuple: (R, G, B)
        """
        # Remove '#' if present
        hex_color = hex_color.lstrip("#")

        # Check if valid length
        if len(hex_color) != 6:
            raise ValueError("Hex color must be 6 characters long.")

        # Convert
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        return (r, g, b)

    def redact(self, pdf_info: dict, pdf_path: str, output_path: str):
        doc = fitz.open(pdf_path)

        for page_num, page_info in pdf_info.items():
            page = doc.load_page(int(page_num))

            for block in page_info:
                bbox = block["bbox"]
                x0, y0, x1, y1 = bbox
                rect = fitz.Rect(x0, y0, x1, y1)
                image = block["image"]

                # Get the background color
                background_color = self._get_background_color(image)

                # Convert to RGB
                red, green, blue = self.hex_to_rgb(background_color)

                # draw new shape
                shape = page.new_shape()
                shape.draw_rect(rect)
                shape.finish(
                    fill=(red / 255, green / 255, blue / 255), fill_opacity=1.0, width=0
                )
                shape.commit()

        doc.save(output_path)

        return output_path


if __name__ == "__main__":
    # Example usage
    pdf_path = "1st.pdf"
    output_path = "redacted_1st.pdf"
    text_extractor = TextExtractor(pdf_path)
    pdf_info = text_extractor.extract_text()

    # print(pdf_info)
    redactor = Redactor()
    redacted_pdf_path = redactor.redact(pdf_info, pdf_path, output_path)
    print(f"Redacted PDF saved at: {redacted_pdf_path}")
