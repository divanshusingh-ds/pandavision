import cv2

print("📷 Opening webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Webcam NOT found!")
else:
    print("✅ Webcam opened! Showing preview...")
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Webcam Test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print("👋 Done!")