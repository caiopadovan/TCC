import csv
import numpy as np
from scipy.interpolate import interp1d


def interpolacao(data):
    # Salva os principais valores usados
    frame_numero = np.array([int(row['frame']) for row in data])
    carro_ids = np.array([int(float(row['carro_id'])) for row in data])
    carros = np.array([list(map(float, row['carro'][1:-1].split())) for row in data])
    placas = np.array([list(map(float, row['placa'][1:-1].split())) for row in data])

    interpolated_data = []
    carro_ids_unicos = np.unique(carro_ids)
    for carro_id in carro_ids_unicos:

        frame_numero_ = [p['frame'] for p in data if int(float(p['carro_id'])) == int(float(carro_id))]
        print(frame_numero_, carro_id)

        # Filtra valor de acordo com o id do carro encontrado
        carro_mascara = carro_ids == carro_id
        car_frame_numero = frame_numero[carro_mascara]
        carro_interpolado = []
        placa_interpolado = []

        primeiro_frame_numero = car_frame_numero[0]

        for i in range(len(carros[carro_mascara])):
            frame_atual = car_frame_numero[i]
            carro = carros[carro_mascara][i]
            placa = placas[carro_mascara][i]

            if i > 0:
                pre_frame_numero = car_frame_numero[i-1]
                pre_carro = carro_interpolado[-1]
                pre_placa = placa_interpolado[-1]

                if frame_atual - pre_frame_numero > 1:
                    # Interpolando os dados
                    frames_gap = frame_atual - pre_frame_numero
                    x = np.array([pre_frame_numero, frame_atual])
                    x_new = np.linspace(pre_frame_numero, frame_atual, num=frames_gap, endpoint=False)
                    interp_func = interp1d(x, np.vstack((pre_carro, carro)), axis=0, kind='linear')
                    interpolated_carro = interp_func(x_new)
                    interp_func = interp1d(x, np.vstack((pre_placa, placa)), axis=0, kind='linear')
                    interpolated_placa = interp_func(x_new)

                    carro_interpolado.extend(interpolated_carro[1:])
                    placa_interpolado.extend(interpolated_placa[1:])

            carro_interpolado.append(carro)
            placa_interpolado.append(placa)

        for i in range(len(carro_interpolado)):
            frame_atual = primeiro_frame_numero + i
            row = {}
            row['frame'] = str(frame_atual)
            row['carro_id'] = str(carro_id)
            row['carro'] = ' '.join(map(str, carro_interpolado[i]))
            row['placa'] = ' '.join(map(str, placa_interpolado[i]))

            if str(frame_atual) not in frame_numero_:
                # Coloca valores não encontrados como '0'
                row['placa_probabilidade'] = '0'
                row['texto'] = '0'
                row['texto_probabilidade'] = '0'
            else:
                # Se encontrar valor, salvar ele
                original_row = [p for p in data if int(p['frame']) == frame_atual and int(float(p['carro_id'])) == int(float(carro_id))][0]
                row['placa_probabilidade'] = original_row['placa_probabilidade'] if 'placa_probabilidade' in original_row else '0'
                row['texto'] = original_row['texto'] if 'texto' in original_row else '0'
                row['texto_probabilidade'] = original_row['texto_probabilidade'] if 'texto_probabilidade' in original_row else '0'

            interpolated_data.append(row)

    return interpolated_data


# Lendo o arquivo csv original
with open('resultado.csv', 'r') as file:
    reader = csv.DictReader(file)
    data = list(reader)

# Interpolando o arquivo original
interpolated_data = interpolacao(data)
interpolated_data_filtrado = [row for row in interpolated_data if float(row['carro_id']) != -1]

# Escrevendo o resultado em um novo CSV
header = ['frame', 'carro_id', 'carro', 'placa', 'placa_probabilidade', 'texto', 'texto_probabilidade']
with open('resultado_interpolado.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    writer.writerows(interpolated_data_filtrado)

print("Arquivo 'resultado_interpolado.csv' salvo com sucesso!")