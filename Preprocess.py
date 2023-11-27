import os
from PIL import Image, ImageEnhance
import numpy as np
import cv2
import fitz  # PyMuPDF

def preprocess_image(image_path, output_folder):
    # Open the image
    img = Image.open(image_path)

    # Straighten the image
    img_array = np.array(img)
    img_array = straighten_image(img_array)
    img = Image.fromarray(img_array)

    # Convert to grayscale
    img = img.convert('L')

    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)

    # Save the preprocessed image
    output_path = os.path.join(output_folder, os.path.basename(image_path))
    img.save(output_path)
    return output_path

def straighten_image(image_array):
    # Convert to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply edge detection using Canny
    edges = cv2.Canny(blurred, 50, 150)

    # Find lines using Hough Transform
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

    # Find the angle of the most dominant line
    angles = [angle for rho, angle in lines[:, 0]]
    dominant_angle = np.median(angles)

    # Rotate the image to straighten it
    rotated = Image.fromarray(image_array).rotate(-np.degrees(dominant_angle))

    return np.array(rotated)

def preprocess_pdf(pdf_path, output_folder):
    # Create an output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Iterate over each page in the PDF
    for page_number in range(pdf_document.page_count):
        # Get the page
        page = pdf_document[page_number]

        # Get the image of the page (render as image)
        image_list = page.get_pixmap()
        image = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)

        # Preprocess the image
        preprocessed_image_path = preprocess_image(image, output_folder)

        # Replace the image in the PDF with the preprocessed image
        page.set_pixmap(fitz.Pixmap(preprocessed_image_path))

    # Save the preprocessed PDF
    output_path = os.path.join(output_folder, os.path.basename(pdf_path))
    pdf_document.save(output_path)
    pdf_document.close()

    return output_path

def main(input_folder, output_folder):
    # Process each file in the input folder
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        # Check if the file is an image (supported image formats: PNG, JPEG, GIF, BMP)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            preprocess_image(file_path, output_folder)
            print(f"Image {filename} preprocessed.")

        # Check if the file is a PDF
        elif filename.lower().endswith('.pdf'):
            preprocess_pdf(file_path, output_folder)
            print(f"PDF {filename} preprocessed.")

        else:
            print(f"Unsupported file type: {filename}")

if __name__ == "__main__":
    input_folder = "D:\Downloads\DocPreprocessIN"
    output_folder = "D:\Downloads\DocPreprocessOUT"
    main(input_folder, output_folder)