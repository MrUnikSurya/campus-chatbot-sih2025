import json
from flask import Flask, request, jsonify, render_template

# Initialize the Flask application
app = Flask(__name__, template_folder="../frontend")

# Load the FAQ data from the JSON file
# Use encoding='utf-8' to support characters like 'नमस्ते'
try:
    with open('backend/faq.json', 'r', encoding='utf-8') as f:
        faq_data = json.load(f)
except FileNotFoundError:
    print("Error: faq.json not found. Please create the file.")
    faq_data = []

def get_bot_response(user_message):
    """
    Finds a response from the FAQ data based on the user's message.
    """
    # Clean and convert the user's message to lowercase
    message = user_message.lower().strip()

    for item in faq_data:
        # Check if any pattern in the list matches the user's message
        for pattern in item['patterns']:
            if pattern.lower() in message:
                return item['response']
    
    # If no match is found, return a default response
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
    # Get the message from the POST request's JSON body
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Get the bot's response
    bot_reply = get_bot_response(user_message)

    # Return the response as JSON
    return jsonify({'reply': bot_reply})

if __name__ == '__main__':
    # Run the Flask app
    # debug=True allows you to see errors and automatically reloads the server on changes
    app.run(debug=True)