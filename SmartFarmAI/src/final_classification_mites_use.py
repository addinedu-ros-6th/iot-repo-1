# Mites 제어동작 확인용

from final_classification_mites import TomatoDiseaseClassifier

if __name__ == "__main__":
    classifier = TomatoDiseaseClassifier(
    '/home/heechun/dev_ws/iot-repo-1/SmartFarmAI/src/tomato_vgg16_model.h5',
    '/home/heechun/dev_ws/iot-repo-1/SmartFarmAI/src/mites_suc_01.jpg'  # 여기에 테스트할 이미지의 경로를 입력하세요.
)
    classifier.run()
