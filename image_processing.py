import numpy as np
import math
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
    image_file = Image.open(filename).convert('RGB')
    return np.asarray(image_file, dtype='uint8')

# Mostrar imagem
def showImage(matrix_image):
    mpl.imshow(matrix_image)
    
#Salvar imagem
def saveImage(path, matrix):
    imageio.imwrite(path, matrix) 
    
#Salvar imagem colorida
def saveImageColorful(path, matrix):
    mpl.imsave(path, matrix.astype(np.uint8))   
     
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
    
# Filtro de constraste que gera uma imagem com pixels equalizados
def filterHistogram(img_matrix, is_colorful=False):
    
    if is_colorful: 
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        # Calculando probabilidades acumulativas R
        countsR, labelsR = calculateHistogram(img_matrix)
        probsR, labelsR = calculateProbability(countsR, labelsR)
        probs_acumR = calculateAcuProbability(probsR)
        
        # Calculando probabilidades acumulativas G
        countsG, labelsG = calculateHistogram(img_matrix)
        probsG, labelsG = calculateProbability(countsG, labelsG)
        probs_acumG = calculateAcuProbability(probsG)
        
        # Calculando probabilidades acumulativas B
        countsB, labelsB = calculateHistogram(img_matrix)
        probsB, labelsB = calculateProbability(countsB, labelsB)
        probs_acumB = calculateAcuProbability(probsB)
        
        r = calculateChannelHistogram(r, probs_acumR)
        g = calculateChannelHistogram(g, probs_acumG)
        b = calculateChannelHistogram(b, probs_acumB)
        RGB = toRGBImage(r,g,b)
        
        return RGB.astype('uint8')
    
    else:
        # Aplicando filtro de fato
        one_channel_img = getOneChannelFromRGBMatrix(img_matrix)
        
        # Calculando probabilidades acumulativas
        counts, labels = calculateHistogram(img_matrix)
        probs, labels = calculateProbability(counts, labels)
        probs_acum = calculateAcuProbability(probs)
        one_channel_img = calculateChannelHistogram(one_channel_img, probs_acum)

        # Criando imagem com os três canais RGB em preto e branco
        img_matrix = expandOneToThreeChannels(one_channel_img)
        img_matrix = np.array(img_matrix)
        return img_matrix.astype('uint8')

# Filtro da convolução
def filterConvolution(img_matrix, filter_, is_colorful=False):
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        # Calculando sobre canais
        r = calculateChannelConvolution(r, filter_)
        g = calculateChannelConvolution(g, filter_)
        b = calculateChannelConvolution(b, filter_)
        
        # Normalizando
        r = np.array(r)
        r = r/r.max()
        r = 255 * r
        
        g = np.array(g)
        g = g/g.max()
        g = 255 * g
        
        b = np.array(b)
        b = b/b.max()
        b = 255 * b
        
        RGB = toRGBImage(r,g,b)
        
        return RGB.astype('uint8')
    
    else:
        
        # Obtendo apenas um canal da imagem
        img_matrix = getOneChannelFromRGBMatrix(img_matrix.copy())

        new_m = calculateChannelConvolution(img_matrix, filter_)

        # Normalizando
        new_m = np.array(new_m)
        new_m = new_m/new_m.max()
        new_m = 255 * new_m
        new_m = expandOneToThreeChannels(new_m)

        return np.array(new_m).astype('uint8')

# Filtro da média (embaçar)
def filterMean(img_matrix, n, is_colorful=False):
    
    # Tamanho da máscara da média
    mask = np.zeros((n,n))
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        r = calculateChannelMean(r, mask)
        g = calculateChannelMean(g, mask)
        b = calculateChannelMean(b, mask)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
        
    else:
        
        # Separando apenas um canal do RGB
        one_channel = getOneChannelFromRGBMatrix(img_matrix.copy())
        one_channel = calculateChannelMean(one_channel, mask)
        new_m = expandOneToThreeChannels(one_channel)
        return np.array(new_m).astype('uint8')

