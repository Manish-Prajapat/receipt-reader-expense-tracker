import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
from PIL import Image

if os.name == 'nt':  # 'nt' means Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_total_amount(text):
    """Hunts for monetary values in the text and guesses the total."""
    # Find all decimal numbers like 10.99, 5.00, 125.50
    amounts = re.findall(r'\d+\.\d{2}', text)
    
    if amounts:
        # Convert text numbers into real numbers we can compare
        floats = [float(amount) for amount in amounts]
        # The largest number on a receipt is almost always the grand total!
        return max(floats)
    return None

# --- STREAMLIT PIGGY BANK INTERFACE ---
st.title("🧾 Smart Receipt Reader")
st.write("Upload a picture of your receipt, and I'll find out how much you spent!")

# Create a file uploader box
uploaded_file = st.file_uploader("Choose a receipt image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 1. Display the uploaded image so the user can see it
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Uploaded Receipt", use_container_width=True)
    
    with st.spinner("The robot is reading your receipt... 🧠"):
        # 2. Convert image so OpenCV and Tesseract can understand it
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 3. Read the text from the image
        extracted_text = pytesseract.image_to_string(opencv_image)
        
        # 4. Extract the final amount
        total = extract_total_amount(extracted_text)
        
    # --- DISPLAY RESULTS ---
    st.success("Reading complete!")
    
    if total:
        st.metric(label="💰 Estimated Total Spent", value=f"${total:.2f}")
    else:
        st.warning("Hmm, I couldn't clearly see a total amount. Try a clearer picture!")
        
    # Optional: Show the raw text if you want to see what the robot saw
    with st.expander("See raw text found by the robot"):
        st.text(extracted_text)