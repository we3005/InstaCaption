"""
instacaption.py
----------------
Graphical entry point for InstaCaption.

Loads the captioning model once, then shows a window with two buttons:
  - "Caption an Image"  -> opens a file browser, then displays the chosen
                            picture and its caption right in the window.
  - "Live Webcam"        -> opens a webcam window with a live-updating
                            caption overlay (press 'q' in that window to stop).

Usage:
    python instacaption.py
"""

import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from captioner import Captioner
from caption_live import run_live_mode

IMAGE_FILETYPES = [("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All files", "*.*")]
CANVAS_WIDTH = 440
CANVAS_HEIGHT = 280
PREVIEW_MAX_SIZE = (CANVAS_WIDTH - 10, CANVAS_HEIGHT - 10)


class InstaCaptionApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.captioner = None  # loaded in the background after the window appears
        self._current_photo = None  # keep a reference so Tkinter doesn't garbage-collect it

        root.title("InstaCaption")
        root.geometry("580x740")
        root.minsize(580, 740)
        root.resizable(True, True)

        # --- Status line ---
        self.status_var = tk.StringVar(
            value="Loading model... (first run downloads ~1GB, this can take a few minutes)"
        )
        tk.Label(root, textvariable=self.status_var, fg="#666", wraplength=470, justify="center").pack(
            pady=(12, 4)
        )

        # --- Image preview area (Canvas, not Label - avoids char/pixel sizing ambiguity) ---
        self.canvas = tk.Canvas(
            root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#222222", highlightthickness=1,
            highlightbackground="#444444",
        )
        self.canvas.pack(pady=10)
        self._placeholder_text_id = self.canvas.create_text(
            CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, text="No image yet", fill="#888888", font=("Helvetica", 12)
        )
        self._canvas_image_id = None

        # --- Caption text ---
        self.caption_var = tk.StringVar(value="")
        tk.Label(
            root,
            textvariable=self.caption_var,
            wraplength=470,
            font=("Helvetica", 14),
            justify="center",
        ).pack(pady=(4, 12))

        # --- Mode buttons ---
        button_frame = tk.Frame(root)
        button_frame.pack(pady=8)

        self.image_button = tk.Button(
            button_frame, text="Caption an Image", width=20, height=2,
            state="disabled", command=self.on_choose_image,
        )
        self.image_button.grid(row=0, column=0, padx=8)

        self.live_button = tk.Button(
            button_frame, text="Live Webcam", width=20, height=2,
            state="disabled", command=self.on_start_live,
        )
        self.live_button.grid(row=0, column=1, padx=8)

        tk.Button(root, text="Quit", width=12, command=root.quit).pack(pady=(20, 10))

        # Load the model in the background so the window shows up immediately
        threading.Thread(target=self._load_model, daemon=True).start()

    # ---------- model loading ----------

    def _load_model(self):
        captioner = Captioner()
        self.root.after(0, lambda: self._on_model_loaded(captioner))

    def _on_model_loaded(self, captioner: Captioner):
        print("[InstaCaption] Model loaded, GUI is ready.")
        self.captioner = captioner
        self.status_var.set("Ready")
        self.image_button.config(state="normal")
        self.live_button.config(state="normal")

    # ---------- image mode ----------

    def on_choose_image(self):
        if self.captioner is None:
            messagebox.showinfo("InstaCaption", "The model is still loading — please wait a moment and try again.")
            return

        path = filedialog.askopenfilename(title="Choose an image to caption", filetypes=IMAGE_FILETYPES)
        if not path:
            return

        print(f"[InstaCaption] Selected image: {path}")

        try:
            self._show_preview(path)
        except Exception as exc:
            print(f"[InstaCaption] Preview failed: {exc}")
            self._show_placeholder(f"(Couldn't preview image: {exc})")

        self.caption_var.set("Captioning...")
        self.root.update_idletasks()
        self._set_buttons_state("disabled")

        threading.Thread(target=self._caption_image_thread, args=(path,), daemon=True).start()

    def _caption_image_thread(self, path: str):
        print(f"[InstaCaption] Captioning {path} ...")
        start = time.time()
        try:
            caption = self.captioner.caption(path)
            print(f"[InstaCaption] Done in {time.time() - start:.1f}s: {caption}")
        except Exception as exc:  # keep the app alive even if captioning fails
            print(f"[InstaCaption] Captioning failed: {exc}")
            caption = f"(Error captioning image: {exc})"
        self.root.after(0, lambda: self._on_caption_ready(caption))

    def _on_caption_ready(self, caption: str):
        print(f"[InstaCaption] Displaying caption in GUI: {caption}")
        self.caption_var.set(caption)
        self.root.update_idletasks()
        self._set_buttons_state("normal")

    def _show_preview(self, path: str):
        image = Image.open(path).convert("RGB")
        image.thumbnail(PREVIEW_MAX_SIZE)
        photo = ImageTk.PhotoImage(image)

        self.canvas.delete("all")
        self.canvas.create_image(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, image=photo)
        self._current_photo = photo  # prevent garbage collection
        self.root.update_idletasks()

    def _show_placeholder(self, text: str):
        self.canvas.delete("all")
        self.canvas.create_text(
            CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, text=text, fill="#cc4444",
            font=("Helvetica", 11), width=CANVAS_WIDTH - 20,
        )
        self._current_photo = None

    # ---------- live mode ----------

    def on_start_live(self):
        self._set_buttons_state("disabled")
        self.status_var.set("Live mode running — press 'q' in the video window to stop")
        self.root.update()  # repaint the status line before we block for the webcam window

        try:
            run_live_mode(self.captioner)
        except Exception as exc:
            messagebox.showerror("InstaCaption", f"Could not run live mode:\n{exc}")

        self.status_var.set("Ready")
        self._set_buttons_state("normal")

    # ---------- helpers ----------

    def _set_buttons_state(self, state: str):
        self.image_button.config(state=state)
        self.live_button.config(state=state)


def main():
    root = tk.Tk()
    InstaCaptionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
