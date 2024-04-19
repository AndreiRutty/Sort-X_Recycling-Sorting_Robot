import cvzone
from cvzone.ClassificationModule import Classifier
import cv2
import os
import serial
import serial.tools.list_ports
import time
import pyttsx3
import threading

text_engine = pyttsx3.init()


# Function to verify the distance from sensor to object
def verify_distance(data):
    # Data will be received as "{number 1} {number2}"
    # number 1 - data from the IR Sensor (either 0 or 1)
    # number 2 - data from the Ultrasonic Sensor (double)

    # Splitting the data
    data_set = data.split()

    # Add the data to a list
    numbers = [int(data_set[0]), float(data_set[1])]
    print(data_set)

    # Checking if the object is within acceptable range
    if (numbers[0] == 1) and 8.80 < numbers[1] < 15:
        # An object has been detected but not within the acceptable range
        # IR sensor cannot detect and confirm object presence.
        # Alarm the user to bring the object closer
        text_engine.say("Please bring the object closer.")
        text_engine.runAndWait()
        return False
    elif numbers[0] == 0 and numbers[1] < 8.80:
        # The IR sensor has detected and confirmed the presence of an object
        # The ultrasonic data is within acceptable range
        # Alarm the user that an object has been detected
        text_engine.say("Object Detected")
        text_engine.runAndWait()
        return True


# Get a list of available serial ports from device
ports = serial.tools.list_ports.comports()
# Initializing a Serial object
ser = serial.Serial()
# Available ports list
portsList = []
use = ""

print("Available ports:")
# Iterating through every port
for port in ports:
    count = 1
    # Adding port to the port list and printing the port
    portsList.append(str(port))
    print(f"{count}. {str(port)}")
    count += 1

# Taking user input for COM port
com = input("Select COM Port for Arduino : ")

for i in range(len(portsList)):
    # Checking if user input for COM Port exists
    if portsList[i].startswith("COM" + str(com)):
        # If it exists, then assign the port name to use
        use = "COM" + str(com)
        print(f"{use} is being used. Successfull connection")

# Setting baud rate for serial communication
ser.baudrate = 9600
# Setting port for serial communication
ser.port = use
# Opening the serial connection
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

classifier = Classifier("Model/keras_model4.h5", "Model/labels.txt")

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

# Global variable
valid = False


# Function to communicate with Arduino to receive data
def serial_thread():
    # accessing global variable "valid"
    global valid

    # While the program hasn't been stopped or connection aborted,
    # keep fetching data from arduino
    while True:
        # Reading data from Arduino and decode
        arduino_data = ser.readline().decode().strip()
        # Verify distance with data from Arduino and update value of valid
        valid = verify_distance(arduino_data)
        # Pausing the thread to avoid consuming too much CPU power
        time.sleep(0.1)


# Creating thread object with the function
serial_thread = threading.Thread(target=serial_thread, daemon=True)

# Starting the thread
serial_thread.start()

while True:
    # Capturing frames from the camera
    rep, img = cap.read()

    # Resize the frame size and add a background image
    imgResize = cv2.resize(img, (454, 340))
    bgImg = cv2.imread("assets/background.png")

    # Get a prediction from the classifier based on the frame
    prediction = classifier.getPrediction(img)

    # Getting the class id from the prediction results
    classID = prediction[1]

    # Checking if classID is not 0
    # 0 indicates nothing i.e. no object is presented
    if classID != 0:

        # Overlay specific images based on the class ID
        bgImg = cvzone.overlayPNG(bgImg, imgWasteList[classID - 1], (909, 127))
        bgImg = cvzone.overlayPNG(bgImg, imgArrow, (978, 320))

        # Getting the id of the bin from a dictionary depending on classID
        classIDBin = classDic[classID]

    # If the detected object was placed within acceptable range,
    # Send Bin ID to Arduino Board
    if valid:
        # Checking for a timelaps of 2 seconds:
        # Giving time for the classifier to be sure about the prediction
        if time.time() - last_write_time >= 2:
            # Sending encoded data to arduino
            ser.write(str(classIDBin + 1).encode("utf-8"))
            # Print bin id
            print(f"-----------Bin: {classIDBin + 1}---------------")
            last_write_time = time.time()  # Update the last write time

    # Overlay an image of the corresponding bin
    bgImg = cvzone.overlayPNG(bgImg, imgBinsList[classIDBin], (895, 374))
    bgImg[148:148 + 340, 159:159 + 454] = imgResize

    # Displays
    # cv2.imshow("CAM", img)
    cv2.imshow("Waste Classifier", bgImg)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
