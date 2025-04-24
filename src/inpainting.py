from simple_lama_inpainting import SimpleLama
from PIL import Image
from abc import ABC, abstractmethod

class BaseInpainting(ABC):
    @abstractmethod
    def load_model(self):
        pass


    @abstractmethod
    def invoke(self, image_path: str, mask_path: str):
        pass

class SimpleLamaInpainting(BaseInpainting):
    def load_model(self):
        model = SimpleLama()
        return model


    def invoke(self, image_path: str, mask_path: str):
        simple_lama = self.load_model()
        image = Image.open(image_path)
        mask = Image.open(mask_path).convert("L")

        result = simple_lama(image, mask)
        result.save("inpainted_image.png")
        return result


if __name__ == "__main__":
    inpaint_instance = SimpleLamaInpainting()
    inpaint_instance.invoke(
        "/home/phongmt1/phongmt1/project/pdf_translation/output_images/page_1.png",
        "tmp/mask.png",
    )