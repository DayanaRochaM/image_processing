#GARANTIR APLICACAO D FILTRO SÓ DEPOIS Q O UPLOAD DA FOTO FOR FEITOR
import image_processing as pi
from os import listdir,remove
from PIL import Image
import ast
import json
import urllib.request
import requests
global filename

# Excluindo arquivos para deixar apenas o desejado
def cleaningFolder(directory):
	files = listdir(directory)
	for file in files:
		remove(directory + file)

# Aplicar filtro
def applyFilter(filter_, img_matrix, args, is_img_colorful):

	print(filter_)
	if filter_ == 'negative':
		img_matrix = pi.filterNegative(img_matrix)

	elif filter_ == 'log':
		img_matrix = pi.filterContrastLog(img_matrix)

	elif filter_ == 'power':
		img_matrix = pi.filterContrastPow(img_matrix)

	elif filter_ == 'histogram':
		img_matrix = pi.filterHistogram(img_matrix, is_img_colorful)

	elif filter_ == 'convolution':
		# Aqui o extra é uma matriz que é um filtro
		img_matrix = pi.filterConvolution(img_matrix, args['convolution'], is_img_colorful)

	elif filter_ == 'mean':
		# Aqui o extra é um n, que é a dimensão da máscara da matriz
		img_matrix = pi.filterMean(img_matrix, args['mean'], is_img_colorful)

	elif filter_ == 'median':
		# Aqui o extra é um n, que é a dimensão da máscara da matriz
		img_matrix = pi.filterMedian(img_matrix, args['median'], is_img_colorful)

	elif filter_ == 'laplacian':
		img_matrix = pi.filterLaplacian(img_matrix, args['laplacian']['n'], args['laplacian']['sigma'], is_img_colorful)

	elif filter_ == 'gaussian':
		img_matrix = pi.filterGaussian(img_matrix, args['gaussian']['n'], args['gaussian']['sigma'], is_img_colorful)

	elif filter_ == 'highboost':
		img_matrix = pi.filterHighboost(img_matrix, args['highboost'], is_img_colorful)

	elif filter_ == 'sobel':
		img_matrix = pi.filterSobel(img_matrix, is_img_colorful)

	elif filter_ == 'two_points':
		print(args['two_points']['point1'])
		print(args['two_points']['point2'])
		img_matrix = pi.filterTwoPointsChart(img_matrix, args['two_points']['point1'], args['two_points']['point2'], is_img_colorful)

	elif filter_ == 'limit':
		img_matrix = pi.filterLimit(img_matrix, args['limit']['limit'], is_img_colorful)

	elif filter_ == 'geometric_mean':
		img_matrix = pi.filterGeometricMean(img_matrix, args['geometric_mean'], is_img_colorful)

	elif filter_ == 'harmonic_mean':
		img_matrix = pi.filterHarmonicMean(img_matrix, args['harmonic_mean'], is_img_colorful)

	elif filter_ == 'contraharmonic_mean':
		img_matrix = pi.filterContraHarmonicMean(img_matrix, args['contraharmonic_mean'], is_img_colorful)

	elif filter_ == 'gradient':
		img_matrix = pi.filterGradient(img_matrix, is_img_colorful)

	elif filter_ == 'encode_msg':
		img = Image.open(filename).convert('RGB') # Abrir imagem colorida
		img_matrix = pi.filterEncodeMsg(img, args['encode_msg']['msg'])

	elif filter_ == 'HSV_ajust':
		print('entrou')
		img_matrix = pi.RGBtoHSV(img_matrix)
		print('passou do RGB TO HSV')
		img_matrix = pi.applyPercentChannelHSV(img_matrix,  args['HSV_ajust']['channel'], args['HSV_ajust']['percent'])
		print('passou do apply percent')
		img_matrix = pi.HSVtoRGB(img_matrix)
		print('passou do HSV to rgb')

	return img_matrix

# Aplicar sequencia de filtros
# def removeFilter(filter_, img_matrix, filters_in_use, args):
# 	filter_ = filter_[4:]
# 	for name in filters_in_use:
# 		img_matrix = applyFilter(name, img_matrix,args)

