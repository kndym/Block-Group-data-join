import pandas as pd
import os

# Input and output file paths
input_file = "ACSST5Y2023.S1501-Data.csv"  # Replace with actual path
output_file = "output_census_tract_shares.csv"

# Read the CSV file
df = pd.read_csv(input_file)
print(df.head())

df=df.drop(index=0)

print(df.head())

df['S1501_C01_031E']=df['S1501_C01_031E'].astype(int)
df['S1501_C01_033E']=df['S1501_C01_033E'].astype(int)

# Ensure necessary columns exist
required_columns = ['GEO_ID', 'S1501_C01_031E', 'S1501_C01_033E']
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"Missing one or more required columns: {required_columns}")

# Calculate the share of Whites with a bachelor's degree or higher
def calculate_share(row):
    if row['S1501_C01_031E'] == 0 or type(row['S1501_C01_033E'])==str:
        return 0.5
    return row['S1501_C01_033E'] / row['S1501_C01_031E']

df['share_white_bach_degree'] = df.apply(calculate_share, axis=1)

# Select only GEOID and the calculated share for output
output_df = df[['GEO_ID', 'share_white_bach_degree']]

# Save to a new CSV file
output_df.to_csv(output_file, index=False)

print(f"Processed data saved to {output_file}")
