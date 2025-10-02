import cv2

cascade_path = "cascade/haarcascade_russian_plate_number.xml"
placa_cascade = cv2.CascadeClassifier(cascade_path)

img = cv2.imread("imgs/Placa-Mercosul-3.jpg")
imgcinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
placas = placa_cascade.detectMultiScale(imgcinza)

print(placas)


for (x, y, w, h) in placas:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow("Placa", img)
cv2.waitKey()