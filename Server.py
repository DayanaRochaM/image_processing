from flask import Flask, render_template, request, redirect, jsonify, make_response
from os import listdir, remove
from os.path import isfile, join
import image_processing as pi
from werkzeug.utils import secure_filename
import json
#from flask_cors import CORS
'''
REGRAS DA APLICAÇÃO:

Para cada efeito haverá duas pastas: Antes e depois. Assim, teremos
o controle sobre o do e undo. 

Instalacoes pro image_processing: 
	conda install -c conda-forge imread
	pip install Pillow
'''

app = Flask(__name__)
path = "static/images/original/"
filters_list = ["negative", "log", "power"]
#CORS(app)  

if __name__ == '__main__':    
    app.run(host='127.0.0.1', port=5000, debug=True)

#Excluindo arquivos para deixar apenas o desejado
def cleaningFolder(dire):
	files = listdir(dire)
	for file in files:
		remove(path + file)

@app.route('/', methods=['GET'])
def home():
	return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
	
	if request.method == 'POST':

		file = request.files['file']
		cleaningFolder(path)	
		f = pi.transformImage(file)

		# Salvando arquivo
		complete_path = path + secure_filename(file.content_type).replace('_','.')
		pi.saveImage(complete_path, f) 
		#f.save(path + secure_filename(f.content_type).replace('_','.'))

	return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

# Aqui será a parte de gestao de filtros aplicados.
# A ideia é receber apenas uma string e aqui decidir o que aplicar.
@app.route('/apply_filter', methods=['POST'])
def apply_filter():
	
	# Pegando nome do arquivo
	files = listdir(path)
	if request.method == 'POST' and len(files) == 1:

		file = files[0]
		print(file)

		filter_ = request.form['filter']
		if filter_ in filters_list:

			print(filter_)
			filename = file.replace('_','.')
			complete_filename = path + filename
			img_matrix = pi.readImage(complete_filename)

			if filter_ == 'negative':
				img_matrix = pi.filterNegative(img_matrix)

			elif filter_ == 'log':
				img_matrix = pi.filterContrastLog(img_matrix)

			elif filter_ == 'power':
				img_matrix = pi.filterContrastPow(img_matrix)

			cleaningFolder(path)

			# Salvando arquivo
			complete_path = path + filename
			pi.saveImage(complete_path, img_matrix) 
			#f.save('static/images/original/' + secure_filename(f.content_type).replace('_','.'))

		return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

	else:
		return json.dumps({'success':False}), 500, {'ContentType':'application/json'} 
























