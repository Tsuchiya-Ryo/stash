import numpy as np
import cv2

import math
import pyautogui

# initialize direction
center = True
right = False
left =False
up = False
down=False

# calc for poly2d from convexhull coordinates
def calcpoly(pts):
    lines = np.hstack([pts,np.roll(pts,-1,axis=0)])
    area = 0.5*abs(sum(x1*y2-x2*y1 for x1,y1,x2,y2 in lines))
    return area

# Open Camera
capture = cv2.VideoCapture(0)
count = 0
while capture.isOpened():

    # Capture frames from the camera
    count += 1
    ret, frame = capture.read()
    if count % 5 == 0:
        
        # Get hand data from the rectangle sub window
        cv2.rectangle(frame, (100, 100), (600, 400), (0, 255, 0), 0)
        crop_image = frame[100:400, 100:600]
        # cv2.imwrite("original.jpg", crop_image)
        cv2.rectangle(crop_image, (80,70),(400,240), (0,255,0), 0)

        # Apply Gaussian blur

        blur = cv2.GaussianBlur(crop_image, (3, 3), 0)

        # Change color-space from BGR -> HSV
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

        # Create a binary image with where white will be skin colors and rest is black
        mask2 = cv2.inRange(hsv, np.array([2, 0, 0]), np.array([20, 255, 255]))
                                                                                                # cv2.imwrite("mask.jpg", mask2)
        # Kernel for morphological transformation
        kernel = np.ones((5, 5))

        # Apply morphological transformations to filter out the background noise
        dilation = cv2.dilate(mask2, kernel, iterations=1)
        erosion = cv2.erode(dilation, kernel, iterations=1)
                                                                                                # cv2.imwrite("dilation.jpg", dilation)
                                                                                                # cv2.imwrite("erosion.jpg", erosion)
        # Kernel for morphological transf
        # Kernel for morphological transf
        # Apply Gaussian Blur and Threshold
        filtered = cv2.GaussianBlur(erosion, (3, 3), 0)
                                                                                                # cv2.imwrite("filtereed.jpg", filtered)
        ret, thresh = cv2.threshold(filtered, 127, 255, 0)

    #####
        # Find contours

        contours, hierachy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        try:
            # Find contour with maximum area
            contour = max(contours, key=lambda x: cv2.contourArea(x))

            # Create bounding rectangle around the contour
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(crop_image, (x, y), (x + w, y + h), (0, 0, 255), 0)

            # Find convex hull
            # calc convex area

            hull = cv2.convexHull(contour, clockwise=True, returnPoints=True)
            pts = [x[0].tolist() for x in hull]
            convexarea = calcpoly(pts)

            moments = cv2.moments(contour)
            if moments["m00"] != 0:
                cx = int(moments["m10"]/moments["m00"])
                cy = int(moments["m01"]/moments["m00"])

            centerMass=(cx, cy)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.circle(crop_image,(cx,cy),7,[100,0,255],2)

            if count % 5 == 0:

                if cx > 400 and center==True:
                    center=False
                    left=True

                elif cx < 80 and center==True:   
                    center=False
                    right=True

                elif cy >240 and center==True:             
                    center=False
                    down=True

                elif cy < 70 and center==True:        
                    center=False
                    up=True

                else:
                    center = True
                    up=False
                    down=False
                    right=False
                    left=False

                # Draw contour
                drawing = np.zeros(crop_image.shape, np.uint8)
                cv2.drawContours(drawing, [contour], -1, (0, 255, 0), 0)
                cv2.drawContours(drawing, [hull], -1, (0, 0, 255), 0)

                # Fi convexity defects
                hull = cv2.convexHull(contour, returnPoints=False)
                defects = cv2.convexityDefects(contour, hull)
                
                # Use cosine rule to find angle of the far point from the start and end point i.e. the convex points (the finger
                # tips) for all defects
                count_defects = 0
                trianglesarea = 0
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(contour[s][0])
                    end = tuple(contour[e][0])
                    far = tuple(contour[f][0])

                    a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                    b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                    s = (a+b+c)/2
                    area = 1/2* math.sqrt(s*(s-a)*(s-b)*(s-c))
                    angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14
                    trianglesarea += area

                    # if angle >= 90 draw a circle at the far point
                    if angle <= 90:
                        count_defects += 1
                        cv2.circle(crop_image, far, 1, [0, 0, 255], -1)

                    cv2.line(crop_image, start, end, [0, 255, 0], 2)
                
                # ratio = (convexarea-trianglesarea)/convexarea
                # ratio = cv2.contourArea(contour)/convexarea
     
                # Press SPACE if condition is match
                if count_defects >= 4:
                    pyautogui.press('r')
                    cv2.putText(frame, "R-Spin", (115, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)
                elif count_defects ==2:
                    pyautogui.press("l")
                    cv2.putText(frame, "L-Spin", (115, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)
                elif right == True:
                    pyautogui.press("d")
                    cv2.putText(frame, "Right", (115, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)
                elif left == True:
                    pyautogui.press('a')
                    cv2.putText(frame, "left", (115, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)
                elif up == True:
                    pyautogui.press("w")
                    cv2.putText(frame, "Hold", (115, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)
                elif down == True:
                    pyautogui.press("s")
                    cv2.putText(frame, "Hard Drop", (115, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)

                # add some finger signs

                # elif count_defects == 1 and ratio > 0.89 and ratio < 9.5:
                #     cv2.putText(frame, "Thumb Up", (115, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)
                # elif count_defects == 1 and ratio > 0.81 and ratio < 0.85:
                #     cv2.putText(frame, "Finger Gun", (115, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)

                # neutral (if needed)
                # else:
                #     cv2.putText(frame, "Neutral", (115, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, 2, 2)

        except:
            pass

        # Show required images
        cv2.imshow("Gesture", frame)

        # Close the camera if 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

capture.release()
cv2.destroyAllWindows()