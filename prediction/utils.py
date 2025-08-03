import io
import logging
import os
from urllib.parse import urlparse

import requests
from .models import Prediction
from .naive import allowed_file, predict
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image


logger = logging.getLogger(__name__)
MAX_FILE_SIZE = 10 * 1024 * 1024


def compress_image(uploaded_file, max_size=(800, 800)):
    try:
        img = Image.open(uploaded_file)
        img.thumbnail(max_size)
        output = io.BytesIO()
        img.save(output, format=img.format or "JPEG", quality=85)
        output.seek(0)
        return ContentFile(output.read(), name=uploaded_file.name)
    except Exception as e:
        logger.error(f"Error compressing image: {e}")
        return None


def get_image_from_request(request, user_data, target_dir):  # noqa: PLR0911
    link = request.POST.get("link")
    if link:
        parsed_url = urlparse(link)
        if parsed_url.scheme not in {"http", "https"}:
            return None, "Only HTTP or HTTPS URLs are allowed."

        file_ext = "jpg"
        img_name = f"{user_data['unique_filename']}.{file_ext}"
        img_path = os.path.join(target_dir, img_name)

        try:
            response = requests.get(link, timeout=5)
            response.raise_for_status()
            with open(img_path, "wb") as f:
                f.write(response.content)
            return img_name, None
        except requests.RequestException as e:
            return None, f"Error fetching image: {e}"

    if "file" in request.FILES:
        uploaded_file = request.FILES["file"]
        if uploaded_file.size > MAX_FILE_SIZE:
            logger.error("File size exceeds 10MB limit")
            return None, "File size exceeds 10MB limit."
        if not allowed_file(uploaded_file.name):
            return None, "Invalid file format. Only JPG, JPEG, and PNG are allowed."
        compressed_file = compress_image(uploaded_file)
        if not compressed_file:
            return None, "Error processing uploaded image."
        file_ext = uploaded_file.name.split(".")[-1].lower()
        img_name = f"{user_data['unique_filename']}.{file_ext}"
        default_storage.save(f"images/{img_name}", compressed_file)
        return img_name, None

    return None, "No image provided."


def process_and_save_prediction(img, user):
    img_full_path = os.path.join(settings.MEDIA_ROOT, "images", img)
    if not os.path.exists(img_full_path):
        return None, "The image file was not found."

    class_result, prob_result = predict(img_full_path)
    prediction = Prediction(
        submitted_by=user,
        image_file=f"images/{img}",
        class_1=class_result[0],
        prob_1=prob_result[0],
        class_2=class_result[1],
        prob_2=prob_result[1],
        class_3=class_result[2],
        prob_3=prob_result[2],
        class_4=class_result[3],
        prob_4=prob_result[3],
    )
    prediction.save()
    return prediction, None
