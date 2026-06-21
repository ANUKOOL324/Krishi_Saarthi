"""
Crop recommendation engine for KrishiSaarthi.

Trains a K-Nearest Neighbors classifier on soil and climate parameters
from the crop_recommendation.csv dataset. Uses scikit-learn when available;
falls back to a custom pure-Python KNN implementation using Euclidean
distance for maximum compatibility in constrained environments.
"""

import os
import math
import pandas as pd

_X_train = []
_y_train = []
_feature_means = []
_feature_stds = []
_knn_model = None
_is_sklearn = False

def init_model():
    global _X_train, _y_train, _feature_means, _feature_stds, _knn_model, _is_sklearn
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    filepath = os.path.join(data_dir, "crop_recommendation.csv")
    
    if not os.path.exists(filepath):
        from src.utils.generate_data import generate_crop_data
        generate_crop_data()
        
    df = pd.read_csv(filepath)
    feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    
    _feature_means = df[feature_cols].mean().tolist()
    _feature_stds = df[feature_cols].std().tolist()
    _feature_stds = [x if x != 0 else 1.0 for x in _feature_stds]
    
    df_norm = df.copy()
    for i, col in enumerate(feature_cols):
        df_norm[col] = (df[col] - _feature_means[i]) / _feature_stds[i]
        
    _X_train = df_norm[feature_cols].values.tolist()
    _y_train = df_norm["label"].tolist()
    
    try:
        from sklearn.neighbors import KNeighborsClassifier
        import numpy as np
        
        _knn_model = KNeighborsClassifier(n_neighbors=5)
        _knn_model.fit(np.array(_X_train), np.array(_y_train))
        _is_sklearn = True
        print("Successfully trained Crop Suitability model using scikit-learn.")
    except ImportError:
        _is_sklearn = False
        print("scikit-learn not available. Using custom, pure-Python K-Nearest Neighbors fallback.")

def predict_crop(N, P, K, temp, hum, ph, rain, k=5):
    global _X_train, _y_train, _feature_means, _feature_stds, _knn_model, _is_sklearn
    
    if not _X_train:
        init_model()
        
    query = [N, P, K, temp, hum, ph, rain]
    query_norm = []
    for i in range(len(query)):
        query_norm.append((query[i] - _feature_means[i]) / _feature_stds[i])
        
    if _is_sklearn:
        import numpy as np
        probabilities = _knn_model.predict_proba(np.array([query_norm]))[0]
        classes = _knn_model.classes_
        results = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)
        return [(crop, float(prob)) for crop, prob in results if prob > 0]
    else:
        distances = []
        for idx, train_point in enumerate(_X_train):
            dist = math.sqrt(sum((q - t) ** 2 for q, t in zip(query_norm, train_point)))
            distances.append((dist, _y_train[idx]))
            
        distances.sort(key=lambda x: x[0])
        neighbors = distances[:k]
        
        counts = {}
        for _, crop in neighbors:
            counts[crop] = counts.get(crop, 0) + 1
            
        results = [(crop, count / k) for crop, count in counts.items()]
        results.sort(key=lambda x: x[1], reverse=True)
        return results

if __name__ == "__main__":
    init_model()
    recs = predict_crop(90, 42, 43, 25.5, 82.3, 6.2, 180.0)
    print("Test recommendation:", recs)
