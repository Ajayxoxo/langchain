import streamlit as st
import cohere
import json
import pytesseract
from PIL import Image
import io
from pytesseract import TesseractNotFoundError

# Initialize the Cohere client with your API key
co = cohere.Client('DWYlDQorZ6fUuT2Hfzh02vlWdWML0l6jXLuUhFVX')

def extract_transaction_info(user_input):
    prompt = f"""
    Extract the following information from this input: '{user_input}'
    - Transaction type (income or expense)
    - Total amount
    - Number of people involved (if splitting)
    - Payee or payer
    - Purpose of transaction
    - Amount per person (if splitting)
    Format the response as a JSON object with keys 'type', 'total_amount', 'num_people', 'payee_or_payer', 'purpose', and 'amount_per_person'.
    If it's not a split transaction, omit 'num_people' and 'amount_per_person'.
    """
   
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=200,
        temperature=0.5,
        stop_sequences=["}"]
    )
   
    result = response.generations[0].text.strip()
    result = result.replace("```json", "").replace("```", "").strip()

    try:
        transaction_info = json.loads(result)
    except json.JSONDecodeError:
        transaction_info = {"error": "Could not parse response"}
   
    return transaction_info

def extract_text_from_image(image):
    try:
        text = pytesseract.image_to_string(image)
    except TesseractNotFoundError:
        text = "Tesseract not found. Please install Tesseract OCR."
    return text

def extract_bill_info(image):
    extracted_text = extract_text_from_image(image)
    return extract_transaction_info(extracted_text)

st.title('Transaction Information Extractor')

input_method = st.radio("Choose input method:", ('Text', 'Image'))

if input_method == 'Text':
    user_input = st.text_area("Enter your transaction details:", "its rahul's birthday and we are splitting the bill among four people the total amount is 800")

    if st.button('Extract Information'):
        if "hey butler enable secret mode" in user_input.lower():
            st.success("Secret mode activated! Additional features unlocked.")
            # Add your secret feature functionality here

        transaction_info = extract_transaction_info(user_input)
        st.json(transaction_info)

else:  # Image input
    uploaded_file = st.file_uploader("Choose a bill image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        if st.button('Extract Bill Information'):
            with st.spinner('Analyzing bill...'):
                bill_info = extract_bill_info(image)
                st.json(bill_info)
