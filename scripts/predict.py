import pandas as pd
import os
import sys
from collections import defaultdict

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import datapath, colconfig, predictors, cat_cols, pred_col, execute_model_prediction, modelname
from preprocess import preprocess_data

def predict_team(selected_teams, match_no):
    print("🔹 Predicting best XI...")

    processed_data_path = preprocess_data(datapath, colconfig)
    spreadsheet_path = datapath['spreadsheetpath']
    predicted_path = datapath['predictedpath']
    default_path = datapath['defaultpath']
    excel_path = datapath['excelpath']

    if not os.path.exists(spreadsheet_path):
        print("❌ Spreadsheet not found. Run preprocess first.")
        return

    try:
        playing11_df = pd.read_excel(excel_path, sheet_name=f"Match_{match_no}")
        playing11_df = playing11_df[playing11_df["IsPlaying"] == "PLAYING"]
    except Exception as e:
        print(f"❌ Error reading Excel sheet: {e}")
        return

    latest_credit_df = playing11_df[["Player Name", "Credits"]].rename(columns={"Credits": "LatestCredit"})

    print(f"🛠 Executing model prediction using {modelname}...")
    execute_model_prediction(datapath, predictors, modelname, cat_cols, pred_col,
                             usetimeseries=False, predpath=predicted_path)

    if not os.path.exists(predicted_path):
        raise FileNotFoundError(f"❌ Prediction output not found: {predicted_path}")

    team_df = pd.read_csv(predicted_path)
    default_df = pd.read_csv(default_path)[["Player Name", "Matches"]].drop_duplicates(subset="Player Name")

    team_df = team_df.merge(default_df, on="Player Name", how="left")
    team_df = team_df.merge(latest_credit_df, on="Player Name", how="left")

    ruled_out = ["Adam Zampa", "Ruturaj Gaikwad", "Lockie Ferguson", "Glenn Phillips"]
    team_df = team_df[~team_df["Player Name"].isin(ruled_out)]

    if "LatestCredit" not in team_df.columns or "AverageCredits" not in team_df.columns:
        print("❌ Required columns missing.")
        return

    team_df["Credit Weightage"] = round(
        0.5 * team_df["AverageCredits"].astype(float) + 0.5 * team_df["LatestCredit"].astype(float), 2
    )
    team_df["Matches"] = team_df["Matches"].fillna(0).astype(int)
    team_df = team_df.drop_duplicates(subset=["Player Name"])
    team_df = team_df[team_df["Player Name"].isin(playing11_df["Player Name"])]
    team_df = team_df[team_df["Team"].isin(selected_teams)]

    # Sort by Credit Weightage then Matches
    team_df = team_df.sort_values(by=["Credit Weightage", "Matches"], ascending=[False, False]).reset_index(drop=True)

    # Select 15 best players regardless of team count/credit if necessary
    selected_players = []
    total_credit = 0.0
    for _, row in team_df.iterrows():
        if len(selected_players) >= 15:
            break
        if row["Player Name"] not in [p["Player Name"] for p in selected_players] and total_credit + row["Credit Weightage"] <= 100:
            selected_players.append(row)
            total_credit += row["Credit Weightage"]

    # Fallback: If not enough players due to credit, relax credit constraint
    if len(selected_players) < 15:
        for _, row in team_df.iterrows():
            if len(selected_players) >= 15:
                break
            if row["Player Name"] not in [p["Player Name"] for p in selected_players]:
                selected_players.append(row)

    final_df = pd.DataFrame(selected_players).drop_duplicates(subset=["Player Name"]).head(15).copy()
    final_df["Role"] = "NA"

    # Sort again for role assignment
    final_df = final_df.sort_values(by=["Credit Weightage", "Matches"], ascending=[False, False]).reset_index(drop=True)

    # Assign Captain
    final_df.loc[0, "Role"] = "C"

    # Assign VC using CreditWeight = second highest, then role priority
    vc_credit = final_df.loc[1, "Credit Weightage"]
    vc_pool = final_df[(final_df["Credit Weightage"] == vc_credit) & (final_df["Role"] != "C")]

    if len(vc_pool) == 1:
        final_df.loc[vc_pool.index[0], "Role"] = "VC"
    else:
        role_priority = {"ALL": 1, "WK": 2, "BAT": 3, "BOWL": 4}
        vc_pool = vc_pool.copy()
        vc_pool["Priority"] = vc_pool["Player Type"].map(role_priority)
        vc_pick = vc_pool.sort_values(by="Priority").iloc[0]
        final_df.loc[final_df["Player Name"] == vc_pick["Player Name"], "Role"] = "VC"

    # Fill NA and SUB
    final_df.loc[final_df["Role"] == "NA", "Role"] = "NA"
    final_df.loc[final_df["Role"] == "VC", "AssignedVC"] = True
    na_assigned = final_df[final_df["Role"].isin(["C", "VC"])].index.tolist()
    remaining = final_df[~final_df.index.isin(na_assigned)].copy()

    final_df.loc[remaining.head(9).index, "Role"] = "NA"
    final_df.loc[remaining.tail(4).index, "Role"] = "SUB"

    # Ensure order
    final_df["Role"] = pd.Categorical(final_df["Role"], categories=["C", "VC", "NA", "SUB"], ordered=True)
    final_df = final_df.sort_values(by=["Role", "Credit Weightage"], ascending=[True, False])
    final_df = final_df[["Player Type", "Player Name", "Team", "lineupOrder", "Credit Weightage", "Role"]]

    try:
        final_df.to_csv(predicted_path, index=False)
        print(f"✅ Final team saved to {predicted_path}")
        print(f"🧮 Total Credit Used (Main XI): {final_df[final_df['Role'] != 'SUB']['Credit Weightage'].sum():.2f}")
    except PermissionError:
        print("❌ Close the prediction file and retry.")

    for path in [processed_data_path, spreadsheet_path]:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    return final_df

if __name__ == "__main__":
    print("⚠️ Ensure 'techie_wizards_output.csv' is CLOSED before proceeding.")
    match_no_str = os.environ.get("MATCH_NO")
    if not match_no_str:
        try:
            match_no_str = input("Enter Match Number (e.g., 1 - 70): ").strip()
        except EOFError:
            print("❌ No input. Set MATCH_NO environment variable.")
            sys.exit(1)

    try:
        match_no = int(match_no_str)
        excel_path = datapath["excelpath"]
        print(f"📖 Reading Excel sheet: Match_{match_no}")
        playing11_df = pd.read_excel(excel_path, sheet_name=f"Match_{match_no}")
        team1, team2 = playing11_df["Team"].unique().tolist()
        print(f"✅ Match {match_no}: {team1} vs {team2}")
        predict_team([team1, team2], match_no)
    except ValueError:
        print("❌ Invalid match number.")
    except FileNotFoundError:
        print(f"❌ Excel file not found at path: {excel_path}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")