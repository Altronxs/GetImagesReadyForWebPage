import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image, ImageTk, ImageOps
from pathlib import Path
from pillow_heif import register_heif_opener

# ---------------------------------------------------------------------------
# HEIC/HEIF support
# ---------------------------------------------------------------------------
# pillow-heif patches Pillow so Image.open() understands .heic/.heif files
# transparently. This needs to run once, before any Image.open() call, and
# is safe to call multiple times.
def enable_heif_support():
    register_heif_opener()


def open_image_file(path):
    """
    Central place to open an image file, HEIC/HEIF included.

    Every place in this app that needs to load a file from disk (thumbnail
    preview, resizing, and eventually format conversion) should go through
    this function rather than calling Image.open() directly, so HEIC/HEIF
    support stays in one spot. Reuse this in the "Convert" mode
    implementation as well.
    """
    return Image.open(path)


enable_heif_support()

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
# Tuple of file paths selected by the user via the file picker.
image_paths = ()
# Keeps a live reference to every PhotoImage we create so Tkinter doesn't
# garbage-collect them (PhotoImage has no strong reference from the widget).
tk_images_cache = []
# Keeps track of the thumbnail Label widgets so we can destroy them when a
# new selection is made (prevents old thumbnails from piling up).
image_widgets = []


def get_crop_factor(width, height, size):
    """
    Work out the scale factor needed to bring the *longer* side of an image
    down to `size`.

    `size` can be:
      - a string like "1080p" (from the resolution combobox) -> the trailing
        "p" is stripped and the number is treated as the target length.
      - a plain int/str number (e.g. used for the 200px thumbnail preview).

    Square images (width == height) are scaled based on that shared side
    length, same as the width/height branches below.
    """
    if width > height:
        # Landscape image: scale based on width.
        if isinstance(size, str):
            new_width = int(size.replace("p", ""))
            new_crop_factor = new_width / width

            return new_crop_factor
        else:
            new_width = int(size)
            new_crop_factor = new_width / width

            return new_crop_factor
    elif height > width:
        # Portrait image: scale based on height.
        if isinstance(size, str):
            new_height = int(size.replace("p", ""))
            new_crop_factor = new_height / height

            return new_crop_factor
        else:
            new_height = int(size)
            new_crop_factor = new_height / height

            return new_crop_factor
    else:
        # Square image: width and height are equal, so either can be used
        # as the reference side length.
        if isinstance(size, str):
            new_side = int(size.replace("p", ""))
            new_crop_factor = new_side / width

            return new_crop_factor
        else:
            new_side = int(size)
            new_crop_factor = new_side / width

            return new_crop_factor

def process_image(image_path, mode, crop_factor, crop_mode, resolution, quality):
    """
    Entry point wired up to the "Run" button.

    image_path : tuple of file paths selected by the user (global image_paths)
    mode       : 1 = Resize, 2 = Convert (Convert is not implemented yet)
    crop_factor: value from the percentage slider (used when crop_mode == 1)
    crop_mode  : 1 = crop by percentage, 2 = crop by target resolution
    resolution : selected resolution string (e.g. "1080p"), used when crop_mode == 2
    quality    : quality combobox value, 1-10, scaled up to a 10-100 JPEG quality
    """
    if isinstance(image_path, tuple):
        for path in image_path:
            try:
                img = open_image_file(path)
                # Quality combobox is 1-10; scale to a more typical
                # JPEG/PIL "quality" range of 10-100.
                new_quality = int(quality) * 10

                # Resize the image based on user's selection
                if mode == 1:
                    if crop_mode == 1:
                        # Crop by percentage: slider value is 0-100, convert to a 0.0-1.0 factor.
                        resize_image(path, float(crop_factor) / 100.0, new_quality)
                    elif crop_mode == 2:
                        # Crop by target resolution: work out the factor needed
                        # to bring the longer side down to the chosen resolution.
                        width, height = img.size
                        resize_image(path, get_crop_factor(width, height, resolution), new_quality)
                elif mode == 2:
                    # "Convert" mode is not implemented yet.
                    print("test")
                    # convert_image(img)

            except IOError:
                print("Unable to open image. Please check the file path.")
                pass


