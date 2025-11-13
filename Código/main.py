import json
import numpy as np
from ultralytics import YOLO
import cv2
from sort.sort import *
from funcoes import get_carro, ler_placa, escrever_csv

tracker = Sort()

# modelo utilizado (YOLO)
modelo = YOLO('yolo/yolov8n.pt')
detector_de_placa = YOLO('detector/detector_de_placas.pt')

# carregar o video
video = cv2.VideoCapture('video/videocompleto.mp4')

frame_numero = -1

resultados = {}

placas_detectadas = {}

# uma lista pré-definida do que vai salvar, sendo 2(carro), 3(moto), 5(onibus), 7(caminhão)
veiculos = [2, 3, 5, 7]

# while para ler os frames do video
ret = True
while ret:
    frame_numero +=1
    ret , frame = video.read()
    if ret:
        resultados[frame_numero] = {}

        #detecta veiculos
        detectados = modelo(frame)[0]
        lista_detectados = []
        for detectado in detectados.boxes.data.tolist():
            x1,y1,x2,y2,valor,classe_id = detectado
            if int(classe_id) in veiculos:
                lista_detectados.append([x1,y1,x2,y2,valor])

        #track video
        track_ids = tracker.update(np.asarray(lista_detectados))

        #detectar as placas do carro
        placas = detector_de_placa(frame)[0]
        for placas in placas.boxes.data.tolist():
            x1,y1,x2,y2,valor,classe_id = placas

            #salvar a placa no carro
            xcarro1,ycarro1,xcarro2,ycarro2,carro_id = get_carro(placas, track_ids)
            
            #crop das placas
            placas_crop = frame[int(y1):int(y2), int(x1):int(x2)]

            #processar a placa do carro e transformando em cinza para ter um melhor rendimento assim
            placas_crop_gray = cv2.cvtColor(placas_crop, cv2.COLOR_BGR2GRAY)
            _, placas_crop_threshold = cv2.threshold(placas_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

            #ler o valor da placa
            placa_texto, placa_texto_score = ler_placa(placas_crop_threshold)

            #salva as informações capturadas no frame, dentro do dicionário result caso tenha uma placa
            #está salvando a placa em um frame especifico e em um carro especifico por isso [frame_numero][carro_id]
            if placa_texto is not None:
                resultados[frame_numero][carro_id] = {'carro': {'area': [xcarro1,ycarro1,xcarro2,ycarro2]},
                                               'placa': {'area': [x1,y1,x2,y2],
                                                                'texto': placa_texto,
                                                                'placa_probabilidade': valor,
                                                                'texto_probabilidade': placa_texto_score}}
                
            # Salvando apenas o frame que é capturado a placa que possui mais chance de estar correta
            if placa_texto is not None :
                carro_id = int(carro_id)
                conf = float(placa_texto_score)
                if carro_id not in placas_detectadas :
                    placas_detectadas[carro_id] = ({
                    "frame": frame_numero,
                    "carro_id": carro_id,
                    "placa": placa_texto,
                    "confianca": conf,
                })
                else:
                    # Se já existe, mantém apenas a de maior confiança
                    if conf > placas_detectadas[carro_id]['confianca']:
                        placas_detectadas[carro_id].update({
                        "frame": frame_numero,
                        "placa": placa_texto,
                        "confianca": conf,
                    })

# Converte para lista
placas_final = list(placas_detectadas.values())

print("\n PLACAS DETECTADAS")
for p in placas_final:
    print(p)

# Resultado
escrever_csv(resultados, './resultado.csv')

with open("placas_detectadas.json", "w", encoding="utf-8") as f:
    json.dump(placas_final, f, indent=4, ensure_ascii=False)

print("\nArquivo 'placas_detectadas.json' salvo com sucesso!")