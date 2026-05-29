
import json
import os
import tensorflow as tf


#TensorFlow model ağırlıklarını JSON formatına export etmek için 
model = tf.keras.models.load_model("data/models/exercise_tf_model.keras")

layers = []


for layer in model.layers:

    weights = layer.get_weights()


    if len(weights) == 2:
        w, b = weights


        layers.append({
            "name": layer.name,
            "activation": layer.activation.__name__,
            "weights": w.tolist(),
            "bias": b.tolist()
        })


os.makedirs("data/models/mobile", exist_ok=True)

#eğittiğim modelleri flutterda kullanmak için json formatında ağırlık oluşturma

with open("data/models/mobile/mlp_model.json", "w", encoding="utf-8") as f:
    json.dump(layers, f)


print("MLP model weights exported:")
print("data/models/mobile/mlp_model.json")