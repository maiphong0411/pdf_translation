from openai import OpenAI
from pydantic import BaseModel

from src.utils.config_utils import get_env

client = OpenAI(api_key=get_env("OPENAI_API_KEY"))


class TranslatorOutput(BaseModel):
    translated_text: str


class BaseTranslator:
    def translate(
        self,
        text_list: list[str],
        source_language: str = "english",
        target_language: str = "vietnamese",
    ) -> TranslatorOutput:
        raise NotImplementedError("Subclasses should implement this method.")


class OpenAITranslator(BaseTranslator):
    def translate(
        self,
        text: str,
        source_language: str = "english",
        target_language: str = "vietnamese",
    ) -> TranslatorOutput:
        """
        Translate a list of strings using OpenAI's GPT-4o model.
        """
        # Call the OpenAI API to get the translation
        response = client.responses.parse(
            model="gpt-4o",
            input=[
                {
                    "role": "system",
                    "content": f"Translate the following text from {source_language} to {target_language}.",
                },
                {"role": "user", "content": text},
            ],
            text_format=TranslatorOutput,
        )

        return response.output_parsed.translated_text


if __name__ == "__main__":
    # Example usage
    translator = OpenAITranslator()
    result = translator.translate(
        ["Hello, how are you?", "This is a test."],
        source_language="english",
        target_language="vietnamese",
    )
    print(result.translated_text)
