import fitz  # PyMuPDF
from src.translator import OpenAITranslator

translator = OpenAITranslator()

# Convert integer color to RGB tuple (0-1 range)
def int_to_rgb(color_int):
    r = ((color_int >> 16) & 255) / 255
    g = ((color_int >> 8) & 255) / 255
    b = (color_int & 255) / 255
    return (r, g, b)

# Normalize the bounding box coordinates
def normalize_rect(rect):
    if rect.y1 < rect.y0:  # If Y-values are inverted
        print("change y1 and y0")
        rect.y0, rect.y1 = rect.y1, rect.y0
    # Make sure the rectangle is within the page bounds
    rect.x0 = max(rect.x0, 0)
    rect.y0 = max(rect.y0, 0)
    return rect

def redact_and_reverse_text_preserve_style(input_pdf_path, output_pdf_path, font_path=None):
    doc = fitz.open(input_pdf_path)

    # Load custom font if provided
    # custom_font = None
    # if font_path:
    #     custom_font = fitz.Font(fontfile=font_path)
    #     print(f"Using custom font: {font_path}")

    for page in doc:
        text_dict = page.get_text("dict")
        reversed_spans = []

        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    rect = fitz.Rect(span["bbox"])
                    text = span["text"].strip()
                    if not text:
                        continue

                    # Normalize and ensure the rect is inside the page
                    rect = normalize_rect(rect)

                    # Redact the original text
                    page.add_redact_annot(rect, fill=None)

                    # Reverse the text or translate it
                    translated_text = translator.translate(text, target_language="chinese")
                    print(translated_text)
                    # Save span details for later use
                    reversed_spans.append({
                        "rect": rect,
                        "text": translated_text,
                        "font": span["font"],  # Use custom font if provided
                        "size": span["size"],
                        "color": int_to_rgb(span["color"])
                    })

        # Apply redactions after removing the original text
        page.apply_redactions()

        # Reinsert the reversed text at the same coordinates with the same font, size, and color
        for span in reversed_spans:
            result = page.insert_text(
                (span["rect"].x0, span["rect"].y1),
                span["text"],
                fontname="microsoft-yahei",
                fontfile=font_path,
                # fontname=span["font"] if custom_font is None else custom_font.name,  # Use custom font
                fontsize=span["size"],
                color=span["color"],
                overlay=True
            )
            # Check if the text is correctly inserted
            if result < 0:
                print(f"Text did not fit in rect: {span['rect']} for text: {span['text']}")

    # Save the final PDF
    doc.save(output_pdf_path)
    doc.close()
    print(f"Redacted and reversed PDF saved to: {output_pdf_path}")

if __name__ == "__main__":
    input_pdf_path = "1st.pdf"  # Path to the input PDF file
    output_pdf_path = "trans_output_redacted.pdf"  # Path to save the redacted PDF file
    font_path = "/home/phongmt1/phongmt1/project/pdf_translation/font_family/Microsoft_Yahei.ttf"
    redact_and_reverse_text_preserve_style(input_pdf_path, output_pdf_path, font_path=font_path)


