import os
import sys
from PIL import Image
from typing import Optional, Tuple
from termcolor import colored
import argparse

FILESIZE_THRESHOLD_KB = 500
FILESIZE_THRESHOLD_TOLERANCE = 1.05


def get_image_info(file_path: str) -> Optional[Tuple[float, int, int]]:
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            file_size_kb = os.path.getsize(file_path) / 1024  # Convert bytes to kB
            return file_size_kb, width, height
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resize images in a directory if they exceed a filesize threshold."
    )
    parser.add_argument(
        "--path",
        type=str,
        default="/home/declan/Documents/code/declanoller.github.io/assets/images/thumbnails/",
        help="Path to the directory containing images to resize.",
    )

    parser.add_argument(
        "--max-size-kb",
        type=float,
        default=FILESIZE_THRESHOLD_KB,
        help=f"Maximum allowed file size in kB (default: {FILESIZE_THRESHOLD_KB})",
    )
    args = parser.parse_args()

    filesize_threshold_kb = args.max_size_kb
    directory_path = args.path

    if not os.path.isdir(directory_path):
        print(f"Error: {directory_path} is not a valid directory.")
        sys.exit(1)

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                file_path = os.path.join(root, file)
                image_info = get_image_info(file_path)
                if image_info:
                    file_size_kb, width, height = image_info
                    if (
                        file_size_kb
                        > FILESIZE_THRESHOLD_TOLERANCE * filesize_threshold_kb
                    ):
                        print(colored(f"{file}", "red"))
                        print(
                            colored(
                                f"    over tolerance of {FILESIZE_THRESHOLD_TOLERANCE * filesize_threshold_kb:.0f} kB",
                                "red",
                            )
                        )
                        print(
                            colored(
                                f"    {file_size_kb:.2f} kB, {width}x{height}",
                                "red",
                            )
                        )
                        target_size_kb = filesize_threshold_kb
                        resize_ratio = (target_size_kb / file_size_kb) ** 0.5
                        new_width = int(width * resize_ratio)
                        new_height = int(height * resize_ratio)

                        try:
                            with Image.open(file_path) as img:
                                img = img.resize((new_width, new_height), Image.LANCZOS)
                                img.save(file_path, optimize=True)
                            image_info = get_image_info(file_path)
                            print(
                                colored(
                                    f"    Resized to {new_width}x{new_height}, now under {filesize_threshold_kb} kB",
                                    "green",
                                )
                            )
                            print(
                                colored(
                                    f"    New info: {file_size_kb:.2f} kB, {width}x{height}\n",
                                    "green",
                                )
                            )
                        except Exception as e:
                            print(colored(f"    Failed to resize: {e}", "red"))
                    # else:
                    #     print(f"{file}")
                    #     print(f"    {file_size_kb:.2f} kB, {width}x{height}")


if __name__ == "__main__":
    main()
