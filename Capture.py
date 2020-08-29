import cv2, os ,datetime

cam = cv2.VideoCapture(0)
while True:
    ret, frame = cam.read()
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    cv2.imshow("Press Space Bar to captured Image...Please Smile", frame)
    if not ret:
        break
    k = cv2.waitKey(1)

    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_counter = datetime.datetime.now()
        img_counter = img_counter.strftime("%H_%I_%S_%p")
        img_name = "Image_{}.png".format(img_counter)
        cv2.imwrite(os.getcwd() + '/static/images/capturedImages/' + img_name, gray)

cam.release()

cv2.destroyAllWindows() 