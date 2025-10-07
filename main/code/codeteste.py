from ultralytics import YOLO
import cv2
import pytesseract
import re
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

model_path = r"models/license_plate_detector.pt"
model = YOLO(model_path)

# --- ABRIR VÍDEO ---
video_path = "video/video.mp4"
cap = cv2.VideoCapture(video_path)

# --- ARRAY PARA GUARDAR AS PLACAS DETECTADAS ---
placas_detectadas = []

# --- LOOP PRINCIPAL ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # fim do vídeo

    # --- DETECÇÃO COM YOLO ---
    results = model.predict(frame, conf=0.5, verbose=False)

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # --- RECORTAR PLACA ---
            placa_crop = frame[y1:y2, x1:x2]
            if placa_crop.size == 0:
                continue

            placa_gray = cv2.cvtColor(placa_crop, cv2.COLOR_BGR2GRAY)
            placa_gray = cv2.bilateralFilter(placa_gray, 9, 75, 75)
            _, placa_bin = cv2.threshold(placa_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # --- OCR ---
            texto = pytesseract.image_to_string(
                placa_bin,
                config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            )

            texto = re.sub(r'[^A-Z0-9]', '', texto.upper())
            if len(texto) > 7:
                texto = texto[-7:]
            if texto and texto not in placas_detectadas and len(texto) >= 6:
                placas_detectadas.append(texto)
                print("Placa detectada:", texto)

            # --- DESENHAR NO FRAME ---
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, texto, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # --- MOSTRAR VÍDEO EM TEMPO REAL ---
    cv2.imshow("Detecção de Placas", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- FINALIZAR ---
cap.release()
cv2.destroyAllWindows()

print("\n✅ Placas encontradas durante o vídeo:")
print(placas_detectadas)