def resize_image(image_path, crop_factor, quality_factor):
    """
    Open the image at image_path, scale it by crop_factor, fix its
    orientation using the EXIF data, and save it alongside the original
    with a "-resized" suffix (see add_salt_to_file_name).
    """
    with open_image_file(image_path) as image:
        width, height = image.size
        new_width = int(width * crop_factor)
        new_height = int(height * crop_factor)
        # LANCZOS gives noticeably sharper/cleaner results than the default
        # nearest-neighbor resampling when downscaling.
        resized_img = image.resize((new_width, new_height), Image.LANCZOS)
        # Re-apply orientation from EXIF data so the resized image isn't
        # accidentally rotated/mirrored.
        img_oriented = ImageOps.exif_transpose(resized_img )
        # Add salt to the file name and save the resized image
        new_file_path = add_salt_to_file_name(image_path)
        img_oriented.save(new_file_path, optimize=True, quality=quality_factor)


def add_salt_to_file_name(image_path):
    """
    Build the output file path for a resized image: strips underscores
    from the original file name, appends "-resized", and uses whatever
    format is currently selected in the save-format combobox.
    """
    salt = "-resized"
    file_format = save_format_val.get()

    path_obj = Path(image_path)
    # Path.stem only strips the LAST extension, so internal dots
    # (e.g. "photo.v2") are preserved correctly. We keep the stem as-is
    # (previously underscores were stripped out here, which could make two
    # differently-named source files collide onto the same output path,
    # e.g. "photo_1.jpg" and "photo1.jpg" would both become "photo1-resized.jpg").
    stem = path_obj.stem

    new_file_name = f"{stem}{salt}.{file_format}"
    new_file_path = str(path_obj.with_name(new_file_name))

    print(new_file_path)
    return new_file_path

def select_image_files():
    """
    Handle the "Browse File" button: open a native file picker restricted
    to common image types, then refresh the thumbnail list with whatever
    the user picked.
    """
    global image_paths, tk_images_cache, image_widgets

    # Define allowed file extensions
    filetypes = (
        ('Image files', '*.jpg *.jpeg *.png *.bmp *.gif *.heic *.heif'),
        ('All files', '*.*')
    )

    # Open the file picker dialog
    filename = fd.askopenfilenames(
        title='Select a file',
        initialdir='/',
        filetypes=filetypes
    )

    if filename:
        image_paths = filename
        update_image_widgets(filename)

def update_image_widgets(filename):
    """
    Rebuild the scrollable list of thumbnails/labels for the currently
    selected files. Clears out anything left over from a previous
    selection first.
    """
    # Remove existing widgets and clear caches
    for widget in image_widgets:
        widget.destroy()  # Remove the widget from the GUI
    image_widgets.clear()  # Clear the list of image widgets
    tk_images_cache.clear()  # Clear the cache before adding new images

    # Update the message label with selected file name(s)
    if isinstance(filename, tuple):
        counter = len(filename)
        message = f"Selected {counter} files"
        message_label.config(text=message)

        for index, path in enumerate(filename):
            try:
                img = open_image_file(path)
                width, height = img.size
                # Scale each thumbnail down so its longer side is ~200px.
                factor = get_crop_factor(width, height, 200)
                new_width = int(width * factor)
                new_height = int(height * factor)

                resized_img = img.resize((new_width, new_height), Image.BILINEAR)  # Resize for display

                img_tk = ImageOps.exif_transpose(resized_img)
                img_tk = ImageTk.PhotoImage(img_tk)

                img_label = tk.Label(image_info_frame, image=img_tk)
                img_label.grid(row=index, column=0, padx=5, pady=5)

                size_label = tk.Label(image_info_frame, text=f"Original File Size:{width}x{height}", font=('bold', 10))
                size_label.grid(row=index, column=2, padx=5, pady=5)

                tk_images_cache.append(img_tk)  # Add the PhotoImage to the cache
                image_widgets.append(img_label)  # Keep track of the thumbnail widget
                image_widgets.append(size_label)  # Keep track of the size label widget too
            except IOError:
                print("Unable to open image. Please check the file path.")


def on_scale_move(value):
    """Update the label next to the percentage slider as it's dragged."""
    scale_label.config(text=f"Current Value: {int(float(value))}")

