# InstaCaption

Turn any image — or your live webcam feed — into a natural-language caption.
Example: a photo of a cat sleeping on a couch becomes **"a cat is sleeping on a couch"**.

Built on [BLIP](https://huggingface.co/Salesforce/blip-image-captioning-base), an
open image-captioning model from Salesforce, run locally via Hugging Face
`transformers`. No API key required, and after the first run (which downloads
the model, ~1GB) it works fully offline.

## Setup

1. **Python 3.9+** is recommended.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   - If you have an NVIDIA GPU and want faster inference, install a CUDA-enabled
     build of PyTorch first by following https://pytorch.org/get-started/locally/,
     then install the rest of `requirements.txt`.
3. The first time you run either script, it will download the BLIP model
   (a few hundred MB to ~1GB depending on variant). This only happens once.

## Usage

### GUI app (recommended)

```bash
python instacaption.py
```

Opens a window with two buttons:

- **🖼 Caption an Image** — opens your file browser immediately; click a
  picture and it's shown in the window along with its caption.
- **🎥 Live Webcam** — opens a webcam window with a live-updating caption
  overlaid on the video. Press `q` in that window to stop.

Note: while live mode is running, the main InstaCaption window will look
unresponsive — that's expected (it's how the webcam window's own event loop
works on most systems) and it goes back to normal as soon as you press `q`.

### Or run a single mode from the command line

If you only ever want one mode and prefer a CLI:

```bash
python caption_image.py path/to/photo.jpg      # caption a single image
python caption_image.py                        # ...or opens a file picker

python caption_live.py                         # live webcam captioning
python caption_live.py --camera 1              # use a different webcam
python caption_live.py --interval 1.0          # caption more frequently (default: every 2s)
```

Captioning runs a bit slower than real-time video, so the live mode updates
the caption periodically (every `--interval` seconds) rather than on every
single frame — this keeps the video feed smooth while still refreshing the
caption regularly.

## Project structure

```
InstaCaption/
├── instacaption.py      # GUI entry point: buttons for image mode and live mode
├── captioner.py         # Core model-loading + captioning logic (shared by both modes)
├── caption_image.py     # Image-captioning logic; also runnable standalone from the CLI
├── caption_live.py      # Live webcam captioning logic; also runnable standalone from the CLI
├── requirements.txt
└── README.md
```

## Notes & tips

- **Better quality captions**: swap `MODEL_NAME` in `captioner.py` from
  `Salesforce/blip-image-captioning-base` to `Salesforce/blip-image-captioning-large`
  for noticeably better captions at the cost of a larger download and slower
  inference.
- **Speed**: on CPU, expect roughly 0.5–2 seconds per caption depending on
  your machine. A GPU will be much faster.
- **Custom prompts**: `Captioner.caption()` accepts an optional `prompt`
  argument (e.g. `"a photo of"`) to help steer the caption's phrasing.
