"""
Quick script to save the base64 CV to Downloads folder
Run this after generating a CV through Claude Desktop
"""

import base64
import os
from pathlib import Path

# Paste the base64 string from Claude's response here
PDF_BASE64 = """
PASTE_BASE64_HERE
"""

def save_cv():
    # Get Downloads folder
    downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    # Create cv-generator folder
    cv_folder = os.path.join(downloads, 'cv-generator')
    os.makedirs(cv_folder, exist_ok=True)
    
    # Decode base64
    pdf_data = base64.b64decode(PDF_BASE64.strip())
    
    # Save with timestamp
    import time
    timestamp = int(time.time())
    filename = f"cv_{timestamp}.pdf"
    filepath = os.path.join(cv_folder, filename)
    
    with open(filepath, 'wb') as f:
        f.write(pdf_data)
    
    print(f"✅ CV saved to: {filepath}")
    print(f"📂 Open folder: {cv_folder}")
    
    # Try to open the folder
    import platform
    if platform.system() == 'Windows':
        os.startfile(cv_folder)
    elif platform.system() == 'Darwin':
        os.system(f'open "{cv_folder}"')
    else:
        os.system(f'xdg-open "{cv_folder}"')

if __name__ == '__main__':
    if 'PASTE_BASE64_HERE' in PDF_BASE64:
        print("❌ Please paste the base64 string from Claude's response into this script first!")
        print("   Look for 'pdfBase64' field in the CV generation response")
    else:
        save_cv()
