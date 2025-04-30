from PIL import Image  # install by > python3 -m pip install --upgrade Pillow


def images_to_pdf(image_paths, pdf_path, resolution=100.0):
    """
    Converts a list of image paths to a single PDF file.

    :param image_paths: List of paths to image files.
    :param pdf_path: Path to save the output PDF file.
    :param resolution: Resolution of the output PDF.
    """
    if not image_paths:
        raise ValueError("The image_paths list cannot be empty.")

    # Open the images
    images = [Image.open(image_path) for image_path in image_paths]

    # Save the first image as PDF and append the rest
    images[0].save(
        pdf_path, "PDF", resolution=resolution, save_all=True, append_images=images[1:]
    )