def update_crop_mode_label(*args):
    """
    Called whenever crop_mode_val changes (and once at startup) to keep the
    "Crop By:" label and the visible controls (percentage slider vs
    resolution dropdown) in sync with the selected crop mode.
    """
    current_crop_mode = crop_mode_val.get()

    if current_crop_mode == 1:
        # Percentage mode: show the slider, hide the resolution dropdown.
        crop_mode_label.config(text="Crop By: Percentage")
        show(horizontal_scale)
        show(scale_label)
        hide(resolution_label)
        hide(resolution_combobox)
    elif current_crop_mode == 2:
        # Resolution mode: show the resolution dropdown, hide the slider.
        crop_mode_label.config(text="Crop By: Resolution")
        hide(horizontal_scale)
        hide(scale_label)
        show(resolution_label)
        show(resolution_combobox)

    else:
        crop_mode_label.config(text="No crop mode selected.")

def hide(widget):
    """Hide a gridded widget while preserving its grid options for later."""
    widget.grid_remove()

def show(widget):
    """Re-show a widget previously hidden with hide()."""
    widget.grid()

# Keep scrollregion in sync with the frame's actual size
def _on_frame_configure(event):
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))


# Keep the inner frame's width matched to the canvas width
def _on_canvas_configure(event):
    scroll_canvas.itemconfig(canvas_window, width=event.width)



# Optional: mouse-wheel scrolling (Windows/macOS uses <MouseWheel>, Linux uses Button-4/5)
def _on_mousewheel(event):
    scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

# ---------------------------------------------------------------------------
# UI setup
# ---------------------------------------------------------------------------
root = tk.Tk()
root.title("Image Processor")
root.geometry("810x540")

# --- Mode selection (Resize / Convert) -------------------------------------
# Create a frame for the mode selection
top_left_frame = ttk.Frame(root)
top_left_frame.grid(row=0, column=0, padx=11, pady=11, sticky='nsew')
mode_frame = ttk.Frame(top_left_frame, relief="solid", padding="10")
mode_frame.grid(row=0, column=0, sticky='ns')

tk.Label(mode_frame, text="Select a mode:", font=('bold', 12)).grid(row=0, column=0, padx=10, pady=10, sticky='nw')
mode = tk.IntVar(value=1)  # Default mode is 1 (resize)

# Resize radio button
resize_radio = ttk.Radiobutton(mode_frame, text="Resize", variable=mode, value=1)
convert_radio = ttk.Radiobutton(mode_frame, text="Convert", variable=mode, value=2)
resize_radio.grid(row=1, column=0, padx=10, pady=10, sticky='nw')
convert_radio.grid(row=1, column=1, padx=0, pady=10, sticky='nw')

# --- File picker + selection summary label ----------------------------------
# Create a button to open the file dialog
file_frame = ttk.Frame(top_left_frame, relief="solid", padding="10")
file_frame.grid(row=2, column=0, pady=(10, 0), sticky='nsew')
open_button = ttk.Button(file_frame, text='Browse File', command=select_image_files)
open_button.grid(row=0, column=0, padx=0, pady=10, sticky='nw')
message_label = tk.Label(file_frame, text="No file selected.", wraplength=350, justify='left')
message_label.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky='nw')


# --- Crop controls (percentage slider or resolution dropdown) ---------------
# Create a horizontal scale for crop factor
scale_frame = ttk.Frame(root, padding="10", relief="solid")
scale_frame.grid(row=0, column=2, pady=10, sticky='nsew')

crop_mode_frame = ttk.Frame(scale_frame, padding="10", borderwidth=0, relief="flat")
crop_mode_frame.grid(row=0, column=0, sticky='nw')

crop_mode_val = tk.IntVar(value=2)  # Default crop mode is 1 (percentage)

# Crop by label
crop_mode_label = tk.Label(crop_mode_frame, text="Crop By:", font=('bold', 12))
crop_mode_label.grid(row=0, column=0, padx=10, pady=5, sticky='nw')

# Crop by percentage radio button
crop_mode_percentage_radio = ttk.Radiobutton(crop_mode_frame, text="Percentage", variable=crop_mode_val, value=1)
crop_mode_resolution_radio = ttk.Radiobutton(crop_mode_frame, text="Resolution", variable=crop_mode_val, value=2)
crop_mode_percentage_radio.grid(row=1, column=0, padx= 10, pady= 10, sticky='nw')
crop_mode_resolution_radio.grid(row=1, column=1, pady=10, sticky='nw')

