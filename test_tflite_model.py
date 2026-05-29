# test_tflite_model.py

import numpy as np
import tensorflow as tf
import pandas as pd
import joblib

print("=" * 60)
print("TFLITE MODEL TESTI")
print("=" * 60)

# TFLite model yükle
interpreter = tf.lite.Interpreter(
    model_path="data/models/exercise_model.tflite"
)

interpreter.allocate_tensors()

# Input / output detayları
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("\nInput detayları:")
print(input_details)

print("\nOutput detayları:")
print(output_details)

# Feature kolonları
feature_columns = joblib.load(
    "data/models/tf_feature_columns.pkl"
)

# Scaler
scaler = joblib.load(
    "data/models/tf_scaler.pkl"
)

# Datasetten örnek veri al
df = pd.read_csv("data/processed/features.csv")

X = df.drop(columns=["form_label"])

if "exercise_type" in X.columns:
    X = pd.get_dummies(X, columns=["exercise_type"])

X = X.fillna(0)

# Eksik kolon kontrolü
for col in feature_columns:
    if col not in X.columns:
        X[col] = 0

X = X[feature_columns]

# İlk örnek
sample = X.iloc[0].values.reshape(1, -1)

# Scale
sample_scaled = scaler.transform(sample)

# Float32 çevir
sample_scaled = sample_scaled.astype(np.float32)

# Input ver
interpreter.set_tensor(
    input_details[0]["index"],
    sample_scaled
)

# Çalıştır
interpreter.invoke()

# Sonuç al
output_data = interpreter.get_tensor(
    output_details[0]["index"]
)

prediction = output_data[0][0]

print("\nTahmin sonucu:")
print(prediction)

if prediction > 0.5:
    print("Tahmin: CORRECT FORM")
else:
    print("Tahmin: INCORRECT FORM")

print("\nTFLite model başarıyla çalıştı.")
print("=" * 60)