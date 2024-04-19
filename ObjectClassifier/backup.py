import cvzone
from cvzone.ClassificationModule import Classifier
import cv2
import os
import serial
import serial.tools.list_ports
import time
import pyttsx3

text_engine = pyttsx3.init()


def verify_distance(data):
    data_set = data.split()

    numbers = [int(data_set[0]), float(data_set[1])]

    if (numbers[0] == 0) and 8.80 < numbers[1] < 15:
        # print("Please bring the object closer.")
        text_engine.say("Please bring the object closer.")
        text_engine.runAndWait()
        return False
    elif numbers[0] == 1 and numbers[1] < 8.80:
        return True


ports = serial.tools.list_ports.comports()
ser = serial.Serial()
portsList = []
use = ""

for port in ports:
    portsList.append(str(port))
    print(str(port))

com = input("Select COM Port for Arduino : ")

for i in range(len(portsList)):
    if portsList[i].startswith("COM" + str(com)):
        use = "COM" + str(com)
        print(use)

ser.baudrate = 9600
ser.port = use
ser.open()

# while True:
#     command = input("Arduino Command (Integer Value/reset/exit): ")
#     ser.write(command.encode("utf-8"))
#
#     if command == "exit":
#         exit()
#     elif command == "reset":
#         ser.write("0".encode("utf-8"))

# cv2.VideoCapture(0) - Builtin webcam
# cv2.VideoCapture(1, cv2.CAP_DSHOW) - External webcam
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")

# Importing arrow
imgArrow = cv2.imread("assets/arrow.png", cv2.IMREAD_UNCHANGED)

classIDBin = 0
# Importing waste categories images
imgWasteList = []
pathFolderWaste = "assets/Waste"
pathList = os.listdir(pathFolderWaste)
for path in pathList:
    imgWasteList.append(cv2.imread(os.path.join(pathFolderWaste, path), cv2.IMREAD_UNCHANGED))

# Importing bins images
imgBinsList = []
pathFolderBins = "assets/Bin"
pathList = os.listdir(pathFolderBins)
for path in pathList:
    imgBinsList.append(cv2.imread(os.path.join(pathFolderBins, path), cv2.IMREAD_UNCHANGED))

# 0 - G_M
# 1 - Organic
# 2 - Paper
# 3 - Plastic
# 4 - Other

classDic = {
    0: None,
    1: 0,
    2: 1,
    3: 2,
    4: 3,
    5: 4
}

last_write_time = time.time()

while True:
    arduino_data = ser.readline().decode().strip()
    # print("Data from Arduino:", arduino_data)
    valid = verify_distance(arduino_data)
    print(valid)

    rep, img = cap.read()
    imgResize = cv2.resize(img, (454, 340))

    bgImg = cv2.imread("assets/background.png")

    prediction = classifier.getPrediction(img)

    classID = prediction[1]
    if classID != 0:
        print(classID)
        bgImg = cvzone.overlayPNG(bgImg, imgWasteList[classID - 1], (909, 127))
        bgImg = cvzone.overlayPNG(bgImg, imgArrow, (978, 320))

        classIDBin = classDic[classID]

    if valid:
        if time.time() - last_write_time >= 2:
            # Sending data to arduino
            ser.write(str(classIDBin + 1).encode("utf-8"))
            last_write_time = time.time()  # Update the last write time

    bgImg = cvzone.overlayPNG(bgImg, imgBinsList[classIDBin], (895, 374))

    bgImg[148:148 + 340, 159:159 + 454] = imgResize

    # Displays
    # cv2.imshow("CAM", img)
    cv2.imshow("Waste Classifier", bgImg)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
