#GARANTIR APLICACAO D FILTRO SÓ DEPOIS Q O UPLOAD DA FOTO FOR FEITOR
import image_processing as pi
from os import listdir,remove

# Excluindo arquivos para deixar apenas o desejado
def cleaningFolder(directory):
	files = listdir(directory)
	for file in files:
		remove(directory + file)

# Aplicar filtro
def applyFilter(filter_, img_matrix, args):

	if filter_ == 'negative':
		img_matrix = pi.filterNegative(img_matrix)

	elif filter_ == 'log':
		img_matrix = pi.filterContrastLog(img_matrix)

	elif filter_ == 'power':
		img_matrix = pi.filterContrastPow(img_matrix)

	elif filter_ == 'power':
		img_matrix = pi.filterContrastPow(img_matrix)

	elif filter_ == 'histogram':
		img_matrix = pi.filterHistogram(img_matrix)

	elif filter_ == 'convolution':
		# Aqui o extra é uma matriz que é um filtro
		img_matrix = pi.filterConvolution(img_matrix, args['convolution'])

	elif filter_ == 'mean':
		# Aqui o extra é um n, que é a dimensão da máscara da matriz
		img_matrix = pi.filterMean(img_matrix, args['mean'])

	elif filter_ == 'median':
		# Aqui o extra é um n, que é a dimensão da máscara da matriz
		img_matrix = pi.filterMedian(img_matrix, args['median'])

	elif filter_ == 'laplacian':
		img_matrix = pi.filterLaplacian(img_matrix)

	elif filter_ == 'gaussian':
		img_matrix = pi.filterGaussian(img_matrix, args['gaussian']['n'], args['gaussian']['sigma'])

	elif filter_ == 'highboost':
		img_matrix = pi.filterHighboost(img_matrix, args['highboost'])

	return img_matrix

# Aplicar sequencia de filtros
def removeFilter(filter_, img_matrix, filters_in_use, args):
	filter_ = filter_[4:]
	for name in filters_in_use:
		img_matrix = applyFilter(name, img_matrix,args)

	return img_matrix

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