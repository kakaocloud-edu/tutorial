import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
import os

def train_model(learning_rate=0.001, batch_size=32):
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0
    
    model = Sequential([
        Flatten(input_shape=(28, 28)),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')
    ])

    model.compile(optimizer=Adam(learning_rate=learning_rate),
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    model.fit(x_train, y_train, epochs=5, batch_size=batch_size, validation_data=(x_test, y_test))

    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
    print('\nTest learning_rate:', learning_rate)
    print('\nTest batch_size:', batch_size)
    print('\nTest accuracy:', test_acc)

    # Log metrics to a file in the expected format
    with open('/tmp/mnist.log', 'w') as f:
        f.write(f"{{metricName: accuracy, metricValue: {test_acc}}}\n")

    return test_acc

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--learning_rate', type=float, default=0.001)
    parser.add_argument('--batch_size', type=int, default=32)

    args = parser.parse_args()

    train_model(learning_rate=args.learning_rate, batch_size=args.batch_size)
