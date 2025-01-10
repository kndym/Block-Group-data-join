import pandas as pd
import os

# List of state abbreviations
states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

# Directory containing the CSV files
input_dir = "block_groups"
output_file = "merged_demographic_data.csv"

# Initialize an empty DataFrame for merging
merged_data = pd.DataFrame()

# Loop through each state and read the corresponding CSV file
for state in states:
    file_path = os.path.join(input_dir, f"demographic_data_blockgroup_{state}.v01.csv")
    if os.path.exists(file_path):
        print(f"Reading data from {file_path}")
        state_data = pd.read_csv(file_path, dtype={'block_group_geoid': str})
        merged_data = pd.concat([merged_data, state_data], ignore_index=True)
    else:
        print(f"File not found: {file_path}")

# Save the merged data to a new CSV file
merged_data.to_csv(output_file, index=False)
print(f"Merged data saved to {output_file}")