# CNN / VGG16 모델 사용

from final_classification import TomatoDiseaseClassifier

if __name__ == "__main__":
    classifier = TomatoDiseaseClassifier('tomato_vgg16_model.h5')
    classifier.run()