# Filtro da mediana (tirar ruído)
def filterMedian(img_matrix, n, is_colorful=False):
    
    # Tamanho da máscara da mediana
    mask = np.zeros((n,n))
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        r = calculateChannelMedian(r, mask)
        g = calculateChannelMedian(g, mask)
        b = calculateChannelMedian(b, mask)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
    
    else:
        
        # Separando apenas um canal do RGB
        img_matrix = getOneChannelFromRGBMatrix(img_matrix.copy())

        new_m = calculateChannelMedian(img_matrix, mask)

        new_m = expandOneToThreeChannels(new_m)
        return np.array(new_m).astype('uint8')

# Filtro Laplaciano
def filterLaplacian(img_matrix, n_dimension=None, sigma=None, is_colorful=False):
    
    # Definindo filtro laplaciano
    filter_ = [[0,1,0],[1,-4,1],[0,1,0]]
    
    # Filtro laplaciano diagonal
    #filter_ = [[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]
    
    # Realizando suavização Gaussiana primeiro
    img_matrix = filterGaussian(img_matrix, n_dimension, sigma, is_colorful)
    
    # Mask
    mask = filterConvolution(img_matrix, filter_, is_colorful)
    
    new_image = np.array(img_matrix) + np.array(mask)
    
    # Rotacionar matriz de filtro
    return new_image.astype('uint8')

# Filtro de suavização Gaussiano
def filterGaussian(img_matrix, n_dimension, sigma, is_colorful=False):
    
    # Criando filtro
    filter_ = matlab_style_gauss2D((n_dimension,n_dimension),sigma)
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        r = calculateChannelGaussian(r, filter_)
        g = calculateChannelGaussian(g, filter_)
        b = calculateChannelGaussian(b, filter_)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
    
    else:
    
        # Obtendo apenas um canal da imagem
        one_channel = getOneChannelFromRGBMatrix(img_matrix.copy())

        new_m = calculateChannelGaussian(one_channel, filter_)

        # Normalizando
        new_m = expandOneToThreeChannels(new_m)

        return np.array(new_m).astype('uint8')
    
