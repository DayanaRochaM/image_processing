import numpy as np
import copy
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
    
#Salvar imagem
def saveImage(path, matrix):
    imageio.imwrite(path, matrix) 
    
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
    
# Filtro de constraste que gera uma imagem com pixels equalizados
def filterHistogram(img_matrix):
    # Calculando probabilidades acumulativas
    counts, labels = calculateHistogram(img_matrix)
    probs, labels = calculateProbability(counts, labels)
    probs_acum = calculateAcuProbability(probs)
    
    # Aplicando filtro de fato
    one_channel_img = getOneChannelFromRGBMatrix(img_matrix)
    qt_lines = len(one_channel_img)
    qt_columns = len(one_channel_img[0])
    
    for i in range(qt_lines):
        for j in range(qt_columns):
            one_channel_img[i][j] = one_channel_img[i][j] * probs_acum[one_channel_img[i][j]]
    
    # Criando imagem com os três canais RGB
    img_matrix = expandOneToThreeChannels(one_channel_img)
    img_matrix = np.array(img_matrix)
    return img_matrix.astype('uint8')

# Filtro da convolução
def filterConvolution(img_matrix, filter_):
    # Obtendo apenas um canal da imagem
    img_matrix = getOneChannelFromRGBMatrix(img_matrix.copy())
    
    # Matriz de filtro tem que ser quadrada
    
    # Rotacionar matriz de filtro
    f_reverse = rotateMatrix180(filter_)
    
    # Encontrar centro da matriz
    center = findMatrixCenter(filter_)
    
    # Definir dicionário com operações a serem aplicadas em cada célula referente ao filtro
    f_operations = createDictFromCoordsCentered(filter_, center)
    
    # Colhendo informações da imagem
    lin = len(img_matrix)
    col = len(img_matrix[0])

    new_m = copy.deepcopy(img_matrix)   

    for i in range(lin):
        for j in range(col):
            sum_ = 0
            
            for key, value in f_operations.items():
                try:
                    sum_ = sum_ + img_matrix[i + value[0]][j + value[1]] * f_reverse[key[0]][key[1]]
                except:
                    sum_ = sum_
                    
            new_m[i][j] = int(sum_)
    
    # Normalizando
    new_m = np.array(new_m)
    new_m = new_m/new_m.max()
    new_m = 255 * new_m
    new_m = expandOneToThreeChannels(new_m)
            
    return np.array(new_m).astype('uint8')

# Filtro da média (embaçar)
def filterMean(img_matrix, n):
    
    # Tamanho da máscara da média
    mask = np.zeros((n,n))
    
    # Separando apenas um canal do RGB
    img_matrix = getOneChannelFromRGBMatrix(img_matrix.copy())
    
    # Encontrando centro da máscara
    center = findMatrixCenter(mask)
    
    # Definir dicionário com operações a serem aplicadas em cada célula referente ao filtro
    m_operations = createDictFromCoordsCentered(mask, center)

    # Colhendo informações da imagem
    lin = len(img_matrix)
    col = len(img_matrix[0])

    new_m = copy.deepcopy(img_matrix)

    for i in range(lin):
        for j in range(col):
            sum_ = 0

            for key, value in m_operations.items():
                try:
                    sum_ = sum_ + img_matrix[i + value[0]][j + value[1]]
                except:
                    sum_ = sum_
                    
            mean = sum_/(n*n)  
            new_m[i][j] =  int(mean)
            
    new_m = expandOneToThreeChannels(new_m)
    return new_m

# Filtro da mediana (tirar ruído)
def filterMedian(img_matrix, n):
    
    # Tamanho da máscara da mediana
    mask = np.zeros((n,n))
    
    # Separando apenas um canal do RGB
    img_matrix = getOneChannelFromRGBMatrix(img_matrix.copy())
    
    # Encontrando centro da máscara
    center = findMatrixCenter(mask)
    
    # Definir dicionário com operações a serem aplicadas em cada célula referente ao filtro
    m_operations = createDictFromCoordsCentered(mask, center)

    # Colhendo informações da imagem
    lin = len(img_matrix)
    col = len(img_matrix[0])

    new_m = copy.deepcopy(img_matrix)

    for i in range(lin):
        for j in range(col):
            
            new_list = list()

            for key, value in m_operations.items():
                try:
                    new_list.append(img_matrix[i + value[0]][j + value[1]])
                except:
                    new_list.append(0)

            np_list = np.array(new_list)
            median = np.median(np_list)  
            new_m[i][j] =  int(median)
            
    new_m = expandOneToThreeChannels(new_m)
    return new_m

