import pandas as pd
import os
import sys

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def preprocess_data(datapath, colconfig):
    print("🔹 Preprocessing data...")

    # Read merged CSV match data
    match_data = pd.read_csv(datapath['matchdatapath'])

    # Rename columns as per config
    match_data = match_data.rename(columns=colconfig)
    match_data = match_data.rename(columns=lambda x: x.strip())

    # Ensure required column exists
    if 'Match No' not in match_data.columns:
        raise KeyError("❌ Column 'Match No' not found in the match data. Please check colconfig and source data.")

    # Path to mounted Excel file
    excel_path = datapath['excelpath']
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"❌ Excel file not found at {excel_path}")

    print("📥 Reading squad Excel file...")
    squad_df = pd.read_excel(excel_path)
    squad_df = squad_df.rename(columns=lambda x: x.strip())

    # Merge Excel squad info
    merged_data = pd.merge(match_data, squad_df, on='Player Name', how='left', suffixes=('', '_squad'))

    # Calculate AverageCredits and LatestCredits using last 3 matches
    credits_info = []
    for player, group in merged_data.groupby('Player Name'):
        sorted_group = group.sort_values(by='Match No')  # Ensure chronological order
        credits = sorted_group['Credits'].tolist()
        num_matches = len(credits)

        last_3 = credits[-3:] if num_matches >= 3 else credits
        avg_credit = sum(last_3) / len(last_3)
        latest_credit = sum(last_3) / len(last_3)

        credits_info.append({
            'Player Name': player,
            'AverageCredits': avg_credit,
            'Credits': latest_credit,  # For compatibility with downstream use
        })

    credit_df = pd.DataFrame(credits_info)

    # Base data - final merge
    base_data = merged_data.drop_duplicates(subset='Player Name', keep='last').drop(columns=['Credits'], errors='ignore')
    final_data = base_data.merge(credit_df, on='Player Name', how='left')

    # Save to processed paths
    processed_data_path = datapath['featenggpath']
    spreadsheet_path = datapath['spreadsheetpath']
    final_data.to_csv(processed_data_path, index=False)
    final_data.to_csv(spreadsheet_path, index=False)

    print(f"✅ Processed data saved at {processed_data_path}")
    print(f"✅ Spreadsheet saved at {spreadsheet_path}")
    return processed_data_path
