from flask import Flask, render_template, request, redirect, jsonify, make_response
from werkzeug.utils import secure_filename
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

if __name__ == '__main__':    
    app.run(host='127.0.0.1', port=5000, debug=True)

@app.route('/', methods=['GET'])
def home():
	return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
	
	if request.method == 'POST':
		f = request.files['file']
		f.save('static/images/' + secure_filename(f.content_type).replace('_','.'))
	return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 