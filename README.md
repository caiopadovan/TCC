## Vídeo
The full video I used in this project can be downloaded [here](https://www.pexels.com/video/traffic-flow-in-the-highway-2103099/)

## Order to use
main.py -> filtrando_resultado.py -> visualizar.py

## Summary
This work aimed to develop an automated system for detecting and recognizing vehicle license plates to use them as a way to pay tolls, making the process automatic. 
Computer vision and deep learning techniques were used in the project's development. 
The proposal was implemented in Python, combining the OpenCV and YOLOv8 libraries for object detection, and EasyOCR for optical character recognition (OCR).

The license plate result and vehicle identifier were stored in a JSON file to facilitate communication with the database. This file was generated from the most relevant license plate values ​​obtained from the resultado.CSV file, which contained all the car and license plate information.

Currently, the work is only done with graphics cards in formats such as "AA11AAA", because the video only has this standard, but it is a system that can be adapted to other formats with only minor adjustments.

For future improvements, it is suggested: adapting the code to read more different license plate patterns, implementing it in real time, connected to a camera, 
for practical use in urban monitoring systems or smart tolls, and training the system with different types of test environments, such as low lighting and rainy weather.

## Dependencies
The sort module needs to be downloaded from [this repository](https://github.com/abewley/sort)
