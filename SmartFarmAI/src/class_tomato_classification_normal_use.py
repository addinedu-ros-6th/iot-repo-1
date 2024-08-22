# CNN / VGG16 모델 사용

from class_tomato_classification_normal import TomatoDiseaseClassifier

if __name__ == "__main__":
    classifier = TomatoDiseaseClassifier('/home/heechun/dev_ws/share_folder/tomato_vgg16_model.h5')
    # classifier = TomatoDiseaseClassifier('/home/heechun/dev_ws/share_folder/tomato_CNN_model.h5')|
    classifier.run()
