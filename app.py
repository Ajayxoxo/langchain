import streamlit as st
import cohere
import json
import pytesseract
from PIL import Image
import io
from pytesseract import TesseractNotFoundError
import speech_recognition as sr
import matplotlib.pyplot as plt

# Initialize the Cohere client with your API key
co = cohere.Client('DWYlDQorZ6fUuT2Hfzh02vlWdWML0l6jXLuUhFVX')

# Sample budgets for different categories
budgets = {
    "food": 500,
    "travel": 300,
    "entertainment": 200,
    "others": 100
}

# Sample expenses categorized
categorized_expenses = {
    "food": 0,
    "travel": 0,
    "entertainment": 0,
    "others": 0
}

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
        st.error("Tesseract is not installed or it's not in your PATH. Please install Tesseract OCR and try again.")
        return None
    return text

def extract_bill_info(image):
    extracted_text = extract_text_from_image(image)
    if extracted_text is None:
        return {"error": "Failed to extract text from image."}
    return extract_transaction_info(extracted_text)

def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Say something...")
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

def activate_secret_mode():
    st.success("Secret mode activated!")
    
    # Add Personalized Budget Tracking and Expense Categorization features
    if st.button('Set Budgets'):
        st.json(budgets)
        
    if st.button('Show Categorized Expenses'):
        categorize_expenses()
        st.json(categorized_expenses)
        show_expense_chart()

def categorize_expenses():
    # Example categorization logic (you can expand this)
    for key in categorized_expenses.keys():
        categorized_expenses[key] = 0  # Reset counts

    # Add your logic to update categorized_expenses based on extracted transaction info

def show_expense_chart():
    labels = categorized_expenses.keys()
    sizes = categorized_expenses.values()
    
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    st.pyplot(fig1)

st.title('Transaction Information Extractor')

input_method = st.radio("Choose input method:", ('Text', 'Image', 'Speech'))

if input_method == 'Text':
    user_input = st.text_area("Enter your transaction details:", "its rahul's birthday and we are splitting the bill among four people the total amount is 800")

    if st.button('Extract Information'):
        transaction_info = extract_transaction_info(user_input)
        st.json(transaction_info)

elif input_method == 'Image':
    uploaded_file = st.file_uploader("Choose a bill image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        if st.button('Extract Bill Information'):
            with st.spinner('Analyzing bill...'):
                bill_info = extract_bill_info(image)
                st.json(bill_info)

elif input_method == 'Speech':
    if st.button('Start Speech Input'):
        text = speech_to_text()
        if text:
            if "hey butler enable secret mode" in text.lower():
                activate_secret_mode()
            else:
                transaction_info = extract_transaction_info(text)
                st.json(transaction_info)
