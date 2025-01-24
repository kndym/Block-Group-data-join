import os
import pandas as pd

# Directories
unzipped_dir = "./unzipped"
output_dir = "./block_groups"
os.makedirs(output_dir, exist_ok=True)

# List of state abbreviations for the US
states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

# Process each state's CSV file
for state in states:
    input_path = os.path.join(unzipped_dir, f"{state}", f"demographic_data_block_{state}.v01.csv")
    output_path = os.path.join(output_dir, f"demographic_data_blockgroup_{state}.v01.csv")

    if os.path.exists(input_path):
        print(f"Processing: {input_path}")
        # Read the CSV file
        df = pd.read_csv(input_path, dtype={"GEOID":str})

        # Ensure 'block_id' or equivalent column exists
        if 'GEOID' not in df.columns:
            print(f"Error: 'block_id' column not found in {input_path}")
            continue

        # Create block group GEOID by taking the first 12 characters of block_id
        df['block_group_geoid'] = df['GEOID'].str[:12]

        # Aggregate data by block group GEOID
        numeric_columns = df.select_dtypes(include=['number']).columns
        grouped_df = df.groupby('block_group_geoid')[numeric_columns].sum().reset_index()

        # Save the aggregated data to a new CSV file
        grouped_df.to_csv(output_path, index=False)
        print(f"Saved: {output_path}")

    else:
        print(f"File not found: {input_path}")

print("All processing complete.")
