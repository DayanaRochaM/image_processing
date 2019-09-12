#GARANTIR APLICACAO D FILTRO SÓ DEPOIS Q O UPLOAD DA FOTO FOR FEITOR
import image_processing as pi
from os import listdir,remove

# Excluindo arquivos para deixar apenas o desejado
def cleaningFolder(directory):
	files = listdir(directory)
	for file in files:
		remove(directory + file)

# Aplicar filtro
def applyFilter(filter_, img_matrix, extra=None):

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
		img_matrix = pi.filterConvolution(img_matrix, extra)

	elif filter_ == 'mean':
		# Aqui o extra é um n, que é a dimensão da máscara da matriz
		img_matrix = pi.filterMean(img_matrix, extra)

	elif filter_ == 'median':
		# Aqui o extra é um n, que é a dimensão da máscara da matriz
		img_matrix = pi.filterMedian(img_matrix, extra)

	return img_matrix

# Aplicar sequencia de filtros
def removeFilter(filter_, img_matrix, filters_in_use):
	filter_ = filter_[4:]
	for name in filters_in_use:
		img_matrix = applyFilter(name, img_matrix)

	return img_matrix