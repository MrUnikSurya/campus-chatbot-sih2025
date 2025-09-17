# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS  # optional if serving frontend separately

app = Flask(__name__)
CORS(app)  # remove if serving files from same origin

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_msg = data.get('message', '')
    # Replace with your real chatbot logic
    bot_reply = f"Echo: {user_msg}"
    return jsonify(reply=bot_reply)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
