import firebase_admin
from firebase_admin import credentials, db, storage

# Firebase 초기화 함수
def initialize_firebase():
    # 서비스 계정 키 파일 경로
    cred = credentials.Certificate('serviceAccountKey.json')  # 서비스 계정 키 파일의 경로를 입력하세요.

    # Firebase 초기화
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://face-recognition-979ca-default-rtdb.firebaseio.com',  # Firebase Realtime Database URL
        'storageBucket': 'face-recognition-979ca.appspot.com'  # Firebase Storage 버킷 URL
    })
