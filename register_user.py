import tkinter as tk
from tkinter import messagebox
import cv2
import os
from firebase_config import initialize_firebase  # Firebase 초기화 함수 가져오기
import firebase_admin
from firebase_admin import db, storage

# Firebase 초기화
initialize_firebase()

def upload_image_to_firebase(image_path, student_id, user_name, image_index):
    bucket = storage.bucket()
    blob = bucket.blob(f"user_faces/{student_id}_{user_name}_{image_index}.jpg")
    blob.upload_from_filename(image_path)
    return blob.public_url

def capture_and_register_face(student_id, user_name):
    cap = cv2.VideoCapture(0)  # 기본 카메라
    if not cap.isOpened():
        messagebox.showerror("오류", "카메라를 활성화할 수 없습니다.")
        return

    image_index = 0  # 이미지 인덱스 초기화
    total_images = 50  # 총 캡처할 이미지 수

    while image_index < total_images:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("오류", "카메라에서 이미지를 읽을 수 없습니다.")
            break
        cv2.imshow("Capture Face", frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):  # 's' 키를 누르면 캡처
            face_img = frame  # 이 부분에 얼굴 검출 및 저장 로직 추가
            if not os.path.exists("user_faces"):
                os.makedirs("user_faces")
            image_path = f"user_faces/{student_id}_{user_name}_{image_index}.jpg"
            cv2.imwrite(image_path, face_img)  # 파일 저장
            image_url = upload_image_to_firebase(image_path, student_id, user_name, image_index)
            user_ref = db.reference('users')
            user_ref.child(student_id).child(user_name).child(f'image_{image_index}').set({'image_url': image_url})
            image_index += 1
            print(f"Captured {image_index}/{total_images} images")  # 콘솔에 진행 상황 출력

        if image_index >= total_images:
            break

    cap.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("캡처 완료", f"총 {total_images} 장의 얼굴이 성공적으로 캡처되었습니다.")

def register_user():
    student_id = entry_id.get()
    user_name = entry_name.get()
    if not student_id or not user_name:
        messagebox.showerror("입력 오류", "학번과 사용자 이름을 모두 입력해주세요.")
        return
    capture_and_register_face(student_id, user_name)
    messagebox.showinfo("등록 완료", "사용자가 성공적으로 등록되었습니다.")

# GUI 창 설정
app = tk.Tk()
app.title("얼굴 인식 출석체크 시스템")
app.geometry("300x250")

# 사용자 학번 및 이름 입력 및 안내 문구
tk.Label(app, text="학번과 이름을 입력하시면 카메라가 활성화 됩니다", font=("Arial", 10)).pack(pady=10)
tk.Label(app, text="학번:").pack()
entry_id = tk.Entry(app)
entry_id.pack()
tk.Label(app, text="사용자 이름:").pack()
entry_name = tk.Entry(app)
entry_name.pack()

# 등록 버튼
register_button = tk.Button(app, text="등록", command=register_user)
register_button.pack(pady=20)

app.mainloop()
