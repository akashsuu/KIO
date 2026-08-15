import os
import glob

# Paths
IMAGE_DIR = os.path.join("kio_cat", "SIT")
OUTPUT_FILE = os.path.join("esp32_pixel_cat", "frames.h")

def image_to_c_array(file_path, array_name):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    hex_data = ', '.join([f"0x{byte:02x}" for byte in data])
    
    return f"const uint8_t {array_name}[] PROGMEM = {{ {hex_data} }};\n"

def main():
    png_files = glob.glob(os.path.join(IMAGE_DIR, "*.png"))
    # Sort files numerically
    png_files.sort(key=lambda f: int(''.join(filter(str.isdigit, os.path.basename(f))) or 0))
    
    if not png_files:
        print(f"No PNG files found in {IMAGE_DIR}")
        return

    arrays = []
    array_names = []
    
    for i, file_path in enumerate(png_files):
        array_name = f"sit_{i+1}_png"
        array_names.append(array_name)
        c_array_str = image_to_c_array(file_path, array_name)
        arrays.append(c_array_str)
        
    with open(OUTPUT_FILE, 'w') as f:
        f.write("#pragma once\n")
        f.write("#include <Arduino.h>\n\n")
        
        for array in arrays:
            f.write(array)
            f.write("\n")
            
        # Write array of pointers
        pointers = ", ".join(array_names)
        f.write(f"const uint8_t* const sit_frames[] PROGMEM = {{ {pointers} }};\n")
        
        # Write array of sizes
        sizes = ", ".join([f"sizeof({name})" for name in array_names])
        f.write(f"const size_t sit_frame_sizes[] = {{ {sizes} }};\n")
        
        # Write number of frames
        f.write(f"const int NUM_SIT_FRAMES = {len(array_names)};\n")
        
    print(f"Successfully generated {OUTPUT_FILE} with {len(array_names)} frames.")

if __name__ == "__main__":
    main()
