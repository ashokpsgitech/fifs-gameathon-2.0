import os
import subprocess
import sys

# Step 1: Get match number from command-line argument
if len(sys.argv) < 2:
    print("❌ Match number not provided.")
    sys.exit(1)
match_no = sys.argv[1]

# Step 2: Remove old files
def remove_file(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✅ Removed: {filepath}")
        else:
            print(f"⚠️ File not found: {filepath}")
    except PermissionError:
        print(f"❌ Cannot remove {filepath}: File is open.")
        print("👉 Close it and try again.")

remove_file("scripts/data/match_data.csv")
remove_file("scripts/data/predicted_spreadsheet.csv")

# Step 3: Run scripts in sequence
def run_script(script, args=[]):
    try:
        subprocess.run(["python", script] + args, check=True)
        print(f"✅ Successfully ran {script}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script}: {e}")

run_script("merge.py", [match_no])
run_script("scripts/preprocess.py")
run_script("scripts/trainmodel.py")
run_script("scripts/predict.py")