# Filter Highboost
def filterHighboost(img_matrix, constant, is_colorful=False):
    
    # Aplicar filtro de blur da média
    blur_image = filterMean(img_matrix, 3, is_colorful)
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        blurR = getOneChannelFromRGBMatrix(blur_image, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        blurG = getOneChannelFromRGBMatrix(blur_image, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        blurB = getOneChannelFromRGBMatrix(blur_image, 2)
        
        r = calculateChannelHighboost(r, blurR, constant)
        g = calculateChannelHighboost(g, blurG, constant)
        b = calculateChannelHighboost(b, blurB, constant)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
    
    else:
        
        # Obter um canal de cada um
        one_channel_orig = getOneChannelFromRGBMatrix(img_matrix)
        one_channel_blur = getOneChannelFromRGBMatrix(blur_image)

        new_image = calculateChannelHighboost(one_channel_orig, one_channel_blur, constant)
        new_image = expandOneToThreeChannels(new_image)

        return np.array(new_image).astype('uint8')

# Filter convolução
def filterSobel(img_matrix, is_colorful=False):
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        r = calculateChannelSobel(r)
        g = calculateChannelSobel(g)
        b = calculateChannelSobel(b)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
    
    else:
    
        # Obtendo apenas um canal da imagem
        one_channel = getOneChannelFromRGBMatrix(img_matrix.copy())
        one_channel = calculateChannelSobel(one_channel)
        new_m = expandOneToThreeChannels(one_channel)
        return np.array(new_m).astype('uint8')

# Implementar desenho de grafico
# Formato dos pontos: (x,y)
def filterTwoPointsChart(img_matrix, point1, point2, is_colorful=False):
    
    functions = {}
    
    # Calculate functions
    functions['function1'], functions['function2'], functions['function3'] = findFunctions(point1, point2)
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        r = calculateChannelTwoPoints(r, point1, point2, functions)
        g = calculateChannelTwoPoints(g, point1, point2, functions)
        b = calculateChannelTwoPoints(b, point1, point2, functions)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
        
    else:
        
        one_channel = getOneChannelFromRGBMatrix(img_matrix)
        one_channel = calculateChannelTwoPoints(one_channel, point1, point2, functions)
        new_image = expandOneToThreeChannels(one_channel)

        return np.array(new_image).astype('uint8')

# Filtro de dois Limiarização (thresholging)
def filterLimit(img_matrix, limit, is_colorful=False):
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        r = calculateChannelLimit(r, limit)
        g = calculateChannelLimit(g, limit)
        b = calculateChannelLimit(b, limit)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
    
    else:
        
        one_channel = getOneChannelFromRGBMatrix(img_matrix)
        one_channel = calculateChannelLimit(one_channel, limit)
        new_m = expandOneToThreeChannels(one_channel)
        return np.array(new_m).astype('uint8')

# Filter Gradient borders
def filterGradient(img_matrix, is_colorful=False):
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        r = calculateChannelGradient(r)
        g = calculateChannelGradient(g)
        b = calculateChannelGradient(b)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
    
    else:
        
        # Obtendo apenas um canal da imagem
        one_channel = getOneChannelFromRGBMatrix(img_matrix.copy())
        one_channel = calculateChannelGradient(one_channel)
        new_m = expandOneToThreeChannels(one_channel)
            
        return np.array(new_m).astype('uint8')

# Encode message
def filterEncodeMsg(img, msg):
    
    """
    use the red portion of an image (r, g, b) tuple to
    hide the msg string characters as ASCII values
    red value of the first pixel is used for length of string
    """
    length = len(msg)
    if img.mode != 'RGB':
        print("image mode needs to be RGB")
        return False
    # use a copy of image to hide the text in
    encoded = img.copy()
    width, height = img.size
    index = 0
    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row))
            # first value is length of msg
            if row == 0 and col == 0 and index < length:
                asc = length
            elif index <= length:
                c = msg[index -1]
                asc = ord(c)
            else:
                asc = r
            encoded.putpixel((col, row), (asc, g , b))
            index += 1
    print(type(encoded))
    return encoded

# Filter geometric mean 
def filterGeometricMean(img_matrix, n, is_colorful=False):
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        r = calculateChannelGeometricMean(r, n)
        g = calculateChannelGeometricMean(g, n)
        b = calculateChannelGeometricMean(b, n)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
    
    else:
    
        # Obtendo apenas um canal da imagem
        img_matrix = getOneChannelFromRGBMatrix(img_matrix.copy())
        new_m = calculateChannelGeometricMean(img_matrix, n)
        new_m = expandOneToThreeChannels(new_m)

        return np.array(new_m).astype('uint8')

# Filter harmonic mean 
def filterHarmonicMean(img_matrix, n, is_colorful=False):
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        r = calculateChannelHarmonicMean(r, n)
        g = calculateChannelHarmonicMean(g, n)
        b = calculateChannelHarmonicMean(b, n)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
    
    else:
    
        # Obtendo apenas um canal da imagem
        img_matrix = getOneChannelFromRGBMatrix(img_matrix.copy())
        new_m = calculateChannelHarmonicMean(img_matrix, n)
        new_m = expandOneToThreeChannels(new_m)

        return np.array(new_m).astype('uint8')

