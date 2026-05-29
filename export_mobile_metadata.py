import json
import joblib
import os

'''flutterda StandardScaler joblib pkl dosyası yok 
o yüzden de feature sırası scale ini falan öğretmemiz gerek

'''


scaler = joblib.load("data/models/tf_scaler.pkl")
#eğitimde kullandığı scaler i açar ve feature isimlerini açar
feature_columns = joblib.load("data/models/tf_feature_columns.pkl")

os.makedirs("data/models/mobile", exist_ok=True)


with open("data/models/mobile/feature_columns.json", "w", encoding="utf-8") as f:
    json.dump(feature_columns, f, indent=4)

scaler_params = {
    
    "mean": scaler.mean_.tolist(),
    "scale": scaler.scale_.tolist()
}

with open("data/models/mobile/scaler_params.json", "w", encoding="utf-8") as f:
    json.dump(scaler_params, f, indent=4)

print("Mobil metadata dosyalari olusturuldu:")
print("data/models/mobile/feature_columns.json")
print("data/models/mobile/scaler_params.json")