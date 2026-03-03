import logging
from pathlib import Path

from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def resize_images(
    source_dir: Path,
    output_dir: Path,
    max_width: int = 1920,
    max_height: int = 1080,
) -> None:
    """Resize images in source_dir and save them to output_dir, preserving EXIF metadata including GPS info.

    Args:
        source_dir: Directory containing the original images.
        output_dir: Directory where resized images will be saved.
        max_width: Maximum width of the resized image in pixels.
        max_height: Maximum height of the resized image in pixels.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    image_files = [
        p
        for p in source_dir.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    ]

    for image_path in image_files:
        try:
            with Image.open(image_path) as image:
                # Preserve raw EXIF bytes (includes GPSInfo) before any transformation
                exif_data = image.info.get("exif", b"")

                image.thumbnail((max_width, max_height), Image.LANCZOS)

                output_path = output_dir / image_path.name
                # Pass exif bytes to save so that GPS metadata is retained
                image.save(output_path, exif=exif_data)

            logger.info(f"Resized and saved: {image_path.name}")

        except Exception as e:
            logger.error(f"Failed to process {image_path.name}: {e}")


def run(*args, **options) -> None:
    if len(args) < 2:
        raise ValueError("Usage: resize_images <source_dir> <output_dir> [max_width] [max_height]")

    source_dir = Path(args[0])
    output_dir = Path(args[1])

    max_width = int(args[2]) if len(args) > 2 else 1920
    max_height = int(args[3]) if len(args) > 3 else 1080

    resize_images(
        source_dir=source_dir,
        output_dir=output_dir,
        max_width=max_width,
        max_height=max_height,
    )
