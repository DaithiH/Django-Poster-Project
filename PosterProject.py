import numpy as np 
print(np.__version__)
from matplotlib import pyplot as plt 
import cv2 
from PIL import Image as PILImg 
from IPython.display import Image, display  
import math
import os

pic_path = r'C:\Users\daveh\Pictures\Butterfly.jpg' # Local path to image
image_in = Image(filename= pic_path)
# filename is a class constructor argument in IPython.display Image library
img = PILImg.open(pic_path)
#img.show()
Original = cv2.imread(pic_path) # Saves the image as a multidimensional array
#print(Original)

"""
The following is just to clarify that the image has been 
loaded and stored as the 'Original' variable.
Has nothing to do with the functionality of the program

print(Original) # Prints the array values 
                 # BGR values not RGB

# Display the stored image with Matplotlib pyplot
plt.imshow(Original)
plt.axis('off')
plt.show() 
# Image is shown with colours distorted
# cv2 reads and stores the image in BGR format, not RGB 
# The resulting image can be pretty cool though 
"""

## Segmenting Function ##

def segmenting(image, segment_width, segment_height):
    """
    Function to segment the resized image into A4 size sections.
    Will iterate over the rows and columns of the image and box
    off each A4 sized segment. The segments will then be stored 
    in a list.
    segment_width and segment_height will be calculated in pixels.
    """
    print("Entering segmenting function")
    segments = [] # List to store segments
    height, width, _ = image.shape    # Original image dimensions
                                      # image.shape returns a tuple
                                      # the _ ignores the third element
    segment_height = max(1, segment_height)
    segment_width = max(1, segment_width)

    print("entering for loop")
    for y in range(0, height, segment_height):
        for x in range(0, width, segment_width):
            print(f"Processing segment at x: {x}, y: {y}")
            # Define segment boundry to avoid overshooting poster dimensions
            # Crop if overshooting
            seg_x_end = min(x + segment_width, width)
            seg_y_end = min(y + segment_height, height)
            # Pad the edge with blank space if segment is landing short
            # of the poster edge. This is to avoid segment mismatches
            # Create a blank segment of the correct size
            seg_padded = np.zeros((segment_height, segment_width, 3), dtype = np.uint8)
            # Tuple of height, width, channels. dtype uint8 for pixels: 0 - 255
            segment = image[y : seg_y_end, x : seg_x_end]
            # vertical, (y : seg_y_end), and horizontal, (x : seg_x_end), ranges for iteration
            #print(f'seg shape:{segment.shape}') # This is only for testing
            seg_padded[:segment.shape[0], :segment.shape[1]] = segment
            # Copies all elements of the segment into the blank segment
            # If the segment is smaller, the remaining positions will just be left blank
            # Will result in all segments being the correct size
            #print(f'seg_padded shape: {seg_padded.shape}') # This is only for testing
            segments.append(seg_padded)

    return segments
    

def main(Image_in, new_width, new_height, dpi_new, save_path):
    """
    Image_in as path, new_width and new_height of poster in milimeters
    dpi_new: dots per inch for the resized poster
    save_path where the poster will be saved as a file of A4 size sections
    """
    #pic_path = r'C:\Users\daveh\Pictures\Butterfly.jpg' # Local path to image

    Image_in = cv2.imread(pic_path)
    if Image_in is None:
        print("Error loading image. Check file path is correct.")
        return

    Image_RGB = cv2.cvtColor(Image_in, cv2.COLOR_BGR2RGB)
    # Display image to verify colour conversion (Optional)
    # plt.imshow(Image_RGB)
    # plt.axis('off')
    # plt.show(block= False)

    # Convert width and height from millimeters to pixels
    # Need to convert to inches for dpi value
    # new_width_pix = math.floor(new_width/25.4 * dpi_new)
    # new_height_pix = math.floor(new_height/25.4 * dpi_new)
    new_width_pix = round(new_width/25.4 * dpi_new)
    new_height_pix = round(new_height/25.4 * dpi_new)


    # A4 segment size in pixels
    # A4 size is 210mm × 297mm
    # A4_width_pix = math.floor((210/25.4) * dpi_new)
    # A4_height_pix = math.floor((297/25.4) * dpi_new)
    A4_width_pix = round((210/25.4) * dpi_new)
    A4_height_pix = round((297/25.4) * dpi_new)

    sheets_wide = round(new_width / 210)
    sheets_high = round(new_height / 297)

    new_width_pix = A4_width_pix * sheets_wide
    new_height_pix = A4_height_pix * sheets_high

    # Scale up the image
    
    Poster = cv2.resize(Image_RGB, (new_width_pix, new_height_pix),
                        interpolation= cv2.INTER_CUBIC)
    # Display poster image and shape (Optional)
    print("Poster image")
    plt.imshow(Poster)
    plt.axis('off')
    plt.show(block= False) 
    print(f'Poster shape: {Poster.shape}')


    # Call segmenting() to segment the poster
    segments = segmenting(Poster, A4_width_pix, A4_height_pix)

    # Save Poster segments
    # Loop over segments list and save to destination folder
    # Also necessary to convert back to RGB again 
    print("entering file writing loop")
    for i, seg in enumerate(segments):
        seg_RGB = cv2.cvtColor(seg, cv2.COLOR_BGR2RGB)
        saving = os.path.join(save_path, f'Section_{i+1}.png')
        success = cv2.imwrite(saving, seg_RGB)
        if not success:
            print(f'Error saving segment {i+1}')


if __name__ == "__main__":
    pic_path = r'C:\Users\daveh\Pictures\Butterfly.jpg'
    dpi_new = 300  # This can be adjusted as desired
    save_path = r'C:\Users\daveh\Pictures\Poster_Segments'
    new_width = 1050 # Poster width in mm (5 sheets)
    new_height = 1188 # Poster width in mm (4 sheets)
    main(pic_path, new_width, new_height, dpi_new, save_path)



