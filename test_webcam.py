import cv2

cap = cv2.VideoCapture(0)

if cap.isOpened():
    print("✅ Webcam Found!")
    ret, frame = cap.read()
    if ret:
        print("✅ Frame captured!")
        cv2.imshow('Test', frame)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()
    else:
        print("❌ Frame capture failed!")
else:
    print("❌ Webcam NOT found!")

cap.release()