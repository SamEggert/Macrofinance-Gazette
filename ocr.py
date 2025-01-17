import glob
import os
import time
from tqdm import tqdm
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
def main():
    # Configure Tesseract to use Italian
    custom_config = r'--oem 3 --psm 6 -l ita'

    # Iterate over all PDFs in the gazette_archives directory
    total = len(glob.glob("gazette_archives/*.pdf"))
    for file in tqdm(glob.iglob("gazette_archives/*.pdf"), total=total, desc="Processing PDFs"):
        start_time = time.time()

        # Convert the first page of the PDF to an image
        pages = convert_from_path(file)
        first_page = pages[0]

        # Extract text
        text = pytesseract.image_to_string(first_page, config=custom_config)

        # Save the extracted text to a file
        filename = os.path.basename(file).replace(".pdf", ".txt")
        with open(os.path.join("gazette_archives", filename), "w") as f:
            f.write(text)

        print(f"Processed {file} in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
