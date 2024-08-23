import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

class TomatoDiseaseClassifier:
    def __init__(self, model_path, test_image_path):
        # 모델 로드
        self.model = load_model(model_path)
        self.class_names = ['Blight', 'Healthy', 'Mites', 'Yellow']
        self.test_image_path = "/home/heechun/dev_ws/iot-repo-1/SmartFarmAI/src/mites_suc_01.jpg"

    def run(self):
        # 지정한 이미지를 읽기
        frame = cv2.imread(self.test_image_path)

        # 예측을 위한 초기화
        predicted_class = None

        # 실제 예측 과정
        roi_resized = cv2.resize(frame, (150, 150))
        
        # BGR에서 RGB로 변환
        roi_rgb = cv2.cvtColor(roi_resized, cv2.COLOR_BGR2RGB)
        
        roi_array = image.img_to_array(roi_rgb)
        roi_array = np.expand_dims(roi_array, axis=0)
        roi_array /= 255.0

        predictions = self.model.predict(roi_array)
        predicted_class = np.argmax(predictions, axis=1)
        predicted_label = self.class_names[predicted_class[0]]
        predicted_probabilities = predictions[0]

        # 예측 결과 출력
        cv2.putText(frame, f'Predicted: {predicted_label}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        for i, class_name in enumerate(self.class_names):
            probability = predicted_probabilities[i] * 100
            cv2.putText(frame, f'{class_name}: {probability:.2f}%', (10, 60 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        threshold = 0.5
        if predicted_probabilities[predicted_class[0]] < threshold:
            cv2.putText(frame, 'Prediction Uncertain', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 결과 이미지 보여줌
        cv2.imshow('Predicted Result', frame)

        # 결과를 튜플로 반환
        result_tuple = (predicted_class[0], frame)

        # 결과를 기다리기
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return result_tuple

# 사용 예시
# classifier = TomatoDiseaseClassifier('path/to/your/model.h5', 'path/to/your/test_image.jpg')
# result = classifier.run()
# print(result)
