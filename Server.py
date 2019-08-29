from flask import Flask, render_template, request, redirect, jsonify, make_response
from os import listdir, remove
from os.path import isfile, join
from itertools import chain
import image_processing as pi
import utils
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
path_original = "static/images/original/"
path_actual = "static/images/actual/"
filters_list = ["negative", "log", "power"]
non_filters_list = ["non-negative", "non-log", "non-power"]
global filters_in_use 
filters_in_use = []
#CORS(app)  

if __name__ == '__main__':    
    app.run(host='127.0.0.1', port=5000, debug=True)

@app.route('/', methods=['GET'])
def home():
	return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
	
	if request.method == 'POST':

		file = request.files['file']
		utils.cleaningFolder(path_actual)	
		f = pi.transformImage(file)

		# Salvando arquivo original
		complete_path = path_original + secure_filename(file.content_type).replace('_','.')
		pi.saveImage(complete_path, f) 
		# Salvando copia a ser editada
		complete_path = path_actual + secure_filename(file.content_type).replace('_','.')
		pi.saveImage(complete_path, f) 
		#f.save(path + secure_filename(f.content_type).replace('_','.'))

	return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

# Aqui será a parte de gestao de filtros aplicados.
# A ideia é receber apenas uma string e aqui decidir o que aplicar.
@app.route('/apply_filter', methods=['POST'])
def apply_filter():
	
	# Pegando nome do arquivo
	files = listdir(path_actual)
	if request.method == 'POST' and len(files) == 1:

		file = files[0]
		print(file)

		filter_ = request.form['filter']

		if filter_ in filters_list or filter_ in non_filters_list:

			filename = file.replace('_','.')
			if filter_ in filters_list:

				# Lendo arquivo
				complete_filename = path_actual + filename
				img_matrix = pi.readImage(complete_filename)

				# Aplicando filtro
				filters_in_use.append(filter_)
				img_matrix = utils.applyFilter(filter_, img_matrix)

			elif filter_ in non_filters_list:

				# Lendo arquivo
				complete_filename = path_original + filename
				img_matrix = pi.readImage(complete_filename)
					
				# Removendo um filtro
				filters_in_use.remove(filter_[4:])
				img_matrix = utils.removeFilter(filter_, img_matrix, filters_in_use)

			# Limpando diretório
			utils.cleaningFolder(path_actual)

			# Salvando arquivo
			complete_path = path_actual + filename
			pi.saveImage(complete_path, img_matrix) 
			#f.save('static/images/original/' + secure_filename(f.content_type).replace('_','.'))

			print(filters_in_use)
		else:

			return json.dumps({'success':True}), 400, {'ContentType':'application/json'}

		return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

	else:
		return json.dumps({'success':False}), 500, {'ContentType':'application/json'} 
























