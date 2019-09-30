from flask import Flask, render_template, request, redirect, jsonify, make_response
from os import listdir, remove
from os.path import isfile, join
from matplotlib import pyplot as mpl
from itertools import chain
import image_processing as pi
import utils
from werkzeug.utils import secure_filename
import json
import copy
#from flask_cors import CORS
'''
REGRAS DA APLICAÇÃO:

Para cada efeito haverá duas pastas: Antes e depois. Assim, teremos
o controle sobre o do e undo. 

Instalacoes pro image_processing: 
	conda install -c conda-forge imread
	pip install Pillow
	pip install opencv-python
'''

app = Flask(__name__)
path_ = "static/images/"
path_original = path_ + "original/"
path_actual = path_ + "actual/"
path_histogram_img = path_ +  "histogram/"
file_histogram_img = "hist-image.png"
filters_with_args=["convolution", "mean", "median", "laplacian", "gaussian", "highboost", "two_points", "limit","geometric_mean","harmonic_mean","contraharmonic_mean"]
filters_list = ["negative", "log", "power", "histogram", "convolution", "mean", "median", "laplacian", "gaussian", "highboost", "sobel", "two_points","limit","geometric_mean","harmonic_mean","contraharmonic_mean"]
non_filters_list = ["non-negative", "non-log", "non-power", "non-histogram", "non-convolution", "non-mean", "non-median", "non-laplacian", "non-gaussian", "non-highboost",  "non-sobel", "non-two_points","non-limit","non-geometric_mean","non-harmonic_mean","non-contraharmonic_mean"]
global args 
#args = {'convolution':None,'mean':None,'median':None,'gaussian':None,'highboost':None, 'two_points':None}
args = {}
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
		utils.cleaningFolder(path_original)
		utils.cleaningFolder(path_actual)	
		f = pi.transformImage(file)
		name = secure_filename(file.content_type)

		if("_tiff" in name):
			print(name)
			name = name.replace("_tiff","_png")
			print(name)


		# Salvando arquivo original
		complete_path = path_original + name.replace('_','.')
		pi.saveImage(complete_path, f) 
		# Salvando copia a ser editada
		complete_path = path_actual + name.replace('_','.')
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

		# Indicar que estamos usando a variavel global
		global args

		filter_ = request.form['filter']

		if filter_ in filters_list or filter_ in non_filters_list:

			filename = file.replace('_','.')
			if filter_ in filters_list:

				# Lendo arquivo
				complete_filename = path_actual + filename
				img_matrix = pi.readImage(complete_filename)

				# Tratamento para filtros com argumentos
				if(filter_ in filters_with_args):
					request_form = copy.deepcopy(request.form)
					new_args = utils.saveArgs(filter_,  request_form, args)
					print(new_args)
					args = new_args.copy()
				
				img_matrix = utils.applyFilter(filter_, img_matrix, args)
				print(filter_)
				# Aplicando filtro
				filters_in_use.append(filter_)
				
			elif filter_ in non_filters_list:

				# Lendo arquivo
				complete_filename = path_original + filename
				img_matrix = pi.readImage(complete_filename)
					
				# Removendo um filtro
				filters_in_use.remove(filter_[4:])
				print(filter_[4:])
				img_matrix = utils.removeFilter(filter_, img_matrix, filters_in_use, args)

			# Limpando diretório
			utils.cleaningFolder(path_actual)

			# Salvando arquivo
			complete_path = path_actual + filename
			pi.saveImage(complete_path, img_matrix) 
			#f.save('static/images/original/' + secure_filename(f.content_type).replace('_','.'))

			print(filters_in_use)
		else:

			return json.dumps({'success':False}), 500

		return json.dumps({'success':True}), 200

	else:
		return json.dumps({'success':False, 'error':{'type':500, 'message':'Requisição incorreta!'}}),500 

# Endpoint para calcular o histograma da imagem
@app.route('/show_histogram', methods=['GET'])
def show_histogram():
	
	# Pegando nome do arquivo
	files = listdir(path_actual)
	file_ = files[0]

	# Lendo arquivo de imagem
	complete_filename = path_actual + file_
	img_matrix = pi.readImage(complete_filename)

	# Calculando histograma
	counts, labels = pi.calculateHistogram(img_matrix)

	# Gerando histograma
	mpl.bar(labels[:-1] - 0.5, counts, width=1, edgecolor='none')
	mpl.xlim([-0.5, 255.5])

	# Salvando
	mpl.savefig(path_histogram_img + file_histogram_img)

	mpl.clf()

	return json.dumps({'success':True}), 200






















