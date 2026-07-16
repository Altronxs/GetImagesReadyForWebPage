Image Processor GUI
This script is designed as a graphical user interface (GUI) tool that allows users to select multiple image files, resize or crop them based on specified parameters, and save the processed images with different formats and qualities.

Features
Image Selection: Users can select one or more image files using a file picker dialog.
Image Display: The selected images are displayed in a grid format within the GUI for visual inspection.
Resize/Crop Options:
Resize: Resizes the images based on user-specified percentage or resolution.
Crop: Crops the images by either percentage or resolution, depending on the selected mode.
Image Processing: The script processes the selected images according to the chosen parameters and saves them with a new file name that includes a salted suffix for uniqueness.
Usage
Step-by-Step Guide
Run the Script:

Open your terminal or command prompt.
Navigate to the directory where you saved this script.
Run the script using Python: python image_processor.py.
Select Image Files:

The GUI will open with a file picker dialog. Click on "Browse File" to select one or more image files (supported formats are .jpg, .jpeg, .png, .bmp, and .gif).
View Selected Images:

Once you've selected the images, they will be displayed in a grid format within the GUI.
Set Processing Parameters:

Choose between "Resize" or "Convert" modes.
Select the crop mode (percentage or resolution).
Set the crop factor and resolution if applicable.
Choose the desired image format from the combobox (png or jpg).
Run the Process:

Click on the "Run" button to process the selected images according to your specified parameters.
Save Processed Images:

The processed images will be saved with a new file name that includes a salted suffix, ensuring uniqueness.
The script will display the path of each saved image in the console.
Parameters
Mode: Choose between "Resize" or "Convert".

Resize: Resize the images based on user-specified percentage or resolution.
Convert: Convert the images to a different format (not implemented yet).
Crop Mode:

Percentage: Crop by percentage of the image size.
Resolution: Crop by a specific resolution.
Crop Factor/Resolution: Set the crop factor as a percentage or specify the desired resolution in pixels.

Image Format: Choose between png and jpg.

Contributing
Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue on GitHub. You can also submit a pull request with your changes.