# Filter harmonic mean 
def filterContraHarmonicMean(img_matrix, n, is_colorful=False):
    
    if is_colorful:
        
        # Obtendo canais separados
        r = getOneChannelFromRGBMatrix(img_matrix, 0)
        g = getOneChannelFromRGBMatrix(img_matrix, 1)
        b = getOneChannelFromRGBMatrix(img_matrix, 2)
        
        r = calculateChannelContraHarmonicMean(r, n)
        g = calculateChannelContraHarmonicMean(g, n)
        b = calculateChannelContraHarmonicMean(b, n)
        
        RGB = toRGBImage(r,g,b)
        return RGB.astype('uint8')
    
    else:
        # Obtendo apenas um canal da imagem
        img_matrix = getOneChannelFromRGBMatrix(img_matrix.copy())
        new_m = calculateChannelContraHarmonicMean(img_matrix, n)
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

def matlab_style_gauss2D(shape=(3,3),sigma=1.4):
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

# Função que junta três canais em uma imagem RGB
def toRGBImage(r,g,b):
    RGB = np.dstack((r,g,b))
    return RGB

# Função que retorna apenas uma dos três canais de uma matriz referente a uma imagem RGB cinza 
def getOneChannelFromRGBMatrix(img_matrix, column=0):
    matrix = []
    for line in img_matrix:
        columns = []
        for values in line:
            columns.append(values[column])
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

''' AUXILIARES DE CÁLCULO DE CANAL DOS FILTROS '''

# Função para calcular alteração sobre um canal
def calculateChannelHistogram(one_channel_img, probs_acum):
    qt_lines = len(one_channel_img)
    qt_columns = len(one_channel_img[0])
    
    for i in range(qt_lines):
        for j in range(qt_columns):
            one_channel_img[i][j] = one_channel_img[i][j] * probs_acum[one_channel_img[i][j]]
            
    return one_channel_img.copy()

def calculateChannelConvolution(img_matrix, filter_):
    
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
     
    return new_m

def calculateChannelMean(img_matrix, mask):

    # Encontrando centro da máscara
    center = findMatrixCenter(mask)
    n = len(mask)
    
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
            
    return new_m

def calculateChannelMedian(img_matrix, mask):

    # Encontrando centro da máscara
    center = findMatrixCenter(mask)
    n = len(mask)
    
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
            
    return new_m

def calculateChannelGaussian(img_matrix, filter_):
    
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
            
    return new_m

def calculateChannelHighboost(one_channel_orig, one_channel_blur, constant):

    # Criando máscara
    mask = np.array(one_channel_orig) - np.array(one_channel_blur)
    
    # Calculando nova imagem
    new_image = np.array(one_channel_orig) + constant * np.array(mask)
    
    return new_image

def calculateChannelSobel(img_matrix):
    
    # Máscaras
    g1 = [[-1,-2,-1],[0,0,0],[1,2,1]]

    g2 = [[-1,0,1],[-2,0,2],[-1,0,1]]
    
    # Encontrar centro da matriz
    center_g1 = findMatrixCenter(g1)
    center_g2 = findMatrixCenter(g2)
    
    # Definir dicionário com operações a serem aplicadas em cada célula referente ao filtro
    f1_operations = createDictFromCoordsCentered(g1, center_g1)
    f2_operations = createDictFromCoordsCentered(g2, center_g2)
    
    # Colhendo informações da imagem
    lin = len(img_matrix)
    col = len(img_matrix[0])

    new_m1 = copy.deepcopy(img_matrix)   
    
    # Máscara 1
    for i in range(lin):
        for j in range(col):
            sum_ = 0
            
            for key, value in f1_operations.items():
                try:
                    sum_ = sum_ + img_matrix[i + value[0]][j + value[1]] * g1[key[0]][key[1]]
                except:
                    sum_ = sum_
                    
            new_m1[i][j] = abs(int(sum_))
            
    # Máscara 2    
    new_m2 = copy.deepcopy(img_matrix)   

    for i in range(lin):
        for j in range(col):
            sum_ = 0
            
            for key, value in f2_operations.items():
                try:
                    sum_ = sum_ + img_matrix[i + value[0]][j + value[1]] * g2[key[0]][key[1]]
                except:
                    sum_ = sum_
                    
            new_m2[i][j] = abs(int(sum_))
    
    new_m = np.array(new_m1) + np.array(new_m2)
    
    # Normalizando
    new_m = new_m/new_m.max()
    new_m = 255 * new_m
    
    return new_m

