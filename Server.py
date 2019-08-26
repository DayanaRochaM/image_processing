from flask import Flask, render_template, request, redirect, jsonify, make_response
from os import listdir
from os.path import isfile, join
from werkzeug.utils import secure_filename
import json
#from flask_cors import CORS
'''
REGRAS DA APLICAÇÃO:

Para cada efeito haverá duas pastas: Antes e depois. Assim, teremos
o controle sobre o do e undo. 
'''

app = Flask(__name__)
#CORS(app)  

if __name__ == '__main__':    
    app.run(host='127.0.0.1', port=5000, debug=True)

@app.route('/', methods=['GET'])
def home():
	return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
	
	if request.method == 'POST':
		f = request.files['file']
		f.save('static/images/original/' + secure_filename(f.content_type).replace('_','.'))
	return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

# Aqui será a parte de gestao de filtros aplicados.
# A ideia é receber apenas uma string e aqui decidir o que aplicar.
@app.route('/apply_filter', methods=['POST'])
def apply_filter():
	
	# Pegando nome do arquivo
	# path = "static/images/original/"
	# onlyfiles = listdir(path)
	# file = onlyfiles[0]
	# print(file)

	if request.method == 'POST':
		filter_ = request.form['filter']
		if filter_ == 'negative':
			print(filter_)
		#f.save('static/images/original/' + secure_filename(f.content_type).replace('_','.'))
	return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


























