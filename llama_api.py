from litellm import completion
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def extract_payment_info():
    try:
        question = request.json['question']
        response = completion(
                    model="ollama/llama3", 
                    messages = [{ "content": question}], 
                    api_base="http://localhost:11434"
        )
        return jsonify({'response': response.choices[0]["message"]["content"]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=9000, host='0.0.0.0')