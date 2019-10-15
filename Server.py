from flask import Flask, render_template, request, redirect, jsonify, make_response
from os import listdir, remove
import cv2
from os.path import isfile, join
from matplotlib import pyplot as mpl
from itertools import chain
import image_processing as pi
from PIL import Image
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

filters_with_args=["convolution", "mean", "median", "laplacian", "gaussian", "highboost", "two_points", "limit","geometric_mean","harmonic_mean","contraharmonic_mean","encode_msg","HSV_ajust","equalize_histogram"]
filters_list = ["negative", "log", "power", "histogram", "convolution", "mean", "median", "laplacian", "gaussian", "highboost", "sobel", "two_points","limit","geometric_mean","harmonic_mean","contraharmonic_mean","gradient","encode_msg","HSV_ajust","equalize_histogram","gray_scale_mean","gray_scale_mean_weigh", "sepia"]
non_filters_list = ["non-negative", "non-log", "non-power", "non-histogram", "non-convolution", "non-mean", "non-median", "non-laplacian", "non-gaussian", "non-highboost",  "non-sobel", "non-two_points","non-limit","non-geometric_mean","non-harmonic_mean","non-contraharmonic_mean"]

global args 
global is_img_colorful
global filters_in_use 
global extension
global file_version

#args = {'convolution':None,'mean':None,'median':None,'gaussian':None,'highboost':None, 'two_points':None}
args = {}
filters_in_use = []
file_version = 1
#CORS(app)  

if __name__ == '__main__':    
    app.run(host='127.0.0.1', port=5000, debug=True)

@app.route('/', methods=['GET'])
def home():
	return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
	
	global is_img_colorful

	if request.method == 'POST':

		file = request.files['file']
		is_img_colorful = 'True' in request.form['is_colorful']
		utils.cleaningFolder(path_actual)

		if is_img_colorful:
			f = pi.readImage(file)
		else:
			f = pi.transformImage(file)

		name = secure_filename(file.content_type)

		if("_tiff" in name):
			print(name)
			name = name.replace("_tiff","_png")
			print(name)

		# Salvando arquivo original
		global file_version
		file_version = 1
		name = name.replace('_', str(file_version) + '.')
		complete_path = path_actual + name

		if not is_img_colorful:
			pi.saveImage(complete_path, f) 
		else:
			pi.saveImageColorful(complete_path, f)

		# Salvando extansão
		global extension
		extension = name[name.index('.')+1:]
		print(extension)

	return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

# Aqui será a parte de gestao de filtros aplicados.
# A ideia é receber apenas uma string e aqui decidir o que aplicar.
@app.route('/apply_filter', methods=['POST'])
def apply_filter():

	global file_version
	
	import time
	# Pegando nome do arquivo
	files = listdir(path_actual)
	if request.method == 'POST':

		# Indicar que estamos usando a variavel global
		global args
		global filters_in_use

		filter_ = request.form['filter']

		for file_ in files:
			print("entrou")
			print("file" + file_)
			if "image" + str(file_version) + "_" in file_ and filter_ in filters_in_use:
				print("estrou")
				return json.dumps({'success':True}), 200

		file = files[file_version-1]
		print(file)

		if filter_ in filters_list or filter_ in non_filters_list:

			print("file v" + str(file_version))
			filename = file.replace('_',str(file_version+1)+'.')

			# Lendo arquivo
			complete_filename = path_actual + filename
			img_matrix = pi.readImage(complete_filename)

			if filter_ in filters_list:

				# Tratamento para filtros com argumentos
				if(filter_ in filters_with_args):
					print("filters_with_args")
					request_form = copy.deepcopy(request.form)
					new_args = utils.saveArgs(filter_,  request_form, args, complete_filename)
					args = new_args.copy()
				
				print(filter_)
				img_matrix = utils.applyFilter(filter_, img_matrix, args, is_img_colorful)
				

			# Nome do arquivo
			file_version = file_version + 1
			file_ = 'image' + str(file_version) + '.' + extension
			complete_path = path_actual + file_

			# Salvando arquivo
			if filter_ == 'encode_msg':
				img_matrix.save(complete_path)

			elif filter_ == 'equalize_histogram':
				cv2.imwrite(complete_path,img_matrix) 

			elif not is_img_colorful:
				pi.saveImage(complete_path, img_matrix)

			else:
				pi.saveImageColorful(complete_path, img_matrix)
			#f.save('static/images/original/' + secure_filename(f.content_type).replace('_','.'))
		
		else:

			return json.dumps({'success':False}), 500

		filters_in_use.append(filter_)

		return json.dumps({'success':True}), 200

	else:
		return json.dumps({'success':False, 'error':{'type':500, 'message':'Requisição incorreta!'}}),500 

# Aqui será a parte de gestao de filtros aplicados.
# A ideia é receber apenas uma string e aqui decidir o que aplicar.
@app.route('/remove_filter', methods=['GET'])
def remove_filter():

	print('entrou')

	# Indicar que estamos usando a variavel global
	global filters_in_use
	global file_version

	if len(filters_in_use) > 0:
		filter_ = filters_in_use[-1]
		filters_in_use.remove(filter_)
		file_version = file_version - 1

		print(filters_in_use)
		print(file_version)
		return json.dumps({'success':True}), 200
		
	return json.dumps({'success':False, 'error':{'type':500, 'message':'Requisição incorreta!'}}),500 

# Endpoint para calcular o histograma da imagem
@app.route('/show_histogram', methods=['POST'])
def show_histogram():
	
	# Pegando nome do arquivo
	files = listdir(path_actual)
	file_ = files[0]

	# Lendo arquivo de imagem
	complete_filename = path_actual + file_
	img_matrix = pi.readImage(complete_filename)

	# Img
	if is_img_colorful:

		channel = int(request.form['channel'])

		if 0 <= channel and channel <=2:
			print(channel)
			counts, labels = pi.calculateRGBHistogram(img_matrix, channel)

		else:
			counts, labels = pi.calculateVHistogram(img_matrix)

	else:
		# Calculando histograma
		counts, labels = pi.calculateHistogram(img_matrix)

	# Gerando histograma
	mpl.bar(labels[:-1] - 0.5, counts, width=1, edgecolor='none')
	mpl.xlim([-0.5, 255.5])

	# Salvando
	mpl.savefig(path_histogram_img + file_histogram_img)

	mpl.clf()

	return json.dumps({'success':True}), 200

# Endpoint para calcular o histograma da imagem
@app.route('/decode_image_msg', methods=['GET'])
def decode_image_msg():
	
	# Pegando nome do arquivo
	files = listdir(path_actual)
	file_ = files[file_version-1]

	# Lendo arquivo de imagem
	complete_filename = path_actual + file_

	img = Image.open(complete_filename)

	# Descobrir mensagem
	msg = pi.decodeMsg(img)
	print(msg)
	#return json.dumps({'success':True, 'data':'oi'}), 200
	return jsonify({'mensagem': msg})




















