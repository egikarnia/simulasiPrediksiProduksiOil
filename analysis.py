import time
import numpy as np
import pandas as pd

def measure_execution_time(func, *args):
    start_time = time.time()
    result = func(*args)
    execution_time = time.time() - start_time
    return result, execution_time

def calculate_error_metrics(actual, predicted):
    actual = np.array(actual)
    predicted = np.array(predicted)
    mae = np.mean(np.abs(actual - predicted))
    mse = np.mean((actual - predicted) ** 2)
    rmse = np.sqrt(mse)
    return {"MAE": mae, "MSE": mse, "RMSE": rmse}

def descriptive_statistics(data):
    stats = {
        "Rata-rata": np.mean(data),
        "Median": np.median(data),
        "Standar Deviasi": np.std(data),
        "Nilai Maksimal": np.max(data),
        "Nilai Minimal": np.min(data),
    }
    return stats

def analyze_prediction_accuracy(actual, predicted):
    comparison_df = pd.DataFrame({
        "Produksi Aktual": actual,
        "Produksi Prediksi": predicted,
        "Error (Aktual - Prediksi)": np.array(actual) - np.array(predicted)
    })
    return comparison_df
