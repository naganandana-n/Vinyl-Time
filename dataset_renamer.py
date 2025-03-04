import os

def rename_images(folder_path, date_prefix="01-03-2025"):
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' not found.")
        return
    
    # Get all image files (common image extensions)
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    images = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in image_extensions]
    
    # Sort images to ensure consistent renaming
    images.sort()
    
    # Rename images
    for index, image in enumerate(images, start=1):
        ext = os.path.splitext(image)[1]  # Get file extension
        new_name = f"{date_prefix} {index}{ext}"  # New name format
        old_path = os.path.join(folder_path, image)
        new_path = os.path.join(folder_path, new_name)
        
        os.rename(old_path, new_path)
        print(f"Renamed: {image} -> {new_name}")
    
    print("Renaming complete.")

# Run the function
rename_images("/Users/naganandana/Desktop/CODE/Vinyl-Time/dataset")
