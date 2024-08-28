import cv2
from ultralytics import YOLO

class TomatoDetector:
    def __init__(self, model_path):
        # YOLO 모델 로드
        self.model = YOLO(model_path)
        # 웹캠 열기
        self.cap = cv2.VideoCapture(0)

    def detect(self):
        while True:
            # 웹캠에서 프레임 읽기
            ret, frame = self.cap.read()
            if not ret:
                break  # 프레임을 읽지 못하면 루프 종료

            # 모델에 프레임 전달하여 결과 얻기
            results = self.model(frame)

            # 결과를 이미지에 그리기
            im_array = results[0].plot()  # 첫 번째 결과를 가져와서 그리기

            # 익은 토마토 개수와 전체 개수 계산
            ripe_count = sum(1 for result in results[0].boxes if result.cls == 1 and result.conf >= 0.5)  # 익은 토마토 클래스가 1이라고 가정
            total_count = len(results[0].boxes)

            # 바운딩 박스 및 텍스트 추가
            for result in results[0].boxes:
                box = result.xyxy[0]  # 바운딩 박스 좌표
                cls = result.cls  # 클래스
                conf = result.conf  # 신뢰도

                # 익은 토마토인 경우
                if cls == 1 and conf >= 0.5:
                    # 바운딩 박스 그리기
                    cv2.rectangle(im_array, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
                    # "ripe" 텍스트 표시
                    cv2.putText(im_array, "ripe", (int(box[0]), int(box[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # 익지 않은 토마토인 경우
                elif conf < 0.5:
                    # 바운딩 박스 그리기
                    cv2.rectangle(im_array, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), 2)
                    # "unripe" 텍스트 표시
                    cv2.putText(im_array, "unripe", (int(box[0]), int(box[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            return im_array  # 결과 이미지 반환

    def release(self):
        # 웹캠 해제
        self.cap.release()
        cv2.destroyAllWindows()
