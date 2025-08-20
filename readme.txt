IPL Best XI Prediction  by Techie Wizards
TEAM:
1.Ashokan
2.Dhanushiyaa
3.Sangamithra
4.Logeshwaran

## Overview  
This project aims to predict the best playing XI for an IPL match based on past performance data and Dream11 points rules. The system consists of three main modules:  

1. **Data Preprocessing (`preprocess.py`)**  
   - Cleans raw match data.  
   - Renames columns based on configuration.  
   - Saves processed data for further use.  

2. **Model Training (`trainmodel.py`)**  
   - Trains a machine learning model using historical match data.  
   - Saves the trained model for predictions.  

3. **Team Prediction (`predict.py`)**  
   - Uses the trained model to predict the best XI players from the selected teams.  
   - Ensures balanced team composition (WK, BAT, ALL, BOWL).  
   - Saves the final team selection in a CSV file.  

## How to Run  
******************install all modules in requirements.txt by pip install command for smooth running******************

1. **Preprocess Data:**  
   ```sh
   python preprocess.py
   ```
2. **Train the Model:**  
   ```sh
   python trainmodel.py
   ```
3. **Predict Best XI:**  
   ```sh
   python predict.py
   ```
   Enter two team names (e.g., `RCB, MI`) when prompted.  

## Features  
✅ Filters duplicate players, keeping only the best-rated one.  
✅ Balances team composition based on role (WK, BAT, ALL, BOWL).  
✅ Saves predicted teams in a structured spreadsheet format.  

