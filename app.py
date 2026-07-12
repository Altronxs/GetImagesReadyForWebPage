import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image, ImageTk

image_paths = ()
tk_images_cache = []  # Holds the PhotoImage references safely in global scope
image_widgets = []    # Keeps track of visual labels so we can clean them up later

def import_image(image_path, mode, crop_factor, crop_mode, resolution):
    if isinstance(image_path, tuple):
        for path in image_path:
            try:
                img = Image.open(path)
                if mode == 1:
                    if crop_mode == 1:
                        resize_image(path, (float(crop_factor) / 100.0))
                    elif crop_mode == 2:
                        width, height = img.size
                        if width > height:
                            new_width = int((resolution).replace("p", ""))
                            new_crop_factor = new_width / width
                            resize_image(path, new_crop_factor)
                        elif height > width:
                            new_height = int((resolution).replace("p", ""))
                            new_crop_factor = new_height / height
                            resize_image(path, new_crop_factor)
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
    global image_paths, tk_images_cache, image_widgets
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

        for widget in image_widgets:
            widget.destroy()  # Remove the widget from the GUI
        image_widgets.clear()  # Clear the list of image widgets
        tk_images_cache.clear()  # Clear the cache before adding new images

        # Update the message label with the selected file name(s)
        if isinstance(filename, tuple):
            counter = len(filename)
            message = "Selected" + f" {counter} files"
            message_label.config(text=message)
            for index, path in enumerate(filename):
                # message += f" - {os.path.basename(path)}"
                print()
                try:
                    img = Image.open(path)
                    img_resized = img.resize((100, 100))  # Resize for display

                    img_tk = ImageTk.PhotoImage(img_resized)

                    img_label = tk.Label(image_info_frame, image=img_tk)
                    img_label.grid(row=index, column=0, padx=5, pady=5)
                    
                    tk_images_cache.append(img_tk)  # Add the PhotoImage to the cache
                    image_widgets.append(img_label)  # Keep track of the widget
                except IOError:
                    print("Unable to open image. Please check the file path.")
                    pass
        else:
            message_label.config(text=f"Selected file: {os.path.basename(filename)}")

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

def hide(widget):
    widget.grid_remove()

def show(widget):
    widget.grid()

root = tk.Tk()


root.title("Image Processor")
root.geometry("540x500") 
# Create a frame for the mode selection
top_left_frame = ttk.Frame(root)
top_left_frame.grid(row=0, column=0, padx=11, pady=11, sticky='nsew')
mode_frame = ttk.Frame(top_left_frame, relief="solid", padding="10")
mode_frame.grid(row=0, column=0, sticky='ns')


tk.Label(mode_frame, text="Select a mode:", font=('bold', 12)).grid(row=0, column=0, padx=10, pady=10, sticky='nw')
mode = tk.IntVar(value=1)  # Default mode is 1 (resize)


resize_radio = ttk.Radiobutton(mode_frame, text="Resize", variable=mode, value=1)
convert_radio = ttk.Radiobutton(mode_frame, text="Convert", variable=mode, value=2)
resize_radio.grid(row=1, column=0, padx=10, pady=10, sticky='nw')
convert_radio.grid(row=1, column=1, padx=0, pady=10, sticky='nw')


# Create a button to open the file dialog
file_frame = ttk.Frame(top_left_frame, relief="solid", padding="10")
file_frame.grid(row=2, column=0, pady=(10,0), sticky='nsew')
open_button = ttk.Button(file_frame, text='Browse File', command=select_file)
open_button.grid(row=0, column=0, padx=0, pady=10, sticky='nw')
message_label = tk.Label(file_frame, text="No file selected.", wraplength=350, justify='left')
message_label.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky='nw')






# Create a horizontal scale for crop factor
scale_frame = ttk.Frame(root, padding="10", relief="solid")
scale_frame.grid(row=0, column=2, pady=10, sticky='nsew') 

crop_mode_frame = ttk.Frame(scale_frame, padding="10", borderwidth=0, relief="flat")
crop_mode_frame.grid(row=0, column=0, sticky='nw')

crop_mode_val = tk.IntVar(value=1)  # Default crop mode is 1 (percentage) 2 (resolution)

crop_mode_label = tk.Label(crop_mode_frame, text="Crop By:", font=('bold', 12))
crop_mode_label.grid(row=0, column=0, padx=10, pady=5, sticky='nw')


crop_mode_percentage_radio = ttk.Radiobutton(crop_mode_frame, text="Percentage", variable=crop_mode_val, value=1)
crop_mode_resolution_radio = ttk.Radiobutton(crop_mode_frame, text="Resolution", variable=crop_mode_val, value=2)
crop_mode_percentage_radio.grid(row=1, column=0, padx= 10, pady= 10, sticky='nw')
crop_mode_resolution_radio.grid(row=1, column=1, pady=10, sticky='nw')


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

# Combobox creation
resolution_label = tk.Label(scale_frame, text="Select Resolution:")
resolution_label.grid(row=2, column=0, sticky='nw')
resolution_val = tk.StringVar()
resolution_combobox = ttk.Combobox(scale_frame, width = 41, textvariable = resolution_val)

# Adding combobox drop down list
resolution_combobox['values'] = ('2160p','1440p', '1080p', '720p', '480p', '360p', '240p')

resolution_combobox.grid(row = 3, column = 0, columnspan=1, sticky='nw',)
resolution_combobox.current()

# show the imported images and their respective information
image_info_frame = ttk.Frame(root, padding="10", relief="solid")
image_info_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')



ttk.Button(root, text="Run", command=lambda: import_image(image_paths, mode.get(), scale_val.get(), crop_mode_val.get(), resolution_val.get())).grid(row=9, column=0, padx=10, pady=10, sticky='nw')

# Dynamically update 
crop_mode_val.trace_add("write", update_crop_mode_label)
update_crop_mode_label()

root.mainloop()