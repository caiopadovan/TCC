from ultralytics import YOLO
import cv2
import pytesseract
import re
import os
import csv

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

yolo_model_path = r"models/license_plate_detector.pt"  # ajuste para onde você salvou o .pt
model = YOLO(yolo_model_path)

# --- PASTAS DE INPUT/OUTPUT ---
input_folder = "imgs"
output_folder = "output_yolo"
os.makedirs(output_folder, exist_ok=True)

# --- CSV PARA RESULTADOS ---
csv_file = os.path.join(output_folder, "placas_resultados.csv")
csv_data = []

# --- PROCESSAR TODAS AS IMAGENS ---
for nome_arquivo in os.listdir(input_folder):
    if not nome_arquivo.lower().endswith((".jpg", ".png", ".jpeg")):
        continue

    caminho_img = os.path.join(input_folder, nome_arquivo)
    img = cv2.imread(caminho_img)
    if img is None:
        print(f"Erro ao carregar {nome_arquivo}")
        continue

    results = model.predict(caminho_img, conf=0.4, verbose=False)

    for r in results:
        boxes = r.boxes.xyxy  # coordenadas [x1, y1, x2, y2]
        for box in boxes:
            x1, y1, x2, y2 = map(int, box[:4])

            # --- RECORTAR PLACA ---
            placa_img = img[y1:y2, x1:x2]
            placa_gray = cv2.cvtColor(placa_img, cv2.COLOR_BGR2GRAY)

            # --- PRÉ-PROCESSAMENTO ---
            placa_gray = cv2.bilateralFilter(placa_gray, 9, 75, 75)
            placa_gray = cv2.convertScaleAbs(placa_gray, alpha=1.5, beta=20)
            _, placa_bin = cv2.threshold(placa_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # --- OCR COM WHITELIST ---
            texto = pytesseract.image_to_string(
                placa_bin,
                config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            )

            # --- LIMPAR E AJUSTAR TEXTO ---
            texto = re.sub(r'[^A-Z0-9]', '', texto.upper())
            if len(texto) > 7:
                texto = texto[-7:]
            if not texto:
                texto = "SEM_TEXTO"

            # --- SALVAR IMAGEM RECORTADA ---
            nome_saida = os.path.join(output_folder, f"{os.path.splitext(nome_arquivo)[0]}_{texto}.jpg")
            cv2.imwrite(nome_saida, placa_bin)

            # --- DESENHAR NO ORIGINAL ---
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, texto, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # --- SALVAR RESULTADO NO CSV ---
            csv_data.append([nome_arquivo, texto, nome_saida])

    # --- SALVAR IMAGEM FINAL COM DETECÇÕES ---
    cv2.imwrite(os.path.join(output_folder, f"det_{nome_arquivo}"), img)

# --- ESCREVER CSV ---
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Imagem", "Placa", "ArquivoRecortado"])
    writer.writerows(csv_data)

print("\n Processamento concluído! Imagens e resultados salvos em 'output_yolo'.")
