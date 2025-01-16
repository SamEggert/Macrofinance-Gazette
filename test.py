import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# Convert the first page of the PDF to an image
pages = convert_from_path('test.pdf')
first_page = pages[0]

# Configure Tesseract to use Italian
custom_config = r'--oem 3 --psm 6 -l ita'

# Extract text
text = pytesseract.image_to_string(first_page, config=custom_config)

# Print first 500 characters to see what we got
print("First 500 characters of extracted text:")
print(text[:500])

# Also print Tesseract version to confirm we're on v5
print("\nTesseract Version:")
print(pytesseract.get_tesseract_version())