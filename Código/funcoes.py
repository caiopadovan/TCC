import string
import easyocr

reader = easyocr.Reader(['en'], gpu=False)

# Mapeando dicionários para conversão de caracteres e diferenciar caracteres com números parecidos
dif_caracter_com_inteiro = {'O': '0',
                            'I': '1',
                            'J': '3',
                            'A': '4',
                            'G': '6',
                            'S': '5'}

dif_inteiro_com_caracter = {'0': 'O',
                            '1': 'I',
                            '3': 'J',
                            '4': 'A',
                            '6': 'G',
                            '5': 'S'}

# Escreve o resultado do arquivo em CSV
def escrever_csv(resultados, caminho_saida):
    with open(caminho_saida, 'w') as f:
        f.write('{},{},{},{},{},{},{}\n'.format('frame', 'carro_id', 'carro',
                                                'placa', 'placa_probabilidade', 'texto',
                                                'texto_probabilidade'))

        for frame in resultados.keys():
            for carro_id in resultados[frame].keys():
                print(resultados[frame][carro_id])
                if 'carro' in resultados[frame][carro_id].keys() and \
                   'placa' in resultados[frame][carro_id].keys() and \
                   'texto' in resultados[frame][carro_id]['placa'].keys():
                    f.write('{},{},{},{},{},{},{}\n'.format(frame,
                                                            carro_id,
                                                            '[{} {} {} {}]'.format(
                                                                resultados[frame][carro_id]['carro']['area'][0],
                                                                resultados[frame][carro_id]['carro']['area'][1],
                                                                resultados[frame][carro_id]['carro']['area'][2],
                                                                resultados[frame][carro_id]['carro']['area'][3]),
                                                            '[{} {} {} {}]'.format(
                                                                resultados[frame][carro_id]['placa']['area'][0],
                                                                resultados[frame][carro_id]['placa']['area'][1],
                                                                resultados[frame][carro_id]['placa']['area'][2],
                                                                resultados[frame][carro_id]['placa']['area'][3]),
                                                            resultados[frame][carro_id]['placa']['placa_probabilidade'],
                                                            resultados[frame][carro_id]['placa']['texto'],
                                                            resultados[frame][carro_id]['placa']['texto_probabilidade'])
                            )
        f.close()


def verificar_placa(texto):
    #Verifica se a placa tem apenas 7 numeros/letras
    if len(texto) != 7:
        return False

    #Verifica se a primeira, segunda, quinta, sexta e sétima variavel da placa é uma letra e se a terceira e quarta é um número
    if (texto[0] in string.ascii_uppercase or texto[0] in dif_inteiro_com_caracter.keys()) and \
       (texto[1] in string.ascii_uppercase or texto[1] in dif_inteiro_com_caracter.keys()) and \
       (texto[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or texto[2] in dif_caracter_com_inteiro.keys()) and \
       (texto[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or texto[3] in dif_caracter_com_inteiro.keys()) and \
       (texto[4] in string.ascii_uppercase or texto[4] in dif_inteiro_com_caracter.keys()) and \
       (texto[5] in string.ascii_uppercase or texto[5] in dif_inteiro_com_caracter.keys()) and \
       (texto[6] in string.ascii_uppercase or texto[6] in dif_inteiro_com_caracter.keys()):
        return True
    else:
        return False
    
    """
    MERCOSUL

    if (texto[0] in string.ascii_uppercase or texto[0] in dif_inteiro_com_caracter.keys()) and \
       (texto[1] in string.ascii_uppercase or texto[1] in dif_inteiro_com_caracter.keys()) and \
       (texto[2] in string.ascii_uppercase or texto[4] in dif_inteiro_com_caracter.keys()) and \
       (texto[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or texto[3] in dif_caracter_com_inteiro.keys()) and \
       (texto[4] in string.ascii_uppercase or texto[4] in dif_inteiro_com_caracter.keys()) and \
       (texto[5] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or texto[2] in dif_caracter_com_inteiro.keys()) and \
       (texto[6] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or texto[3] in dif_caracter_com_inteiro.keys()):
        return True
    else:
        return False

    """


def formatar(texto):
    #Percorre todas as caracteres para cada um dos valores
    #Diferenciando letras e números que são parecidos, de acordo com que tipo de valor está esperando naquela posição
    placa_ = ''
    mapear = {0: dif_inteiro_com_caracter, 1: dif_inteiro_com_caracter, 4: dif_inteiro_com_caracter, 5: dif_inteiro_com_caracter, 6: dif_inteiro_com_caracter,
               2: dif_caracter_com_inteiro, 3: dif_caracter_com_inteiro}
    for j in [0, 1, 2, 3, 4, 5, 6]:
        if texto[j] in mapear[j].keys():
            placa_ += mapear[j][texto[j]]
        else:
            placa_ += texto[j]

    return placa_

    """
    MERCOSUL
    placa_ = ''
    mapear = {0: dif_inteiro_com_caracter, 1: dif_inteiro_com_caracter, 2: dif_inteiro_com_caracter, 4: dif_inteiro_com_caracter,
               3: dif_caracter_com_inteiro, 4: dif_caracter_com_inteiro, 6: dif_caracter_com_inteiro}
    for j in [0, 1, 2, 3, 4, 5, 6]:
        if texto[j] in mapear[j].keys():
            placa_ += mapear[j][texto[j]]
        else:
            placa_ += texto[j]

    return placa_
    """


def ler_placa(placa_crop):
    deteccoes = reader.readtext(placa_crop)

    for detectado in deteccoes:
        bbox, texto, valor = detectado

        texto = texto.upper().replace(' ', '')

        if verificar_placa(texto):
            return formatar(texto), valor

    return None, None


def get_carro(placa, veiculo_track_ids):
    x1, y1, x2, y2, valor, class_id = placa

    encontrado = False
    for j in range(len(veiculo_track_ids)):
        xcarro1, ycarro1, xcarro2, ycarro2, carro_id = veiculo_track_ids[j]

        #Verificando se o contorno que está em volta do carro é maior do que o contorno da placa (descobrindo assim que o retangulo de dentro é a placa do carro)
        if x1 > xcarro1 and y1 > ycarro1 and x2 < xcarro2 and y2 < ycarro2:
            carro_indx = j
            encontrado = True
            break

    if encontrado:
        return veiculo_track_ids[carro_indx]

    return -1, -1, -1, -1, -1