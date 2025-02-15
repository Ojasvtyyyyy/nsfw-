import torch
import os
import logging
from diffusers import StableDiffusionPipeline
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MODEL_ID = os.getenv("MODEL_ID", "UnfilteredAI/NSFW-gen")

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_model():
    """Loads the NSFW-gen model from Hugging Face."""
    try:
        logging.info(f"Loading model: {MODEL_ID}")
        pipe = StableDiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.float16)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = pipe.to(device)
        logging.info(f"Model loaded on {device}")
        return pipe
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return None

def generate_image(prompt):
    """Generates an image using the model."""
    pipe = load_model()
    if not pipe:
        return None

    try:
        logging.info(f"Generating image for prompt: {prompt}")
        image = pipe(prompt).images[0]
        image_path = "output.png"
        image.save(image_path)
        logging.info("Image generated successfully")
        return image_path
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return None