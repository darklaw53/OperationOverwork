import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

# Set the path to the Tesseract executable (change this according to your installation)
pytesseract.pytesseract.tesseract_cmd = r'D:\Onedrive\Documentos\Tesseract\tesseract.exe'

def extract_text_from_pdf_or_image(file_path, output_folder):
    # Create an output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Determine the file type
    file_extension = os.path.splitext(file_path)[1].lower()

    # Process PDF file
    if file_extension == '.pdf':
        # Open the PDF file
        pdf_document = fitz.open(file_path)

        # Iterate over each page in the PDF
        for page_number in range(pdf_document.page_count):
            # Get the page
            page = pdf_document[page_number]

            # Get the image of the page (render as image)
            image_list = page.get_pixmap()
            image = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)

            # Perform OCR on the image
            extracted_text = pytesseract.image_to_string(image, lang='eng')

            # Save the extracted text to a text file
            text_output_path = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(file_path))[0]}_page_{page_number + 1}.txt')
            with open(text_output_path, 'w', encoding='utf-8') as text_file:
                text_file.write(extracted_text)

        # Close the PDF document
        pdf_document.close()

    # Process image file
    elif file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        # Perform OCR on the image
        img = Image.open(file_path)
        extracted_text = pytesseract.image_to_string(img, lang='eng')

        # Save the extracted text to a text file
        text_output_path = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(file_path))[0]}.txt')
        with open(text_output_path, 'w', encoding='utf-8') as text_file:
            text_file.write(extracted_text)

    else:
        print(f"Unsupported file type: {file_extension}")

def process_pdfs(input_folder, output_folder):
    # Iterate over each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            extract_text_from_pdf_or_image(pdf_path, output_folder)

if __name__ == "__main__":
    # Specify the input and output folders
    input_folder_path = r'D:\Downloads\ImagesToRead'
    output_folder_path = r'D:\Downloads\ImagesOutput'

    # Process PDFs in the input folder and save the extracted text to the output folder
    process_pdfs(input_folder_path, output_folder_path)

def extract_associations(text, relevant_word, ignored_words):
    # Split the text into lines
    lines = text.split('\n')

    # Create a dictionary to store the associations
    name_number_dict = {}

    # Iterate through each line
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check if the line contains the relevant word
        if relevant_word in line:
            # Combine with the next line if the current line only contains the relevant word
            if line == relevant_word:
                line += ' ' + lines[i + 1].strip()
                i += 1

            # Find the first non-empty line above the current line that does not contain an ignored word or numbers
            j = i - 1
            while j >= 0 and (lines[j].strip() == '' or any(word in lines[j] for word in ignored_words) or any(char.isdigit() for char in lines[j])):
                j -= 1

            # If a non-empty line is found, associate it with the current line containing the relevant word
            if j >= 0:
                name = lines[j].strip()
                number = line
                name_number_dict[name] = number

        i += 1

    return name_number_dict

def process_folder(folder_path, relevant_word, ignored_words, output_folder):
    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)

            # Read the text from the file
            with open(file_path, 'r') as file:
                text = file.read()

            # Extract associations, excluding lines with numbers
            name_number_dict = extract_associations(text, relevant_word, ignored_words)

            # Write the results to a text file in the output folder
            output_file_path = os.path.join(output_folder, f"{filename}_associations.txt")
            with open(output_file_path, 'w') as output_file:
                output_file.write("Associations:\n\n")
                for name, number in name_number_dict.items():
                    output_file.write(f"{name}:\n{number}\n\n")

            print(f"Associations for {filename} written to {output_file_path}")

def main():
    # Get user input for folder path, relevant word, ignored words, and output folder
    folder_path = input("Enter the folder path: ")
    relevant_word = input("Enter the relevant word: ")
    ignored_words_input = input("Enter a comma-separated list of ignored words (if any): ")
    ignored_words = [word.strip() for word in ignored_words_input.split(',')]
    output_folder = input("Enter the output folder path: ")

    # Process the folder
    process_folder(folder_path, relevant_word, ignored_words, output_folder)

if __name__ == "__main__":
    main()