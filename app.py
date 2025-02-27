from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
import os

app = Flask(__name__)

# Serve the HTML page
@app.route('/')
def index():
    return open('index.html').read()

# Rearrange PDF pages
@app.route('/rearrange-pdf', methods=['POST'])
def rearrange_pdf():
    if 'pdf' not in request.files:
        return "No PDF file was uploaded.", 400

    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return "No file selected.", 400

    # Extract the original filename
    original_filename = pdf_file.filename
    name, ext = os.path.splitext(original_filename)  # Split name and extension
    new_filename = f"{name}_copy{ext}"  # Add "_copy" to the filename

    # Read the original PDF
    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    total_pages = len(reader.pages)

    # Rearrange pages in groups of 4
    for i in range(0, total_pages, 4):
        group = list(range(i, min(i + 4, total_pages)))  # Get a group of 4 pages
        reordered_group = [group[j] for j in [0, 2, 3, 1] if j < len(group)]  # Rearrange as (1, 3, 4, 2)
        for page_num in reordered_group:
            writer.add_page(reader.pages[page_num])

    # Save the new PDF
    output_path = os.path.join(os.getcwd(), new_filename)
    with open(output_path, "wb") as output_pdf:
        writer.write(output_pdf)

    # Send the new file to the user
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)