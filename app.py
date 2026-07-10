import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image
image_paths = []
def import_image(image_path, mode, crop_factor):

    if isinstance(image_path, tuple):
        for path in image_path:
            print(path)
            try:
                img = Image.open(path)
                if mode == 1:
                    resize_image(path, (float(crop_factor) / 100.0))
                elif mode == 2:
                    print("test")
                    # convert_image(img)
                else:
                    import_image(image_path, user_mode, crop_factor)
            except IOError:
                print("Unable to open image. Please check the file path.")
                pass


def resize_image(image_path, crop_factor):
    with Image.open(image_path) as image:
        width, height = image.size
        width = int(int(width) * crop_factor)
        height = int(int(height) * crop_factor)
        image = image.resize((width, height))
        print(f"Image resized to {width}x{height}.")
        new_file_path = add_salt_to_file_name(image_path)
        image.save(new_file_path)
        print(f"Image resized and saved as '{new_file_path}'.")
        
def add_salt_to_file_name(image_path):
    print(os.path.basename(image_path))
    # Add salt to the file name here
    original_file_name = os.path.basename(image_path)
    salt = "-resized"
    new_file_name = original_file_name.replace(".", f"{salt}.")
    new_file_name = new_file_name.replace("_", "")
    new_file_path = image_path.replace(original_file_name, new_file_name)
    return new_file_path

def select_file():
    global image_paths
    # Define allowed file extensions
    filetypes = (
        ('Image files', '*.jpg *.jpeg *.png *.bmp *.gif'),
        ('All files', '*.*')
    )

    # Open the picker
    filename = fd.askopenfilenames(
        title='Select a file',
        initialdir='/',
        filetypes=filetypes
    )
    
    if filename:
        image_paths = filename
        message_label.config(text=filename)
        print(f"Selected file(s): {image_paths}")

def update_mode_label(*args):

    current_mode = mode.get()

    if current_mode == 1:
        mode_label.config(text="Resize mode selected.")
    elif current_mode == 2:
        mode_label.config(text="Convert mode selected.")
    else:
        mode_label.config(text="No mode selected.")

root = tk.Tk()


root.title("Image Processor")
root.geometry("500x500")


mode_frame = ttk.Frame(root, padding="10", relief="solid")
mode_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nw')


tk.Label(mode_frame, text="Select a mode:", font=('bold', 12)).grid(row=0, column=0, padx=10, pady=10, sticky='nw')
mode = tk.IntVar(value=1)  # Default mode is 1 (resize)


resize_radio = ttk.Radiobutton(mode_frame, text="Resize", variable=mode, value=1)
convert_radio = ttk.Radiobutton(mode_frame, text="Convert", variable=mode, value=2)
resize_radio.grid(row=1, column=0, padx=10, pady=10, sticky='nw')
convert_radio.grid(row=1, column=1, padx=0, pady=10, sticky='nw')


mode_label = tk.Label(root, text="")
mode_label.grid(row=3, column=0, padx=10, pady=10, sticky='nw')
mode.trace_add("write", update_mode_label)
update_mode_label()


scale_val = tk.IntVar(value=50)  
def on_scale_move(value):
    scale_label.config(text=f"Current Value: {int(float(value))}")
    print(scale_val.get())
horizontal_scale = tk.Scale(
    root, 
    from_=10,          
    to=100,           
    orient='horizontal',
    variable=scale_val,
    command=on_scale_move,
    length=200     
)
horizontal_scale.grid(row=7, column=0, padx=10, sticky='nw')
scale_label = tk.Label(root, text="Current Value: 50")
scale_label.grid(row=8, column=0, padx=10, sticky='nw')

open_button = ttk.Button(root, text='Browse File', command=select_file).grid(row=4, column=0, padx=10, pady=10, sticky='nw')
message_label = tk.Label(root, text="No file selected.", wraplength=350, justify='left')
message_label.grid(row=5, column=0, columnspan=5, padx=10, pady=10, sticky='nw')

ttk.Button(root, text="Run", command=lambda: import_image(image_paths, mode.get(), scale_val.get())).grid(row=9, column=0, padx=10, pady=10, sticky='nw')
root.mainloop()