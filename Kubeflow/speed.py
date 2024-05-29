# TensorFlow 및 기타 라이브러리 임포트
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
import time
from tensorflow.keras.utils import plot_model
import matplotlib.pyplot as plt

# TensorFlow가 GPU를 인식하는지 확인 
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        device_name = '/GPU:0'
        print(f"Using GPU: {gpus}")
    except RuntimeError as e:
        print(e)
else:
    device_name = '/CPU:0'
    print("No GPUs detected. Using CPU.")

# CIFAR-10 데이터셋 로드
(X_train, y_train), (X_test, y_test) = tf.keras.datasets.cifar10.load_data()

# 데이터 정규화
X_train = X_train / 255.0
X_test = X_test / 255.0

# 모델 정의
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(32, 32, 3)),
    MaxPooling2D((2, 2), padding='same'),
    Conv2D(64, (3, 3), activation='relu', padding='same'),
    MaxPooling2D((2, 2), padding='same'),
    Conv2D(128, (3, 3), activation='relu', padding='same'),
    MaxPooling2D((2, 2), padding='same'),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(10, activation='softmax')
])

# 모델 구조 요약 출력
model.summary()

# 모델 컴파일
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# TensorBoard 설정
log_dir = "logs/fit/" + time.strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

# 학습 시간 측정 및 학습 진행
start_time = time.time()
with tf.device(device_name):  # GPU 또는 CPU 사용 설정
    history = model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1, callbacks=[tensorboard_callback])
end_time = time.time()

print(f"Training time on {device_name}: {end_time - start_time:.2f} seconds")

# 테스트 데이터로 모델 평가
print("Evaluating model...")
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=2)
print(f"Test accuracy on {device_name}: {test_acc * 100:.2f}%")

# 학습 곡선 시각화
plt.plot(history.history['loss'], label='loss')
plt.plot(history.history['accuracy'], label='accuracy')
plt.xlabel('Epoch')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.title('Training Loss and Accuracy')
plt.show()

# TensorBoard 시작 방법 출력
print(f"Run the following command to see TensorBoard logs:\n\ntensorboard --logdir {log_dir}")
