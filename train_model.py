# train_model.py

#manual etiketleme yaptıktan sonra modeli eğitme aşaması

import os
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def train_model():

    input_csv = "data/processed/features.csv"

    model_dir = "data/models"

    model_path = os.path.join(model_dir, "exercise_form_model.pkl")


    if not os.path.exists(input_csv):

        print(f"Hata: {input_csv} bulunamadı.")

        return
    

    df = pd.read_csv(input_csv)

    print("=" * 60)

    print("MODEL EGITIMI BASLIYOR")

    print("=" * 60)



    print(f"Toplam veri sayısı: {len(df)}")

    print("Label dağılımı:")

    print(df["form_label"].value_counts())


    if df["form_label"].nunique() < 2:

        print("\nUYARI: Model eğitimi için en az 2 sınıf gerekli.")

        print("Şu anda sadece tek label var.")

        print("Doğru form ve yanlış form verisi toplamalısın.")
        print("Örneğin:")
        print("  squat correct  -> form_label = 1")

        print("  squat incorrect -> form_label = 0")

        return

    X = df.drop(columns=["frame", "exercise_type", "form_label"])

    y = df["form_label"]

    X = X.fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(

        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )


    model = RandomForestClassifier(

        n_estimators=100,
        max_depth=10,
        random_state=42
    )


    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    print("\n" + "=" * 60)

    print("MODEL SONUCLARI")
    print("=" * 60)

    print(f"Accuracy: {accuracy:.4f}")


    print("\nClassification Report:")

    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix:")

    print(confusion_matrix(y_test, y_pred))


    os.makedirs(model_dir, exist_ok=True)

    joblib.dump(

        {
            "model": model,
            "feature_columns": list(X.columns)
        },

        model_path
    )


    print("\n" + "=" * 60)


    print(f"Model kaydedildi: {model_path}")
    print("=" * 60)
    


if __name__ == "__main__":
    train_model()