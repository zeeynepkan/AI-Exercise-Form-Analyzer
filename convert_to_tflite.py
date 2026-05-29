# convert_to_tflite.py

import tensorflow as tf



print("=" * 60)

print("TFLITE DONUSUMU")

print("=" * 60)

# Keras modeli yükle
model = tf.keras.models.load_model(
    "data/models/exercise_tf_model.keras"
)



# Converter
converter = tf.lite.TFLiteConverter.from_keras_model(model)



# Optimize
converter.optimizations = [tf.lite.Optimize.DEFAULT]



# Convert
tflite_model = converter.convert()



# Kaydet
with open("data/models/exercise_model.tflite", "wb") as f:
    f.write(tflite_model)

print("\nTFLite model oluşturuldu:")

print("data/models/exercise_model.tflite")

print("=" * 60)