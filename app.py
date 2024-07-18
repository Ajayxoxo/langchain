import streamlit as st
import cohere
import json

# Initialize the Cohere client with your API key
co = cohere.Client('DWYlDQorZ6fUuT2Hfzh02vlWdWML0l6jXLuUhFVX')

def extract_expense_info(user_input):
    prompt = f"Extract the amount, payee, and purpose from this input: {user_input}. Format the response as a JSON object with keys 'amount', 'payee', and 'purpose'."
    
    response = co.generate(
        model='command-xlarge-nightly',  # You can choose the appropriate model
        prompt=prompt,
        max_tokens=100,
        temperature=0.5,
        stop_sequences=["}"]
    )
    
    # Extract the text
    result = response.generations[0].text.strip()

    # Clean up the response to remove triple backticks
    result = result.replace("```json", "").replace("```", "").strip()

    # Attempt to parse the response as JSON
    try:
        expense_info = json.loads(result)
    except json.JSONDecodeError:
        expense_info = {"error": "Could not parse response"}
    
    return expense_info

# Streamlit interface
st.title('Expense Information Extractor')

user_input = st.text_area("Enter your text here:", "its rahul's birthday and we are splitting the bill amoung four people the total amount is 800")

if st.button('Extract Information'):
    expense_info = extract_expense_info(user_input)
    st.json(expense_info)  # Display the result in JSON format
