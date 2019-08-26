import numpy as np
from imread import imread
from matplotlib import pyplot as mpl
from PIL import Image 
import imageio

# Transforma a imagem em preto e branco e RGB (o formato desejado)
def transformImage(filename):
    image_file = Image.open(filename) # Abrir imagem colorida
    image_file = image_file.convert('L').convert('RGB') # Convertendo para preto e branco e RGB
    return np.asarray(image_file, dtype ='uint8')

# Leitura simples para arquivo que nao precisa de pre-processamento
def readImage(filename):
    return imread(filename)

# Mostrar imagem
def showImage(matrix_image):
    mpl.imshow(matrix_image)
    
'''  FILTROS '''

# Filtro negativo
def filterNegative(matrix_image):
    negative_image = 255 - matrix_image
    return negative_image

# Filtro de contraste com o log
def filterContrastLog(matrix_image):
    matrix_image = np.log(matrix_image + 1)
    matrix_image = matrix_image/matrix_image.max()
    matrix_image = 255 * matrix_image
    return matrix_image.astype('uint8')
    
# Filtro de contraste com potência
def filterContrastPow(matrix_image):
    matrix_image = np.power(np.double(matrix_image), 5)
    matrix_image = matrix_image/matrix_image.max()
    matrix_image = 255 * matrix_image
    return matrix_image.astype('uint8')
   
# Filtro de contraste que calcula de acordo com dois pontos desenhados
def filterTwoPoints(p1, p2):
    matrix_image = matrix_image

#Salvar imagem
def saveImage(path, matrix):
    imageio.imwrite(path, matrix) 