# Filtro Laplaciano
def filterLaplacian(img_matrix, n_dimension=None, sigma=None):
    
    # Definindo filtro laplaciano
    filter_ = [[0,1,0],[1,-4,1],[0,1,0]]
    
    # Filtro laplaciano diagonal
    #filter_ = [[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]
    
    # Realizando suavização Gaussiana primeiro
    #img_matrix = filterGaussian(img_matrix, n_dimension, sigma)
    
    # Rotacionar matriz de filtro
    return filterConvolution(img_matrix, filter_)

# Filtro de suavização Gaussiano
def filterGaussian(img_matrix, n_dimension, sigma):
    
    # Criando filtro
    filter_ = matlab_style_gauss2D((n_dimension,n_dimension),sigma)
    
     # Obtendo apenas um canal da imagem
    img_matrix = getOneChannelFromRGBMatrix(img_matrix.copy())
    
    # Matriz de filtro tem que ser quadrada
    
    # Rotacionar matriz de filtro
    f_reverse = rotateMatrix180(filter_)
    
    # Encontrar centro da matriz
    center = findMatrixCenter(filter_)
    
    # Definir dicionário com operações a serem aplicadas em cada célula referente ao filtro
    f_operations = createDictFromCoordsCentered(filter_, center)
    
    # Colhendo informações da imagem
    lin = len(img_matrix)
    col = len(img_matrix[0])

    new_m = copy.deepcopy(img_matrix)   

    for i in range(lin):
        for j in range(col):
            sum_ = 0
            
            for key, value in f_operations.items():
                try:
                    sum_ = sum_ + img_matrix[i + value[0]][j + value[1]] * f_reverse[key[0]][key[1]]
                except:
                    sum_ = sum_
                    
            new_m[i][j] = int(sum_)
    
    # Normalizando
    new_m = expandOneToThreeChannels(new_m)
            
    return np.array(new_m).astype('uint8')
    
''' CALCULAR HISTOGRAMA '''

# Funcao que retorna quantidade de ocorrencias por pixel e os pixels associados
def calculateHistogram(img_matrix):
    # img = cv2.imread(filename)
    
    # Calcula a média do canais RGB e concatena em um array 1D
    vals = img_matrix.mean(axis=2).flatten()
    
    # Calcular histograma de 0 a 255 cores
    counts, labels = np.histogram(vals, range(257))
    return counts, labels

# Função que exibe histograma
def showHistogram(counts, labels):
    
    # Plottar histagrama centrados nos valores 0..255
    mpl.bar(labels[:-1] - 0.5, counts, width=1, edgecolor='none')
    mpl.xlim([-0.5, 255.5])
    mpl.show()
    
    
''' CRIAR FILTRO DE SUAVIZAÇÃO GAUSSIANA '''

def matlab_style_gauss2D(shape=(3,3),sigma=0.5):
    """
    2D gaussian mask - should give the same result as MATLAB's
    fspecial('gaussian',[shape],[sigma])
    """
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h


''' OPERACOES COM MATRIZES '''

# Função que retorna apenas uma dos três canais de uma matriz referente a uma imagem RGB cinza 
def getOneChannelFromRGBMatrix(img_matrix):
    matrix = []
    for line in img_matrix:
        columns = []
        for values in line:
            columns.append(values[0])
        matrix.append(columns)
    return matrix

# Função que dada uma matriz referente a um canal de imagem, retorna uma matriz com 3 canais iguais, representando uma imagem cinza
def expandOneToThreeChannels(img_matrix):
    matrix = []
    for line in img_matrix:
        columns = []
        for value in line:
            columns.append([value, value, value])
        matrix.append(columns)
    return matrix

# Para rotacionar matriz em 180 graus (usado na convolução)
def rotateMatrix180(filter_):
    filter_ = np.matrix(filter_)
    f_reverse = np.rot90(filter_, 2)
    f_reverse = f_reverse.tolist()
    
    return f_reverse

# Criando dicionario de coordenadas da matriz baseadas no centro da mesma
def createDictFromCoordsCentered(filter_, center):
    line = len(filter_)
    col = len(filter_[0])
    f_operations = {}
    for i in range(line):
        for j in range(col):
            f_operations[(i,j)] = tuple(np.subtract((i,j),center))
    
    return f_operations

# Encontrando centro da matriz (lembrando que sempre será quadrada de numero impar)
def findMatrixCenter(matrix):
    i = int(len(matrix)/2) 
    center = (i,i)
    
    return center

''' PROBABILIDADES '''

# Probabilidade individual simples
def calculateProbability(counts, labels):
    # A ordem do counts deve estar correspondente a ordem das labels
    quant = sum(counts)
    probs = []
    for count in counts:
        probs.append(count/quant)
            
    return probs, labels[:-1]   

# Probabilidade acumulada
def calculateAcuProbability(probs):
    probs_acum = []
    for i in range(len(probs)):
        probs_acum.append(sum(probs[0:i+1]))
    return probs_acum       