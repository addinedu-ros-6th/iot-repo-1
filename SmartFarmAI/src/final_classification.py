import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

class TomatoDiseaseClassifier:
    def __init__(self, model_path):
        # 모델 로드
        self.model = load_model(model_path)
        self.class_names = ['Blight', 'Healthy', 'Mites', 'Yellow']
        self.cap = cv2.VideoCapture(0)
        self.start_point = None
        self.end_point = None
        self.drawing = False

        # 마우스 콜백 설정
        cv2.namedWindow('Webcam')
        cv2.setMouseCallback('Webcam', self.mouse_callback)
        # cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_SILENT)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_point = (x, y)
            self.drawing = True
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_point = (x, y)

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            predicted_class = None  # 초기화

            # 드래그한 영역을 그리기
            if self.start_point and self.end_point:
                cv2.rectangle(frame, self.start_point, self.end_point, (0, 255, 0), 2)

                x_min = min(self.start_point[0], self.end_point[0])
                x_max = max(self.start_point[0], self.end_point[0])
                y_min = min(self.start_point[1], self.end_point[1])
                y_max = max(self.start_point[1], self.end_point[1])

                roi_cropped = frame[y_min:y_max, x_min:x_max]

                if roi_cropped.size > 0:
                    roi_resized = cv2.resize(roi_cropped, (150, 150))
                    
                    # BGR에서 RGB로 변환
                    roi_rgb = cv2.cvtColor(roi_resized, cv2.COLOR_BGR2RGB)
                    
                    roi_array = image.img_to_array(roi_rgb)
                    roi_array = np.expand_dims(roi_array, axis=0)
                    roi_array /= 255.0

                    predictions = self.model.predict(roi_array)
                    predicted_class = np.argmax(predictions, axis=1)
                    predicted_label = self.class_names[predicted_class[0]]
                    predicted_probabilities = predictions[0]

                    cv2.putText(frame, f'Predicted: {predicted_label}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                    for i, class_name in enumerate(self.class_names):
                        probability = predicted_probabilities[i] * 100
                        cv2.putText(frame, f'{class_name}: {probability:.2f}%', (10, 60 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    threshold = 0.5
                    if predicted_probabilities[predicted_class[0]] < threshold:
                        cv2.putText(frame, 'Prediction Uncertain', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    cv2.imshow('ROI', roi_cropped)

            cv2.imshow('Webcam', frame)

            
            # 분류 결과와 프레임 정보를 튜플로 반환
            if predicted_class is not None:
                result_tuple = (predicted_class[0], frame)  # predicted_class와 frame을 튜플로 저장
                return result_tuple
                # print(result_tuple)  # 실시간으로 튜플 결과 출력

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            
        
        self.cap.release()
        cv2.destroyAllWindows()

# 사용 예시
# classifier = TomatoDiseaseClassifier('path/to/your/model.h5')
# classifier.run()

