import ast

import cv2
import numpy as np
import pandas as pd


def draw_border(img, top_left, bottom_right, color=(0, 255, 0), thickness=10, line_length_x=200, line_length_y=200):
    x1, y1 = top_left
    x2, y2 = bottom_right

    cv2.line(img, (x1, y1), (x1, y1 + line_length_y), color, thickness)  #-- canto superior esquerdo
    cv2.line(img, (x1, y1), (x1 + line_length_x, y1), color, thickness)

    cv2.line(img, (x1, y2), (x1, y2 - line_length_y), color, thickness)  #-- canto inferior esquerdo
    cv2.line(img, (x1, y2), (x1 + line_length_x, y2), color, thickness)

    cv2.line(img, (x2, y1), (x2 - line_length_x, y1), color, thickness)  #-- canto superior direito
    cv2.line(img, (x2, y1), (x2, y1 + line_length_y), color, thickness)

    cv2.line(img, (x2, y2), (x2, y2 - line_length_y), color, thickness)  #-- canto inferior direito
    cv2.line(img, (x2, y2), (x2 - line_length_x, y2), color, thickness)

    return img


resultados = pd.read_csv('resultado_interpolado.csv')

# carregar video
video_caminho = 'video/videocompleto.mp4'
cap = cv2.VideoCapture(video_caminho)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter('./resultado.mp4', fourcc, fps, (width, height))

placas = {}
for carro_id in np.unique(resultados['carro_id']):
    max_ = np.amax(resultados[resultados['carro_id'] == carro_id]['texto_probabilidade'])
    placas[carro_id] = {'placas_crop': None,
                             'texto': resultados[(resultados['carro_id'] == carro_id) &
                                                             (resultados['texto_probabilidade'] == max_)]['texto'].iloc[0]}
    cap.set(cv2.CAP_PROP_POS_FRAMES, resultados[(resultados['carro_id'] == carro_id) &
                                             (resultados['texto_probabilidade'] == max_)]['frame'].iloc[0])
    ret, frame = cap.read()

    x1, y1, x2, y2 = ast.literal_eval(resultados[(resultados['carro_id'] == carro_id) &
                                              (resultados['texto_probabilidade'] == max_)]['placa'].iloc[0].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))

    placas_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
    placas_crop = cv2.resize(placas_crop, (int((x2 - x1) * 400 / (y2 - y1)), 400))

    placas[carro_id]['placas_crop'] = placas_crop


frame_nmr = -1

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# ler frame
ret = True
while ret:
    ret, frame = cap.read()
    frame_nmr += 1
    if ret:
        df_ = resultados[resultados['frame'] == frame_nmr]
        for row_indx in range(len(df_)):
            # desenhar o carro
            car_x1, car_y1, car_x2, car_y2 = ast.literal_eval(df_.iloc[row_indx]['carro'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
            draw_border(frame, (int(car_x1), int(car_y1)), (int(car_x2), int(car_y2)), (0, 255, 0), 25,
                        line_length_x=200, line_length_y=200)

            # desenhar a placa
            x1, y1, x2, y2 = ast.literal_eval(df_.iloc[row_indx]['placa'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 12)

            # recortar a placa
            placas_crop = placas[df_.iloc[row_indx]['carro_id']]['placas_crop']

            H, W, _ = placas_crop.shape

            try:
                frame[int(car_y1) - H - 100:int(car_y1) - 100,
                      int((car_x2 + car_x1 - W) / 2):int((car_x2 + car_x1 + W) / 2), :] = placas_crop

                frame[int(car_y1) - H - 400:int(car_y1) - H - 100,
                      int((car_x2 + car_x1 - W) / 2):int((car_x2 + car_x1 + W) / 2), :] = (255, 255, 255)

                (text_width, text_height), _ = cv2.getTextSize(
                    placas[df_.iloc[row_indx]['carro_id']]['texto'],
                    cv2.FONT_HERSHEY_SIMPLEX,
                    4.3,
                    17)

                cv2.putText(frame,
                            placas[df_.iloc[row_indx]['carro_id']]['texto'],
                            (int((car_x2 + car_x1 - text_width) / 2), int(car_y1 - H - 250 + (text_height / 2))),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            4.3,
                            (0, 0, 0),
                            17)

            except:
                pass

        out.write(frame)
        frame = cv2.resize(frame, (1280, 720))

out.release()
cap.release()
print("Video gerado com sucesso!")