# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse
from .forms import PosterForm
import cv2
import math
import numpy as np
import zipfile
import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings


def segmenting(image, segment_width, segment_height):
    """
    Function to segment the resized image into A4 size sections.
    Will iterate over the rows and columns of the image and box
    off each A4 sized segment. The segments will then be stored 
    in a list.
    segment_width and segment_height will be calculated in pixels.
    """
    segments = [] # List to store segments
    height, width, _ = image.shape    # Original image dimensions
                                      # image.shape returns a tuple
                                      # the _ ignores the third element
    segment_height = max(1, segment_height)
    segment_width = max(1, segment_width)

    for y in range(0, height, segment_height):
        for x in range(0, width, segment_width):
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

def poster_view(request):
    if request.method == 'POST':
        form = PosterForm(request.POST, request.FILES)
        if form.is_valid():
            # Getting data from the form
            # for user inputted values
            #new_width = form.cleaned_data['width']
            #new_height = form.cleaned_data['height']
            image_file = form.cleaned_data['image']
            dpi_new = form.cleaned_data['dpi_new']
            
            # With predefined sizes chosen by user
            size_choice = form.cleaned_data['size_choice']
            # Allocate dimensions to size choice
            if size_choice == 'small':
                new_width, new_height = 420, 594 # 2 sheets × 2 sheets
            elif size_choice == 'medium':
                new_width, new_height = 630, 891 # 3 sheets × 3 sheets
            elif size_choice == 'large':
                new_width, new_height = 880, 1188 # 4 sheets × 4 sheets


            # Reading the uploaded image to an array
            # This is necessary because file is in-memory byte stream
            # imdecode() decodes bytes into an image in BGR format
            image_np = np.frombuffer(image_file.read(), np.uint8)
            Original = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            # Convert from BGR to RGB format
           #Original_RGB = cv2.cvtColor(Original, cv2.COLOR_BGR2RGB)
            
            # Error message
            if Original is None:
                print("Error loading image. Check file path is correct.")
                return render(request, 'poster_generator/create_poster.html', {'form': form, 'error': 'Error loading image.'})
            
            # Convert dimensions from millimeters to pixels
            new_width_pix = round((210 / 25.4) * dpi_new)
            new_height_pix = round((297 / 25.4) * dpi_new)

            # Calculate the number of A4 sheets high and wide for the poster
            sheets_wide = round(new_width / 210)
            sheets_high = round(new_height / 297)

            # A4 segment size in pixels
            A4_width_pix = round((210 / 25.4) * dpi_new)
            A4_height_pix = round((297 / 25.4) * dpi_new)

            # Total number of pixels for poster width and height
            new_width_pix = A4_width_pix * sheets_wide
            new_height_pix = A4_height_pix * sheets_high

            # Scale up the image
            Poster = cv2.resize(Original, (new_width_pix, new_height_pix),
                        interpolation= cv2.INTER_CUBIC)
            Poster_RGB = cv2.cvtColor(Poster, cv2.COLOR_BGR2RGB)
            # Call segmenting() to segment the poster
            segments = segmenting(Poster, A4_width_pix, A4_height_pix)

            # Create a zip file
            # BytesIO() creates a zip file in memory, so files not stored on disk
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for i, seg in enumerate(segments):
                    seg_RGB = cv2.cvtColor(seg, cv2.COLOR_BGR2RGB) # Convert back to RGB
                    # Save segments to temporary in memory file
                    """_, img_encoded = cv2.imencode('.png', seg_RGB)
                    segment_data = img_encoded.tobytes()"""

                    # convert from array to PIL image
                    pil_img = Image.fromarray(seg_RGB)
                    # save image to in-memory bytes buffer
                    byte_arr = BytesIO()
                    pil_img.save(byte_arr, format= 'PNG')

                    # Add to the zip file
                    zip_file.writestr(f'Segment_{i+1}.png', byte_arr.getvalue())
            #zip_buffer.seek(0)
            #zip_content = ContentFile(zip_buffer.read(), name = 'poster_segments.zip')
            #zip_url = f"{settings.MEDIA_URL}poster_segments.zip"
            zip_path = os.path.join(settings.MEDIA_ROOT, 'poster_segments.zip')
            with open(zip_path, 'wb') as f:
                f.write(zip_buffer.getvalue())

            zip_url = settings.MEDIA_URL + 'poster_segments.zip'
            """
            # Downloadable response will be the zip file
            #response = HttpResponse (zip_buffer, content_type = 'application/zip')
            #response['Content-Disposition'] = 'attachment; filename="poster_segmants.zip"'
            #return response 
            """

            return render(request, 'poster_generator/success.html', {'zip_url': zip_url})

    else:
        form = PosterForm()

    return render(request, 'poster_generator/create_poster.html', {'form': form})

"""# Save segments
save_path = os.path.join(settings.MEDIA_ROOT, 'poster_segments') # Segments go to a subdirectory
# Create the directory if it doesn't exist
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Save the segments
segment_urls = []
try:
    for i, seg in enumerate(segments):
        seg_RGB = cv2.cvtColor(seg, cv2.COLOR_BGR2RGB) # Convert back to R
        saving = os.path.join(save_path, f'Segment_{i+1}.png')
        success = cv2.imwrite(saving, seg)
        if success:
            # Append url to list if the segment successfully saved
            segment_urls.append(f"{settings.MEDIA_URL}poster_segments/Segment_{i+1}.png")
        else:
            print(f'Error saving segment {i+1}')

except Exception as e:
    print(f"Error processing segment {i+1}: {e}")

# Generate URLs for accessing saved segments
return render(request, 'poster_generator/success.html', {'segment_urls': segment_urls})"""
        
    
