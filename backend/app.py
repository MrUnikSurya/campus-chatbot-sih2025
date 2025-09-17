import json
from flask import Flask, request, jsonify, render_template
import re

# Initialize the Flask application
app = Flask(__name__, template_folder="../frontend")

# Load the FAQ data from the JSON file
try:
    with open('backend/faq.json', 'r', encoding='utf-8') as f:
        faq_data = json.load(f)
except FileNotFoundError:
    print("Error: faq.json not found. Please create the file.")
    faq_data = []

def is_hindi(text):
    """
    Checks if the text contains Hindi (Devanagari) characters.
    """
    return bool(re.search('[\u0900-\u097F]', text))

def get_bot_response(user_message):
    """
    Finds a response from the FAQ data based on the user's message
    and returns the reply in the appropriate language.
    """
    # Clean the user's message and convert to lowercase
    message = user_message.lower().strip()
    
    # Determine the user's language
    is_user_hindi = is_hindi(user_message)

    for item in faq_data:
        for pattern in item['patterns']:
            # Convert pattern to lowercase for case-insensitive matching
            # Use '==' for exact matches like greetings and thanks
            if pattern.lower() == message:
                if is_user_hindi and 'response_hindi' in item:
                    return item['response_hindi']
                # Check for English greetings/thanks and return the English response
                elif not is_user_hindi and 'response' in item:
                    return item['response']
            # Use 'in' for matching keywords within a longer question
            elif pattern.lower() in message:
                if is_user_hindi and 'response_hindi' in item:
                    return item['response_hindi']
                return item['response']
    
    # Default response if no match is found
    if is_user_hindi:
        return "मुझे क्षमा करें, मैं यह समझ नहीं पाया। क्या आप कृपया इसे दूसरे शब्दों में कह सकते हैं?"
    return "I'm sorry, I don't understand that. Can you please rephrase?"

@app.route('/')
def index():
    """
    Serves the main HTML page of the chatbot.
    """
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles the chat message from the user and returns the bot's reply.
    """
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    bot_reply = get_bot_response(user_message)
    return jsonify({'reply': bot_reply})

if __name__ == '__main__':
    app.run(debug=True)