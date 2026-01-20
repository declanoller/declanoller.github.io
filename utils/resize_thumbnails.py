import os
import sys
from PIL import Image
from typing import Optional, Tuple
from termcolor import colored
import argparse

FILESIZE_THRESHOLD_KB = 800
FILESIZE_THRESHOLD_TOLERANCE = 1.1


def get_image_info(file_path: str) -> Optional[Tuple[float, int, int]]:
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            file_size_kb = os.path.getsize(file_path) / 1024  # Convert bytes to kB
            return file_size_kb, width, height
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


import os
from PIL import Image


def ensure_under_kb(
    file_path: str,
    target_kb: float,
    *,
    min_dim: int = 256,
    max_iters: int = 8,
) -> tuple[float, int, int]:
    """
    Repeatedly resizes/saves until the file is <= target_kb (or limits reached).
    Returns (final_kb, w, h).
    """
    target_bytes = int(target_kb * 1024)
    ext = os.path.splitext(file_path)[1].lower()

    def cur_bytes() -> int:
        return os.path.getsize(file_path)

    with Image.open(file_path) as im:
        im.load()
        w, h = im.size

    for i in range(max_iters):
        size_bytes = cur_bytes()
        if size_bytes <= target_bytes:
            with Image.open(file_path) as im2:
                return size_bytes / 1024, im2.size[0], im2.size[1]

        # How far off are we?
        ratio = target_bytes / size_bytes  # < 1.0 if too big

        # First-order guess: scale by sqrt(ratio), then be a bit more aggressive
        # because compression often gets worse than area-scaling predicts.
        scale = (ratio**0.5) * 0.95

        with Image.open(file_path) as im:
            w, h = im.size
            new_w = max(min_dim, int(w * scale))
            new_h = max(min_dim, int(h * scale))

            # If we're not shrinking anymore, force an extra step.
            if new_w >= w and new_h >= h:
                new_w = max(min_dim, int(w * 0.9))
                new_h = max(min_dim, int(h * 0.9))

            im = im.resize((new_w, new_h), Image.LANCZOS)

            save_kwargs = {}
            if ext in (".jpg", ".jpeg"):
                # JPEG: pick sane defaults; you can also do a quality search if you want.
                save_kwargs = dict(optimize=True, quality=85, progressive=True)
            elif ext == ".png":
                # PNG: optimize + max compression level helps, but may not be enough.
                save_kwargs = dict(optimize=True, compress_level=9)

                # Optional but often huge: palette-ize thumbnails (good for web graphics)
                # Comment out if you don't want any color quantization.
                if im.mode not in ("P", "L"):
                    im = im.convert("RGBA") if im.mode != "RGBA" else im
                    im = im.quantize(colors=256, method=Image.MEDIANCUT)

            im.save(file_path, **save_kwargs)

    # Give final stats even if we didn't hit target
    with Image.open(file_path) as im2:
        final_kb = cur_bytes() / 1024
        return final_kb, im2.size[0], im2.size[1]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resize images in a directory if they exceed a filesize threshold."
    )
    parser.add_argument(
        "--path",
        type=str,
        default="/home/declan/Documents/code/declanoller.github.io/assets/thumbnails/",
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

                        final_kb, final_w, final_h = ensure_under_kb(
                            file_path, filesize_threshold_kb
                        )
                        if final_kb > filesize_threshold_kb:
                            print(
                                colored(
                                    f"    Still above target: {final_kb:.2f} kB", "red"
                                )
                            )
                        else:
                            print(
                                colored(
                                    f"    Final: {final_kb:.2f} kB, {final_w}x{final_h}\n",
                                    "green",
                                )
                            )


if __name__ == "__main__":
    main()
