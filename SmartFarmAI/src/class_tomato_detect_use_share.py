import cv2
from ultralytics import YOLO
from class_tomato_detect import TomatoDetector  # TomatoDetector 클래스를 임포트합니다.

if __name__ == "__main__":
    model_path = '/home/heechun/dev_ws/detect_tomato/trained_model.pt'  # YOLO 모델 파일 경로를 설정하세요.
    detector = TomatoDetector(model_path)

    while True:
        # 감지 결과 얻기
        result_image = detector.detect()

        # 결과 이미지를 화면에 표시
        cv2.imshow("Tomato Detection", result_image)

        # 'q' 키를 눌러 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 리소스 해제
    detector.release()
