# Image Processor GUI

A Tkinter desktop app for batch-resizing images. Select multiple files, preview
them in a scrollable grid, choose how you want them scaled, and save the
results with a new filename and your choice of format/quality.

## Features

- **Multi-file selection** — pick one or more images at once via a native file
  picker (`.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.heic`, `.heif`).
- **Thumbnail preview** — selected images are listed in a scrollable panel so
  you can confirm what you picked before processing.
- **Two ways to scale:**
  - **Percentage** — scale every image by a percentage (12–100%) using a
    slider.
  - **Resolution** — scale each image so its longer side matches a target
    resolution (2160p, 1440p, 1080p, 720p, 480p, 360p, or 240p), preserving
    aspect ratio.
- **EXIF-aware** — orientation data is reapplied after resizing so photos
  don't come out rotated or mirrored.
- **Output format & quality** — save as PNG or JPG, with a quality slider
  from 1 (lowest) to 10 (highest).
- **Non-destructive output** — processed files are saved next to the
  originals with a `-resized` suffix, so source images are never overwritten.

> **Note:** A "Convert" mode exists in the UI but is not yet implemented —
> selecting it currently does nothing.

## Requirements

- Python 3
- [Pillow](https://pypi.org/project/Pillow/) (`pip install Pillow`)
- [pillow-heif](https://pypi.org/project/pillow-heif/) (`pip install pillow-heif`)
  — enables opening `.heic`/`.heif` files
- Tkinter (usually bundled with Python; on Linux you may need to install it
  separately, e.g. `sudo apt install python3-tk`)

## Usage

1. **Run the app:**
   ```bash
   python app.py
   ```
2. **Select images:** Click **Browse File** and choose one or more images.
   Your selections appear as thumbnails in the panel below.
3. **Choose a mode:** Select **Resize** (currently the only working mode).
4. **Choose how to scale:**
   - **Percentage** — drag the slider to set the scale factor (12–100%).
   - **Resolution** — pick a target resolution from the dropdown; the image's
     longer side will be scaled to match it.
5. **Set the output format and quality:** Choose **png** or **jpg**, and pick
   a quality level from 1–10.
6. **Click Run.** Each image is processed and saved in its original folder
   as `<original-name>-resized.<format>`. The saved path for each file is
   printed to the console.

## Parameters

| Parameter | Options | Notes |
|---|---|---|
| Mode | Resize, Convert | Convert is not implemented yet |
| Scale by | Percentage, Resolution | Determines which control (slider or dropdown) sets the scale factor |
| Percentage | 12–100% | Used when "Scale by" is set to Percentage |
| Resolution | 2160p, 1440p, 1080p, 720p, 480p, 360p, 240p | Scales the image's longer side to this length |
| Format | png, jpg | Applied to the output file extension |
| Quality | 1–10 | Scaled internally to a 10–100 save quality |

## Known Limitations

- Convert mode is a placeholder and does not currently convert file formats.
- If an image can't be opened (e.g. a corrupted or unsupported file), it's
  skipped with a message printed to the console rather than shown in the UI.

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for
improvements, please open an issue on GitHub. You can also submit a pull
request with your changes.
