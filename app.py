import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
import os
from PIL import Image

# --- CROSS-PLATFORM CHECK ---
if os.name == 'nt':  # 'nt' means Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def detect_currency(text):
    """Scans text to auto-detect currency. Defaults to ₹ for India, falls back to $."""
    if re.search(r'(₹|Rs\.?|INR|Rupees)', text, re.IGNORECASE):
        return "₹"
    elif re.search(r'(€|EUR)', text, re.IGNORECASE):
        return "€"
    elif re.search(r'(£|GBP)', text, re.IGNORECASE):
        return "£"
    elif re.search(r'(\$|USD)', text, re.IGNORECASE):
        return "$"
    return "₹"  # Making Rupees your smart default!

def extract_line_items(text):
    """Splits text line-by-line to isolate individual products and their prices."""
    items = []
    exclude_keywords = ['total', 'subtotal', 'tax', 'cgst', 'sgst', 'gst', 'cash', 'change', 'balance', 'amount', 'net']
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for patterns like "Item Name 120.50"
        match = re.search(r'(.*?)\s+([0-9,]+\.\d{2})', line)
        if match:
            item_name = match.group(1).strip()
            price_val = float(match.group(2).replace(',', ''))
            
            clean_name = re.sub(r'[^\w\s\-\.]', '', item_name).strip()
            
            if clean_name and len(clean_name) > 2:
                if not any(kw in clean_name.lower() for kw in exclude_keywords):
                    items.append((clean_name, price_val))
    return items

def extract_total_amount(text):
    """Hunts for monetary values in the text and guesses the grand total."""
    amounts = re.findall(r'[0-9,]+\.\d{2}', text)
    if amounts:
        floats = [float(amount.replace(',', '')) for amount in amounts]
        return max(floats)
    return None

# --- STREAMLIT PIGGY BANK INTERFACE ---
st.title("🧾 Smart Multi-Receipt Reader")
st.write("Drop multiple bills here at once! I'll read currencies and break down product prices line-by-line.")

# accept_multiple_files=True allows dropping many files at once
uploaded_files = st.file_uploader("Choose receipt images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files):
        st.write("---")
        st.markdown(f"### 📄 Receipt {idx + 1}: *{uploaded_file.name}*")
        
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
        
        with st.spinner(f"AI is calculating data for Receipt {idx + 1}... 🧠"):
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            extracted_text = pytesseract.image_to_string(opencv_image)
            
            currency = detect_currency(extracted_text)
            products = extract_line_items(extracted_text)
            total = extract_total_amount(extracted_text)
            
        st.success(f"Analysis Complete for Receipt {idx + 1}!")
        
        if total:
            st.metric(label="💰 Calculated Grand Total", value=f"{currency}{total:.2f}")
        else:
            st.warning("Could not clearly track a grand total number.")
            
        st.markdown("#### 🛒 Detected Item Prices:")
        if products:
            for item, price in products:
                st.write(f"🔹 **{item}**: {currency}{price:.2f}")
        else:
            st.info("No individual product price patterns isolated. Review raw text details below.")
            
        with st.expander(f"See raw OCR text found for {uploaded_file.name}"):
            st.text(extracted_text)