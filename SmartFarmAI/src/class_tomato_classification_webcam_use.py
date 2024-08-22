# CNN / VGG16 모델 사용

from class_tomato_classification_webcam import TomatoDiseaseClassifier

if __name__ == "__main__":
    # classifier = TomatoDiseaseClassifier('/home/heechun/dev_ws/share_folder/tomato_webcam_CNN.h5')
    classifier = TomatoDiseaseClassifier('/home/heechun/dev_ws/share_folder/tomato_webcam_vgg.h5')
    classifier.run()
