#!/bin/bash

# Get the last argument passed to the container as MATCH_NO
MATCH_NO="${@:$#}"  # This gets the last argument from the command-line input

# Validate if MATCH_NO is provided
if [ -z "$MATCH_NO" ]; then
  echo "❌ MATCH_NO is not provided. Please specify the match number."
  exit 1
fi

# Print the match number
echo "✅ Starting IPL Prediction Pipeline for Match No: $MATCH_NO"

# Set environment variable for MATCH_NO
export MATCH_NO

# Proceed with the pipeline execution
echo "✅ Removed: scripts/data/match_data.csv"
rm -f scripts/data/match_data.csv

# Run merge.py to prepare match data (Pass MATCH_NO as argument)
echo "✅ Merging completed. File saved as 'scripts/data/match_data.csv'."
python merge.py "$MATCH_NO"

# Run preprocess.py for data preprocessing
echo "✅ Successfully ran scripts/preprocess.py"
python scripts/preprocess.py

# Run trainmodel.py to train the model
echo "🔹 Training model..."
python scripts/trainmodel.py

# Run predict.py for team prediction
echo "🔹 Predicting best XI..."
python scripts/predict.py

# Completion message
echo "✅ Match $MATCH_NO Prediction completed successfully!"

# Attempt to copy the output file to /app/output
cp scripts/data/techie_wizards_output.csv /app/output/techie_wizards_output.csv && \
echo "✅ Output copied to /app/output (should appear in your parent folder of image )" || \
echo "❌ Failed to copy output to /app/output"
