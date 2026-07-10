import eel
import os
from PIL import Image

# Point Eel to your web asset directory
# eel.init('web')

# # Expose this function to the frontend UI
# @eel.expose
# def process_data(user_input):
#     print(f"Received from UI: {user_input}")
#     return f"Python processed: '{user_input.upper()}'"

# # Start the application window
# eel.start('index.html', size=(400, 300))


def import_image(image_path, mode):
    image_path = image_path
    try:
        img = Image.open(image_path)
        if mode == 1:
            crop_factor = float(input("Enter crop factor: "))
            resize_image(image_path, crop_factor)
        elif mode == 2:
            print("test")
            # convert_image(img)
        else:
            user_mode = int(input("Enter mode (1 for resize, 2 for convert): "))
            import_image(image_path, user_mode)
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
    salt = "-salt"
    new_file_name = original_file_name.replace(".", f"{salt}.")
    remove_underscores = input("Do you want to remove underscores from the file name? (yes/no): ").strip().lower() == "yes"
    if (remove_underscores == True):
        new_file_name = new_file_name.replace("_", "")
    else:
        new_file_name = new_file_name
    new_file_path = image_path.replace(original_file_name, new_file_name)
    return new_file_path

def main():
    user_mode = int(input("Enter mode (1 for resize, 2 for convert): "))
    import_image("./web/_DSC1679.JPG", user_mode) 

if __name__ == "__main__":
    main()