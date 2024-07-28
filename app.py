import streamlit as st
import cohere
import json
import pytesseract
from PIL import Image
import io
import speech_recognition as sr
from pytesseract import TesseractNotFoundError

# Initialize the Cohere client with your API key
co = cohere.Client('YOUR_COHERE_API_KEY')

# Function to extract text from image
def extract_text_from_image(image):
    try:
        text = pytesseract.image_to_string(image)
        return text
    except TesseractNotFoundError:
        st.error("Tesseract OCR is not installed. Please install it and try again.")
        return None

# Function to extract transaction info from text
def extract_transaction_info(text):
    response = co.generate(
        model='command-xlarge-2023-07-21',
        prompt=f"Extract transaction details from the following text:\n{text}",
        max_tokens=100
    )
    return json.loads(response.generations[0].text.strip())

# Function for speech to text conversion
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("Could not understand audio")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# Function for secret feature activation
def activate_secret_features():
    st.write("Secret features activated!")
    # Add additional secret features here
    st.write("Secret Feature 1: Additional analysis enabled.")
    st.write("Secret Feature 2: Enhanced data visualization enabled.")

# Streamlit app layout
st.title("Expense Tracker App")

input_method = st.radio("Choose input method:", ('Text', 'Image', 'Speech'))

if input_method == 'Text':
    user_input = st.text_area("Enter the transaction details:")
    if st.button('Submit'):
        transaction_info = extract_transaction_info(user_input)
        st.json(transaction_info)

elif input_method == 'Image':
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        st.write("")
        st.write("Extracting text from image...")
        extracted_text = extract_text_from_image(image)
        if extracted_text:
            st.write("Extracted Text:", extracted_text)
            transaction_info = extract_transaction_info(extracted_text)
            st.json(transaction_info)

elif input_method == 'Speech':
    if st.button('Start Speech Input'):
        text = speech_to_text()
        if text:
            st.write("You said:", text)
            if "hey butler enable secret mode" in text.lower():
                activate_secret_features()
            else:
                transaction_info = extract_transaction_info(text)
                st.json(transaction_info)

# Display error message for missing Tesseract OCR
if st.button('Check Tesseract Installation'):
    try:
        pytesseract.get_tesseract_version()
        st.success("Tesseract OCR is installed.")
    except TesseractNotFoundError:
        st.error("Tesseract OCR is not installed. Please install it and try again.")