# Scale for crop factor
scale_val = tk.IntVar(value=50)
horizontal_scale = tk.Scale(
    scale_frame,
    from_=12,
    to=100,
    orient='horizontal',
    variable=scale_val,
    command=on_scale_move,
    length=200
)
horizontal_scale.grid(row=2, column=0, sticky='nw')
scale_label = tk.Label(scale_frame, text="Current Value: 50")
scale_label.grid(row=3, column=0, sticky='nw')

# Resolution combobox
resolution_label = tk.Label(scale_frame, text="Select Resolution:")
resolution_label.grid(row=2, column=0, sticky='nw')
resolution_val = tk.StringVar()
resolution_combobox = ttk.Combobox(scale_frame, width=41, textvariable=resolution_val)

# Adding resolution options to the combobox
resolution_combobox['values'] = ('2160p', '1440p', '1080p', '720p', '480p', '360p', '240p')
resolution_combobox.set('1080p')
resolution_combobox.grid(row=3, column=0, columnspan=1, sticky='nw')


# --- Scrollable thumbnail list ------------------------------------------------
# Create a container for the scrollable frame
scroll_container = tk.Frame(root, relief="solid", borderwidth=1)
scroll_container.grid(row=1, column=0, columnspan=3, padx=(10, 0), sticky='nsew')
scroll_container.grid_rowconfigure(0, weight=1)
scroll_container.grid_columnconfigure(0, weight=1)

# Canvas is the actual scrollable widget
scroll_canvas = tk.Canvas(scroll_container)
scroll_canvas.grid(row=0, column=0, sticky='nsew')

# Create a Scrollbar and attach it to the canvas
scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=scroll_canvas.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
scroll_canvas.configure(yscrollcommand=scrollbar.set)

# Create a Frame INSIDE the canvas that will hold the actual widgets
image_info_frame = ttk.Frame(scroll_canvas)
canvas_window = scroll_canvas.create_window((0, 0), window=image_info_frame, anchor='nw')
scroll_canvas.bind("<Configure>", _on_canvas_configure)
scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)

# --- Save options (format + quality) -----------------------------------------
save_frame = ttk.Frame(root, padding="10")
save_frame.grid(row=0, column=3, columnspan=3, sticky='nsew')
image_info_frame.bind("<Configure>", _on_frame_configure)
save_format_frame = ttk.Frame(save_frame, relief="solid", padding="10")
save_format_frame.grid(row=0, column=0, sticky='ns')

# Format combobox
save_format_label = tk.Label(save_format_frame, text="Format:")
save_format_label.grid(row=2, column=0, sticky='nw')
save_format_val = tk.StringVar(value='')
save_format_combobox = ttk.Combobox(save_format_frame, textvariable=save_format_val)

# Adding Format options to the combobox
save_format_combobox['values'] = ('png','jpg')
save_format_combobox.set('jpg')
save_format_combobox.grid(row=3, column=0, columnspan=1, sticky='nw')

# Create a new frame for quality settings
quality_frame = ttk.Frame(save_frame, padding="10", relief="solid")
quality_frame.grid(row=1, column=0, pady=10, sticky='nsew')

# Quality combobox
quality_label = tk.Label(quality_frame, text="Select Quality:")
quality_label.grid(row=4, column=0, sticky='nw')
quality_val = tk.StringVar(value='')
quality_combobox = ttk.Combobox(quality_frame, textvariable=quality_val)

# Adding quality options to the combobox
quality_combobox['values'] = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
quality_combobox.set('10')
quality_combobox.grid(row=5, column=0, sticky='nw')

# --- Run button: kicks off processing with all currently selected options ---
ttk.Button(root, text="Run", command=lambda: process_image(image_paths, mode.get(), scale_val.get(), crop_mode_val.get(), resolution_val.get(), quality_val.get())).grid(row=9, column=0, padx=10, pady=10, sticky='nw')

# Dynamically update the crop mode label
crop_mode_val.trace_add("write", update_crop_mode_label)
update_crop_mode_label()

root.mainloop()

