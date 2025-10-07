import cv2
import pytesseract

# Ajuste se necessário no Windows

# Carregar o classificador Haar Cascade
cascade_path = "models/haarcascade_russian_plate_number.xml"
placa_cascade = cv2.CascadeClassifier(cascade_path)

if placa_cascade.empty():
    print("Erro ao carregar cascade. Verifique o caminho:", cascade_path)
    exit(1)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar placas
    placas = placa_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    for (x, y, w, h) in placas:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        recorte = gray[y:y + h, x:x + w]

        # Melhorar contraste
        recorte = cv2.equalizeHist(recorte)

        # OCR
        texto = pytesseract.image_to_string(recorte, config="--psm 8")
        texto = texto.strip()

        if texto:
            cv2.putText(frame, texto, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            print("Placa detectada:", texto)

    cv2.imshow("Deteccao de Placas", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
