import cv2

def find_camera_index():
    print("SEARCHING FOR IRIUN WEBCAM...")
    # Scan indices 0 to 9
    for index in range(10):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ FOUND CAMERA AT INDEX: {index}")
                print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
                # Optional: Show it briefly to confirm
                cv2.imshow(f"Index {index}", frame)
                cv2.waitKey(1000)
                cv2.destroyAllWindows()
                cap.release()
            else:
                print(f"❌ Index {index} opened but gave no video.")
        else:
            print(f"   Index {index} is empty.")

if __name__ == "__main__":
    find_camera_index()