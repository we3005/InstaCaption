cat > caption_image.py << 'EOF'
"""
caption_image.py
----------------
Caption a single image file.

Can be run standalone:
    python caption_image.py path/to/image.jpg
    python caption_image.py                 # opens a file picker dialog

Or imported and used from instacaption.py via run_image_mode().
"""

from __future__ import annotations

import argparse
import sys

from captioner import Captioner


def pick_file_via_dialog() -> str | None:
    """Open a native file-picker dialog so the user can choose an image."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print("tkinter isn't available in this environment; please type an image path instead.")
        return None

    root = tk.Tk()
    root.withdraw()  # hide the empty root window
    root.attributes("-topmost", True)  # bring the dialog to the front
    path = filedialog.askopenfilename(
        title="Choose an image to caption",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All files", "*.*")],
    )
    root.destroy()
    return path or None


def run_image_mode(captioner: Captioner, image_path: str | None = None):
    """
    Caption a single image. If image_path isn't given, opens a file picker.
    Reuses an already-loaded Captioner so the model isn't reloaded each time.
    """
    image_path = image_path or pick_file_via_dialog()
    if not image_path:
        print("No image selected.")
        return

    caption = captioner.caption(image_path)

    print("\n" + "=" * 40)
    print(f"Image:   {image_path}")
    print(f"Caption: {caption}")
    print("=" * 40)


def main():
    parser = argparse.ArgumentParser(description="InstaCaption - caption a single image")
    parser.add_argument("image", nargs="?", help="Path to an image file. If omitted, a file picker opens.")
    args = parser.parse_args()

    captioner = Captioner()
    run_image_mode(captioner, args.image)


if __name__ == "__main__":
    main()
EOF