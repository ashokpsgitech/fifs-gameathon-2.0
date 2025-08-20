import pandas as pd
import sys
import os

# Get the absolute path of the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Append the absolute path of the parent directory to sys.path
sys.path.append(parent_dir)

from main import datapath, colconfig  # Now import should work correctly
from main import datapath, predictors, cat_cols, target_col, modelname, execute_model_train

def train_model():
    print("🔹 Training model...")
    processed_data_path = datapath['featenggpath']
    execute_model_train(datapath, modelname, predictors, cat_cols, target_col, usetimeseries=False)
    print("✅ Model training complete and saved.")

if __name__ == "__main__":
    train_model()
