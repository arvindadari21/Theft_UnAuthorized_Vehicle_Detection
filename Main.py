# Main.py

import cv2
import numpy as np
import os
import time
from datetime import datetime, timedelta

import DetectChars
import DetectPlates
import pytesseract as tess
import PossiblePlate
from check_database import Database
from send_mail import _send_mail
from send_sms import _send_sms

# module level variables ##########################################################################
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)
THEFT = 1
UNAUTHORIZED = 2
AUTHORIZED = 3

showSteps = False


###################################################################################################
def detect_number(_file, vehicle_data):
    notified = True
    blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()  # attempt KNN training

    if blnKNNTrainingSuccessful == False:  # if KNN training was not successful
        print("\nerror: KNN traning was not successful\n")  # show error message
        return  # and exit program
    # end if

    imgOriginalScene = cv2.imread(_file)  # open image

    if imgOriginalScene is None:  # if image was not read successfully
        print("\nerror: image not read from file \n\n")  # print error message to std out
        os.system("pause")  # pause so user can see error message
    # end if

    listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)  # detect plates

    listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)  # detect chars in plates

    # cv2.imshow("imgOriginalScene", imgOriginalScene)  # show scene image

    if len(listOfPossiblePlates) == 0:  # if no plates were found
        print("\nno license plates were detected\n")  # inform user no plates were found
    else:  # else
        # if we get in here list of possible plates has at leat one plate

        # sort the list of possible plates in DESCENDING order (most number of chars to least number of chars)
        listOfPossiblePlates.sort(key=lambda possiblePlate: len(possiblePlate.strChars), reverse=True)

        # suppose the plate with the most recognized chars (the first plate in sorted by string length descending order) is the actual plate
        licPlate = listOfPossiblePlates[0]

        # cv2.imshow("imgPlate", licPlate.imgPlate)  # show crop of plate and threshold of plate
        # cv2.imshow("imgThresh", licPlate.imgThresh)
        # text = tess.image_to_string(licPlate.imgPlate, lang='eng')
        # print("Tesseract imgPlate: ", text)

        if len(licPlate.strChars) == 0:  # if no chars were found in the plate
            print("\nno characters were detected\n\n")  # show message

        drawRedRectangleAroundPlate(imgOriginalScene, licPlate)  # draw red rectangle around plate

        print(
            "\nlicense plate read from image = " + licPlate.strChars + "\n")  # write license plate text to std out
        print("----------------------------------------")

        vehicle_number = licPlate.strChars.strip()
        print("Vehicle Number:", vehicle_number, "---")
        vehicle_type = Database.number_exists(vehicle_number)
        dt = datetime.now()
        print("Vehicle type:", vehicle_type, "---")
        if vehicle_type == THEFT:
            if vehicle_number not in vehicle_data:
                print(
                    "Entered registration number: {} exists in database as {} vehicle".format(
                        vehicle_number,
                        'theft' if vehicle_type == THEFT else 'unauthorized'))
                print(
                    "Identified the vehicle with registration number: {} at S.R. Nagar signal point at: {}".format(
                        vehicle_number, datetime.now()))
                vehicle_data.update({vehicle_number: 1})
            else:
                vehicle_data[vehicle_number] += 1
                cnt = vehicle_data.get(vehicle_number)
                if cnt > 1:
                    dt = datetime.now()
                    print(
                        "Identified the same vehicle 2nd time with registration number: {} at Ameerpet signal point at: {}".format(
                            vehicle_number, dt))
                    print(
                        "Informing the authorities in the nearest possible routes of current location (Ameerpet)")
                    # Sending Mail
                    _send_mail(vehicle_number, vehicle_type, dt)
                    # Sending SMS
                    # _send_sms(vehicle_number, vehicle_type, dt)
                    notified = False
        elif vehicle_type == AUTHORIZED:
            print("Found registration number: {} is authorized".format(vehicle_number))
        elif vehicle_type == UNAUTHORIZED:
            print("Found registration number: {} does not exist in database, it is an un-authorized vehicle".format(
                vehicle_number))
            # Sending Mail
            _send_mail(vehicle_number, vehicle_type, dt)
            # Sending SMS
            # _send_sms(vehicle_number, vehicle_type, dt)
        else:
            print("Entered registration number: {} does not exist in records".format(vehicle_number))

        writeLicensePlateCharsOnImage(imgOriginalScene, licPlate)  # write license plate text on the image

        # cv2.imshow("imgOriginalScene", imgOriginalScene)  # re-show scene image

        cv2.imwrite("imgOriginalScene.png", imgOriginalScene)  # write image out to file

    time.sleep(5)

    return notified, vehicle_data


# end main

###################################################################################################
def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):
    p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)  # get 4 vertices of rotated rect

    cv2.line(imgOriginalScene, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), SCALAR_RED, 2)  # draw 4 red lines
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), SCALAR_RED, 2)


# end function

###################################################################################################
def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
    ptCenterOfTextAreaX = 0  # this will be the center of the area the text will be written to
    ptCenterOfTextAreaY = 0

    ptLowerLeftTextOriginX = 0  # this will be the bottom left of the area that the text will be written to
    ptLowerLeftTextOriginY = 0

    sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

    intFontFace = cv2.FONT_HERSHEY_SIMPLEX  # choose a plain jane font
    fltFontScale = float(plateHeight) / 30.0  # base font scale on height of plate area
    intFontThickness = int(round(fltFontScale * 1.5))  # base font thickness on font scale

    textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale,
                                         intFontThickness)  # call getTextSize

    # unpack roatated rect into center point, width and height, and angle
    ((intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight),
     fltCorrectionAngleInDeg) = licPlate.rrLocationOfPlateInScene

    intPlateCenterX = int(intPlateCenterX)  # make sure center is an integer
    intPlateCenterY = int(intPlateCenterY)

    ptCenterOfTextAreaX = int(intPlateCenterX)  # the horizontal location of the text area is the same as the plate

    if intPlateCenterY < (sceneHeight * 0.75):  # if the license plate is in the upper 3/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(
            round(plateHeight * 1.6))  # write the chars in below the plate
    else:  # else if the license plate is in the lower 1/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(
            round(plateHeight * 1.6))  # write the chars in above the plate
    # end if

    textSizeWidth, textSizeHeight = textSize  # unpack text size width and height

    ptLowerLeftTextOriginX = int(
        ptCenterOfTextAreaX - (textSizeWidth / 2))  # calculate the lower left origin of the text area
    ptLowerLeftTextOriginY = int(
        ptCenterOfTextAreaY + (textSizeHeight / 2))  # based on the text area center, width, and height

    # write the text on the image
    cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace,
                fltFontScale, SCALAR_YELLOW, intFontThickness)


# end function

def main():
    vehicle_data = {}
    notified = True
    while notified:
        for dir, sub_dir, files in os.walk(
                r'D:\hackthon softwares\OpenCV_3_License_Plate_Recognition_Python\FinalImages'):
            for _file in files:
                file_name = os.path.join(dir, _file)
                print("Processing image: ", file_name)
                notified, vehicle_data = detect_number(file_name, vehicle_data)


###################################################################################################
if __name__ == "__main__":
    main()
