import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import requests
from PIL import Image
from io import BytesIO
from firebase_config import initialize_firebase  # Firebase 초기화 함수 가져오기
import firebase_admin
from firebase_admin import db

# Firebase 초기화
initialize_firebase()

def load_user_faces():
    user_ref = db.reference('users')
    users = user_ref.get()
    user_faces = {}
    for user_name, user_data in users.items():
        response = requests.get(user_data['image_url'])
        img_array = np.array(Image.open(BytesIO(response.content)))
        gray_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        user_faces[user_name] = gray_img
    return user_faces

def recognize_face():
    user_faces = load_user_faces()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("오류", "카메라를 활성화할 수 없습니다.")
        return
    recognized = False
    while not recognized:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("오류", "카메라에서 이미지를 읽을 수 없습니다.")
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            face_img = gray[y:y+h, x:x+w]
            for user_name, user_face in user_faces.items():
                result = cv2.matchTemplate(face_img, user_face, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                if max_val > 0.7:  # 임계값 설정
                    cv2.putText(frame, user_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    messagebox.showinfo("출석 완료", f"{user_name}님, 출석이 완료되었습니다.")
                    recognized = True
                    break
        cv2.imshow("Recognize Face", frame)
        if recognized or cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# GUI 창 설정
app = tk.Tk()
app.title("얼굴 인식 출석체크 시스템")
app.geometry("300x200")

# 얼굴 인식 버튼
recognize_button = tk.Button(app, text="얼굴 인식 시작", command=recognize_face)
recognize_button.pack()

app.mainloop()
