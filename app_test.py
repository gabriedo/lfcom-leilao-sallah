from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Isso permite requisições de qualquer origem

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API está funcionando!"})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        "status": "success",
        "message": "Teste realizado com sucesso!"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 