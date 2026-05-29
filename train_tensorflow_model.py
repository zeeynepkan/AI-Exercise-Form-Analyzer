# train_tensorflow_model.py

#projeyi fluttera taşımak için bu şekilde eğittim tekrardan tensorflow ile

import os
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib


from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping



print("=" * 60)

print("TENSORFLOW MODEL EGITIMI")
print("=" * 60)



# Dataset yükle
df = pd.read_csv("data/processed/features.csv")


print(f"\nToplam veri sayısı: {len(df)}")


# Hedef değişken
y = df["form_label"]


# Feature alanları
X = df.drop(columns=["form_label"])


# exercise_type kategorik olduğu için one-hot encoding yapıyorum
if "exercise_type" in X.columns:
    X = pd.get_dummies(X, columns=["exercise_type"])



# Eksik değerleri temizle
X = X.fillna(0)


print("\nLabel dağılımı:")

print(y.value_counts())

print("\nFeature sayısı:")

print(X.shape[1])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# Standardizasyon
scaler = StandardScaler()



X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


# Model
model = Sequential([

    Input(shape=(X_train_scaled.shape[1],)),

    Dense(128, activation="relu"),
    Dropout(0.2),

    Dense(64, activation="relu"),
    Dropout(0.2),

    Dense(32, activation="relu"),

    Dense(1, activation="sigmoid")
])


model.compile(

    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)


# Early stopping
early_stop = EarlyStopping(

    monitor="val_loss",
    patience=10,
    restore_best_weights=True
)


print("\nModel eğitiliyor...\n")


history = model.fit(

    X_train_scaled,
    y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=16,
    callbacks=[early_stop],
    verbose=1
)


# Test
loss, accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)


print("\n" + "=" * 60)

print("MODEL SONUCLARI")

print("=" * 60)

print(f"Accuracy: {accuracy:.4f}")


# Prediction
y_pred_prob = model.predict(X_test_scaled)

y_pred = (y_pred_prob > 0.5).astype(int).flatten()


print("\nClassification Report:")

print(classification_report(y_test, y_pred, zero_division=0))


print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))


# Klasör oluştur
os.makedirs("data/models", exist_ok=True)



# Model kaydet
model.save("data/models/exercise_tf_model.keras")
model.save("data/models/exercise_tf_model.h5")



# Scaler ve feature column bilgisini kaydet
joblib.dump(

    scaler,
    "data/models/tf_scaler.pkl"
)


joblib.dump(

    list(X.columns),
    "data/models/tf_feature_columns.pkl"
)


print("\n" + "=" * 60)

print("TensorFlow modeli kaydedildi:")

print("data/models/exercise_tf_model.keras")

print("data/models/exercise_tf_model.h5")

print("Scaler kaydedildi:")

print("data/models/tf_scaler.pkl")

print("Feature kolonlari kaydedildi:")

print("data/models/tf_feature_columns.pkl")

print("=" * 60)