from PIL import Image
from pathlib import Path

DEFAULT_LARGEST_DIMENSION_SIZE = 1200


def resize_images(
    image_paths: list[Path],
    largest_dimension_size: int = DEFAULT_LARGEST_DIMENSION_SIZE,
):
    """
    Resize images to the specified output size.

    Parameters:
    - image_paths: List of paths to the images to be resized.
    - largest_dimension_size: The size of the largest dimension (width or height) for the resized images.

    Returns:
    - None
    """

    for path in image_paths:
        print(f"Resizing image: {path}")
        with Image.open(path) as img:
            width, height = img.size
            is_landscape = width > height

            if is_landscape:
                if width <= largest_dimension_size:
                    print(
                        f"Image {path} is already smaller than the largest dimension size. Skipping resizing."
                    )
                    continue
                wpercent = largest_dimension_size / float(width)
                new_height = int((float(height) * float(wpercent)))
                new_width = largest_dimension_size
            else:
                if height <= largest_dimension_size:
                    print(
                        f"Image {path} is already smaller than the largest dimension size. Skipping resizing."
                    )
                    continue
                hpercent = largest_dimension_size / float(height)
                new_width = int((float(width) * float(hpercent)))
                new_height = largest_dimension_size

            print(
                f"Original size: {width}x{height}, New size: {new_width}x{new_height}"
            )

            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            resized_img.save(path)


def resize_images_from_path(
    im_path: Path, largest_dimension_size: int = DEFAULT_LARGEST_DIMENSION_SIZE
):
    """
    Resize all images in a specified directory.

    Parameters:
    - im_path: Path to the directory containing images to be resized.
    - largest_dimension_size: The size of the largest dimension (width or height) for the resized images.

    Returns:
    - None
    """

    image_paths = (
        list(im_path.rglob("*.jpg"))
        + list(im_path.rglob("*.jpeg"))
        + list(im_path.rglob("*.png"))
    )
    print(f"Found {len(image_paths)} images to resize. {image_paths}")
    resize_images(image_paths, largest_dimension_size)


if __name__ == "__main__":
    im_path = Path("/mnt/c/Users/janns/OneDrive/EcoBlogData/photos")
    resize_images_from_path(
        im_path, largest_dimension_size=DEFAULT_LARGEST_DIMENSION_SIZE
    )
