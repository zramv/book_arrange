from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter, PageObject
import os
import io

app = Flask(__name__)

@app.route('/')
def index():
    return open('index.html').read()

@app.route('/rearrange-cut-stack', methods=['POST'])
def rearrange_cut_stack():
    if 'pdf' not in request.files:
        return "No PDF file was uploaded.", 400

    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return "No file selected.", 400

    original_filename = pdf_file.filename
    name, ext = os.path.splitext(original_filename)
    new_filename = f"{name}_CutAndStack{ext}"

    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    # 1. Extract all original pages
    all_pages = [reader.pages[i] for i in range(len(reader.pages))]
    total_pages = len(all_pages)

    # 2. Pad to a multiple of 4 with blank pages
    # This is required so the front/back duplexing doesn't misalign
    remainder = total_pages % 4
    if remainder != 0:
        pages_to_add = 4 - remainder
        # Get dimensions of the first page to make matching blanks
        width = all_pages[0].mediabox.width
        height = all_pages[0].mediabox.height
        
        for _ in range(pages_to_add):
            blank = PageObject.create_blank_page(width=width, height=height)
            all_pages.append(blank)
            
    # Update total count and find the halfway point
    N = len(all_pages)
    H = N // 2 

    # 3. Reorder for Cut and Stack (Duplex)
    # Sequence pattern: [Front Left, Front Right], [Back Left, Back Right]
    reordered_pages = []
    
    for i in range(0, H, 2):
        # Front side of the physical sheet
        reordered_pages.append(all_pages[i])         # Left side (e.g., 1)
        reordered_pages.append(all_pages[H + i])     # Right side (e.g., 51)
        
        # Back side of the physical sheet (FLIPPED for duplexing!)
        reordered_pages.append(all_pages[H + i + 1]) # Left side (e.g., 52)
        reordered_pages.append(all_pages[i + 1])     # Right side (e.g., 2)

    # Add the newly ordered pages to the writer
    for page in reordered_pages:
        writer.add_page(page)

    # 4. Save and send in-memory
    memory_file = io.BytesIO()
    writer.write(memory_file)
    memory_file.seek(0)

    return send_file(
        memory_file, 
        as_attachment=True, 
        download_name=new_filename,
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
