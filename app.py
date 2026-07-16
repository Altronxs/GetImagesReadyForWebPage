import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image, ImageTk, ImageOps
from pathlib import Path

# List to hold image paths selected by user
image_paths = ()
# List to cache PhotoImage references safely in global scope
tk_images_cache = []
# List to keep track of visual labels for cleaning up later
image_widgets = []


def get_crop_factor(width, height, size):
    if width > height:
        if isinstance(size, str):
            new_width = int(size.replace("p", ""))
            new_crop_factor = new_width / width
           
            return new_crop_factor
        else:
            new_width = int(size)
            new_crop_factor = new_width / width
           
            return new_crop_factor
    elif height > width:
        if isinstance(size, str):
            new_height = int(size.replace("p", ""))
            new_crop_factor = new_height / height
           
            return new_crop_factor
        else:
            new_height = int(size)
            new_crop_factor = new_height / height
         
            return new_crop_factor

def process_image(image_path, mode, crop_factor, crop_mode, resolution, quality):
    if isinstance(image_path, tuple):
        for path in image_path:
            try:
                img = Image.open(path)
                new_quality = int(quality) * 10

                # Resize the image based on user's selection
                if mode == 1:
                    if crop_mode == 1: 
                        resize_image(path, float(crop_factor) / 100.0, new_quality)
                    elif crop_mode == 2:
                        width, height = img.size
                        resize_image(path, get_crop_factor(width, height, resolution), new_quality)
                elif mode == 2:
                    print("test")
                    # convert_image(img)

            except IOError:
                print("Unable to open image. Please check the file path.")
                pass


def resize_image(image_path, crop_factor, quality_factor): 
    with Image.open(image_path) as image:
        width, height = image.size
        new_width = int(width * crop_factor)
        new_height = int(height * crop_factor)
        resized_img = image.resize((new_width, new_height))
        img_oriented = ImageOps.exif_transpose(resized_img )
        # Add salt to the file name and save the resized image
        new_file_path = add_salt_to_file_name(image_path)
        img_oriented.save(new_file_path, optimize=True, quality=quality_factor)
        


def add_salt_to_file_name(image_path):
    original_file_name = os.path.basename(image_path)
    
    # Add salt to the file name
    salt = "-resized"
    file_format = save_format_val.get()
    replace_special_character = f"{original_file_name.replace('_', '')}"
    new_file_name = f"{replace_special_character.replace(f'{get_file_format(image_path)}', f'.{file_format}')}"
    salted_file_name = f"{new_file_name.replace('.', f'{salt}.')}"
    new_file_path = image_path.replace(original_file_name, salted_file_name)
    print(new_file_path)
    return new_file_path


def select_image_files():
    global image_paths, tk_images_cache, image_widgets
    
    # Define allowed file extensions
    filetypes = (
        ('Image files', '*.jpg *.jpeg *.png *.bmp *.gif'),
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
                img = Image.open(path)
                width, height = img.size
                factor = get_crop_factor(width, height, 100)
                new_width = int(width * factor)
                new_height = int(height * factor)
                
                resized_img = img.resize((new_width, new_height))  # Resize for display

                img_tk = ImageOps.exif_transpose(resized_img)
                img_tk = ImageTk.PhotoImage(img_tk)

                img_label = tk.Label(image_info_frame, image=img_tk)
                img_label.grid(row=index, column=0, padx=5, pady=5)

                tk_images_cache.append(img_tk)  # Add the PhotoImage to the cache
                image_widgets.append(img_label)  # Keep track of the widget
            except IOError:
                print("Unable to open image. Please check the file path.")


def on_scale_move(value):
    scale_label.config(text=f"Current Value: {int(float(value))}")

def update_crop_mode_label(*args):
    current_crop_mode = crop_mode_val.get()
    
    if current_crop_mode == 1:
        crop_mode_label.config(text="Crop By: Percentage")
        show(horizontal_scale)
        show(scale_label)
        hide(resolution_label)
        hide(resolution_combobox)
    elif current_crop_mode == 2:
        crop_mode_label.config(text="Crop By: Resolution")
        hide(horizontal_scale)
        hide(scale_label)
        show(resolution_label)
        show(resolution_combobox)

    else:
        crop_mode_label.config(text="No crop mode selected.")

def get_file_format(file_path):
    # Create a Path object from the given file path
    file_path_obj = Path(file_path)
    
    # Get the file name and extension
    file_name, file_extension = file_path_obj.stem, file_path_obj.suffix
    
    return file_extension

def hide(widget):
    widget.grid_remove()


def show(widget):
    widget.grid()

root = tk.Tk()
root.title("Image Processor")
root.geometry("810x500")

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

# Create a button to open the file dialog
file_frame = ttk.Frame(top_left_frame, relief="solid", padding="10")
file_frame.grid(row=2, column=0, pady=(10, 0), sticky='nsew')
open_button = ttk.Button(file_frame, text='Browse File', command=select_image_files)
open_button.grid(row=0, column=0, padx=0, pady=10, sticky='nw')
message_label = tk.Label(file_frame, text="No file selected.", wraplength=350, justify='left')
message_label.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky='nw')


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


# Show the imported images and their respective information
image_info_frame = ttk.Frame(root, padding="10", relief="solid")
image_info_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')


save_frame = ttk.Frame(root, padding="10")
save_frame.grid(row=0, column=3, columnspan=3, sticky='nsew')

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
quality_frame.grid(row=1, column=0, pady=10, sticky='ns')

# Quality combobox
quality_label = tk.Label(quality_frame, text="Select Quality:")
quality_label.grid(row=4, column=0, sticky='nw')
quality_val = tk.StringVar(value='')
quality_combobox = ttk.Combobox(quality_frame, textvariable=quality_val)

# Adding quality options to the combobox
quality_combobox['values'] = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
quality_combobox.set('10')
quality_combobox.grid(row=5, column=0, sticky='nw')

ttk.Button(root, text="Run", command=lambda: process_image(image_paths, mode.get(), scale_val.get(), crop_mode_val.get(), resolution_val.get(), quality_val.get())).grid(row=9, column=0, padx=10, pady=10, sticky='nw')

# Dynamically update the crop mode label
crop_mode_val.trace_add("write", update_crop_mode_label)
update_crop_mode_label()

root.mainloop()
