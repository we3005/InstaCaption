"""
captioner.py
------------
Core image-captioning engine for InstaCaption.

Uses Salesforce's BLIP model (via Hugging Face transformers) to turn an
image into a natural-language caption, e.g. "a cat is sleeping on a couch".

The model runs locally once downloaded, so after the first run no internet
connection is required and there's no API key to manage.
"""

import sys
from typing import Optional, Union

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

MODEL_NAME = "Salesforce/blip-image-captioning-base"


class Captioner:
    """Loads the BLIP model once and captions images/frames on demand."""

    def __init__(self, model_name: str = MODEL_NAME, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        print(f"Loading captioning model '{model_name}' on {self.device}...", file=sys.stderr)
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name).to(self.device)
        self.model.eval()
        print("Model loaded.", file=sys.stderr)

    @torch.no_grad()
    def caption(self, image: Union[str, Image.Image], prompt: Optional[str] = None) -> str:
        """
        Generate a caption for a PIL Image or a path to an image file.

        prompt: optional text prefix to condition the caption, e.g. "a photo of"
        """
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        elif image.mode != "RGB":
            image = image.convert("RGB")

        if prompt:
            inputs = self.processor(image, prompt, return_tensors="pt").to(self.device)
        else:
            inputs = self.processor(image, return_tensors="pt").to(self.device)

        output_ids = self.model.generate(**inputs, max_new_tokens=30)
        caption = self.processor.decode(output_ids[0], skip_special_tokens=True)
        return caption.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python captioner.py <image_path>")
        sys.exit(1)

    c = Captioner()
    print(c.caption(sys.argv[1]))