# 	return img_matrix

# Checando se matriz é quadrada
def checkMatrixIsSquare(matrix):

	lines = len(matrix)
	min_cols = lines
	max_cols = lines

	for line in matrix:
		qt_cols = len(line)

		if qt_cols < min_cols:
			min_cols = qt_cols

		if qt_cols > max_cols:
			max_cols = qt_cols

	if lines == min_cols and lines == max_cols:
		return True

	return False

# Tratamento para salvar argumentos
def saveArgs(filter_, request, args, complete_filename):

	if(filter_ == "convolution"): 

		# Checando se texto pode ser transformado em matriz 
		text = request['text']
		matrix = ast.literal_eval(text)

		# Chechando dimensões da matriz
		isSquare = checkMatrixIsSquare(matrix)
		print(isSquare)

		if not isSquare:
			return  json.dumps({'success':False, 'error':'test'}), 500

		args['convolution'] = matrix

	elif (filter_ == "mean" or filter_ == "median" or filter_ == "geometric_mean" or filter_ == "harmonic_mean" or filter_ == "contraharmonic_mean"):

		# Pegando dimensão da matriz e checando se é um inteiro
		text = request['text']
		print(text)
		isInteger = text.isdigit()
		isInteger = isInteger

		if not isInteger:
			return json.dumps({'success':False}), 500

		dimension = int(text)
		if not dimension%2 != 0:
			return json.dumps({'success':False}), 500
		
		args[filter_] = dimension

	elif (filter_ == "gaussian" or filter_ == "laplacian"):
		# Pegando dimensão da matriz e checando se é um inteiro
		n = request['n']
		print("n: " + n)

		sigma = request['sigma']
		print("sigma: " + sigma)

		try:
			sigma = float(sigma)
		except:
			return  json.dumps({'success':False}), 500

		args[filter_] = {'n': int(n), 'sigma': sigma}

	elif (filter_ == "highboost"):

		constant = request['text']
		print('constant: ' + constant)

		try:
			constant = float(constant)
			if (constant < 0 or constant > 1):
				return  json.dumps({'success':False}), 500
		except:
			return  json.dumps({'success':False}), 500

		args['highboost'] = constant

	elif (filter_ == "two_points"):

		point1 = request['point1']
		point2 = request['point2']
		
		print('point1: ' + point1)
		print('point2: ' + point2)

		try:
			point1 = tuple(point1.split(','))
			point2 = tuple(point2.split(','))
			point1 = pi.convertTupleToIntTuple(point1)
			point2 = pi.convertTupleToIntTuple(point2)
			# Verificando se valores estão no intervalo desejado
			if(0 <= point1[0] <= 255 and 0 <= point2[0] <= 255 and 0 <= point1[1] <= 255 and 0 <= point2[1] <= 255):
   				pass
			else:
   				return  json.dumps({'success':False}), 500
		except:
			return  json.dumps({'success':False}), 500

		args['two_points'] = {'point1':point1, 'point2':point2}

	elif (filter_ == 'limit'):

		limit = request['text']

		try:

			limit = int(limit)
			# Verificando se valores estão no intervalo desejado
			if(0 <= limit <= 255):
				pass
			else:
				return  json.dumps({'success':False}), 500
		except:
			return  json.dumps({'success':False}), 500

		args['limit'] = {'limit':limit}

	elif (filter_ == 'encode_msg'):

		msg = request['text']

		if(len(msg) > 255):
			# limit length of message to 255
 			print("Texto muito grande! (don't exeed 255 characters)")
 			return json.dumps({'success':False}), 500

		args['encode_msg'] = {'msg':msg}
		global filename
		filename = complete_filename

	elif (filter_ == 'HSV_ajust'):
		channel = int(request['channel'])
		percent = float(request['percent']) * 0.1
		print(channel)
		print(percent)
		args['HSV_ajust'] = {'channel':channel, 'percent':percent}

	return args