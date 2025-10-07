import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

caminho = "models/haarcascade_russian_plate_number.xml"
cascade = cv2.CascadeClassifier(caminho)

img = cv2.imread("imgs/Placa3.jpg")
img_cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Detecta a placa
placas = cascade.detectMultiScale(img_cinza, scaleFactor=1.1, minNeighbors=4, minSize=(30,30))

if len(placas) == 0:
    print("Nenhuma placa detectada!")
else:
    for (x, y, w, h) in placas:
        placa_img = img_cinza[y:y+h, x:x+w]

        # Remove borda (5%)
        h_img, w_img = placa_img.shape
        margem = 0.05
        placa_img = placa_img[int(h_img*margem):int(h_img*(1-margem)),
                              int(w_img*margem):int(w_img*(1-margem))]
        
        # Reduz ruído sem borrar bordas
        placa_img = cv2.bilateralFilter(placa_img, 9, 75, 75)
        
        # Aumenta contraste e brilho
        placa_img = cv2.convertScaleAbs(placa_img, alpha=1.5, beta=20)

        _,placa_img = cv2.threshold(placa_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Redimensiona a imagem
        placa_img = cv2.resize(placa_img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        # Suaviza para reduzir ruidos
        placa_img = cv2.medianBlur(placa_img, 3)

        # Código para aceitar apenas números e letras e tentar detectar apenas uma pálavra
        placa_texto = pytesseract.image_to_string(placa_img,config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        placa_texto = ''.join(filter(str.isalnum, placa_texto))

        # Remove caracteres diferentes e normaliza
        placa_texto = re.sub(r'[^A-Z0-9]', '', placa_texto.upper())
        if len(placa_texto) > 7:
            placa_texto = placa_texto[-7:]

        print("Placa detectada:", placa_texto)

        # Faz um retângulo em volta da placa
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Carro", img)
    cv2.imshow("Placa Detectada", placa_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