def calculateChannelTwoPoints(one_channel, point1, point2, functions):
    
    # Copia da matriz
    new_m = one_channel.copy()
    
    rows = len(one_channel)
    cols = len(one_channel[0])
    
    # Percorrendo matriz
    for i in range(rows):
        
        for j in range(cols):

            name_func = decideFunction(point1[0], point2[0], one_channel[i][j])
            new_m[i][j] = functions[name_func](one_channel[i][j])
    
    return new_m

def calculateChannelLimit(one_channel, limit):

    # Copia da matriz
    new_m = one_channel.copy()

    rows = len(one_channel)
    cols = len(one_channel[0])
    
    # Percorrendo matriz
    for i in range(rows):
        for j in range(cols):

            if(new_m[i][j] > limit):
                new_m[i][j] = 255
            else:
                new_m[i][j] = 0
    
    return new_m

def calculateChannelGradient(img_matrix):
    
    # Máscaras
    g1 = [[0,0,0],[0,-1,0],[0,0,1]]

    g2 = [[0,0,0],[0,0,-1],[0,1,0]]
    
    # Encontrar centro da matriz
    center_g1 = findMatrixCenter(g1)
    center_g2 = findMatrixCenter(g2)
    
    # Definir dicionário com operações a serem aplicadas em cada célula referente ao filtro
    f1_operations = createDictFromCoordsCentered(g1, center_g1)
    f2_operations = createDictFromCoordsCentered(g2, center_g2)
    
    # Colhendo informações da imagem
    lin = len(img_matrix)
    col = len(img_matrix[0])

    new_m1 = copy.deepcopy(img_matrix)   
    
    # Máscara 1
    for i in range(lin):
        for j in range(col):
            sum_ = 0
            
            for key, value in f1_operations.items():
                try:
                    sum_ = sum_ + img_matrix[i + value[0]][j + value[1]] * g1[key[0]][key[1]]
                except:
                    sum_ = sum_
                    
            new_m1[i][j] = abs(int(sum_))
            
    # Máscara 2    
    new_m2 = copy.deepcopy(img_matrix)   

    for i in range(lin):
        for j in range(col):
            sum_ = 0
            
            for key, value in f2_operations.items():
                try:
                    sum_ = sum_ + img_matrix[i + value[0]][j + value[1]] * g2[key[0]][key[1]]
                except:
                    sum_ = sum_
                    
            new_m2[i][j] = abs(int(sum_))
    
    new_m = np.array(new_m1) + np.array(new_m2)
    
    # Normalizando
    new_m = new_m/new_m.max()
    new_m = 255 * new_m
    return new_m

def calculateChannelGeometricMean(img_matrix, n):
    
    # Máscara
    # Tamanho da máscara da média
    mask = np.ones((n,n))
    
    # Encontrar centro da matriz
    center = findMatrixCenter(mask)
    
    # Definir dicionário com operações a serem aplicadas em cada célula referente ao filtro
    f_operations = createDictFromCoordsCentered(mask, center)
    
    # Colhendo informações da imagem
    lin = len(img_matrix)
    col = len(img_matrix[0])

    new_m = copy.deepcopy(img_matrix)   
    
    for i in range(lin):
        for j in range(col):
            prod_ = np.float(1)
            
            for key, value in f_operations.items():
                try:
                    prod_ = prod_ * img_matrix[i + value[0]][j + value[1]]
                except:
                    prod_ = prod_
                             
            new_m[i][j] = prod_ ** (1/(n*n))
    
    # Normalizando
    new_m = np.array(new_m)
    new_m = new_m/new_m.max()
    new_m = 255 * new_m
    return new_m

def calculateChannelHarmonicMean(img_matrix, n):
    
    # Máscara
    # Tamanho da máscara da média
    mask = np.ones((n,n))
    
    # Encontrar centro da matriz
    center = findMatrixCenter(mask)
    
    # Definir dicionário com operações a serem aplicadas em cada célula referente ao filtro
    f_operations = createDictFromCoordsCentered(mask, center)
    
    # Colhendo informações da imagem
    lin = len(img_matrix)
    col = len(img_matrix[0])

    new_m = copy.deepcopy(img_matrix)   
    
    for i in range(lin):
        for j in range(col):
            sum_ = 0
            
            for key, value in f_operations.items():
                try:
                    sum_ = sum_ + 1/img_matrix[i + value[0]][j + value[1]]
                except:
                    sum_ = sum_
            
            try:
                new_m[i][j] = (n*n)/sum_
            except:
                new_m[i][j] = 0
    
    # Normalizando
    new_m = np.array(new_m)
    new_m = new_m/new_m.max()
    new_m = 255 * new_m
    return new_m

def calculateChannelContraHarmonicMean(img_matrix, n):
    
    # Máscara
    # Tamanho da máscara da média
    mask = np.ones((n,n))
    
    # Encontrar centro da matriz
    center = findMatrixCenter(mask)
    
    # Definir dicionário com operações a serem aplicadas em cada célula referente ao filtro
    f_operations = createDictFromCoordsCentered(mask, center)
    
    # Colhendo informações da imagem
    lin = len(img_matrix)
    col = len(img_matrix[0])

    new_m = copy.deepcopy(img_matrix)   
    
    for i in range(lin):
        for j in range(col):
            sum_ = 0
            sum_squares = 0
            
            for key, value in f_operations.items():
                try:
                    sum_ = sum_ + img_matrix[i + value[0]][j + value[1]]
                    sum_squares = sum_squares + (img_matrix[i + value[0]][j + value[1]])**2
                except:
                    sum_ = sum_
                    sum_squares = sum_squares
            
            try:
                new_m[i][j] = sum_squares/sum_
            except:
                new_m[i][j] = 0
    
    # Normalizando
    new_m = np.array(new_m)
    new_m = new_m/new_m.max()
    new_m = 255 * new_m
    return new_m

''' FUNÇÕES AUXILIARES PARA O FILTRO DE DOIS PONTOS '''

def findFunction(coords1, coords2):
	try :
		const = (coords2[1] - coords1[1])/ (coords2[0] - coords1[0])

		def function(n):
			mult_da_const = n - coords1[0]
			return int(coords1[1] + const * mult_da_const)
	except:
		def function(n):
			return n
	return function


def findFunctions(point1, point2):
    function1 = findFunction((0, 0), point1)
    function2 = findFunction(point1, point2)
    function3 = findFunction(point2, (255, 255))
    
    return function1, function2, function3


def decideFunction(x1, x2, n):
    if n <= x1:
        return "function1"
    
    if x1 <= n <= x2:
        return "function2"
    
    if x2 <= n :
        return "function3"  
    
def convertTupleToIntTuple(tuple_):
	lista = []
	for i in range(len(tuple_)):
		lista.append(int(tuple_[i]))
	return tuple(lista)
    
    
''' CODIFICAÇÃO '''

# Decode message
def decodeMsg(img):
    """
    check the red portion of an image (r, g, b) tuple for
    hidden message characters (ASCII values)
    """
    width, height = img.size
    msg = ""
    index = 0
    for row in range(height):
        for col in range(width):
            try:
                r, g, b = img.getpixel((col, row))
            except ValueError:
                # need to add transparency a for some .png files
                r, g, b, a = img.getpixel((col, row))		
            # first pixel r value is length of message
            if row == 0 and col == 0:
                length = r
            elif index <= length:
                msg += chr(r)
            index += 1
    return msg