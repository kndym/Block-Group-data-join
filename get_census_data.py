import requests
import json
import pandas as pd

import os
import requests
import pandas as pd

def get_census_data():
    # Load the API key
    with open("census_api_key.txt", "r") as file:
        api_key = file.read().strip()

    # Define the state FIPS codes
    state_fips = {
        "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
        "CO": "08", "CT": "09", "DE": "10", "DC": "11", "FL": "12",
        "GA": "13", "HI": "15", "ID": "16", "IL": "17", "IN": "18",
        "IA": "19", "KS": "20", "KY": "21", "LA": "22", "ME": "23",
        "MD": "24", "MA": "25", "MI": "26", "MN": "27", "MS": "28",
        "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33",
        "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38",
        "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44",
        "SC": "45", "SD": "46", "TN": "47", "TX": "48", "UT": "49",
        "VT": "50", "VA": "51", "WA": "53", "WV": "54", "WI": "55",
        "WY": "56"
    }

    # Loop over even-numbered years from 2010 to 2022
    years = [year for year in range(2010, 2023, 2)]
    base_url = "https://api.census.gov/data/{}/acs/acs5/subject"

    # Base output folder
    base_folder = "educ_raw_data"
    os.makedirs(base_folder, exist_ok=True)

    for year in years:
        for state, fips_code in state_fips.items():
            url = f"{base_url}?get=NAME,S1501_C01_031E,S1501_C01_033E&for=tract:*&in=state:{fips_code}&key={api_key}"
            url = url.format(year)

            try:
                # Request data from the API
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                print(data[:1])
                print(data[1:2])

                # Ensure data is valid
                if len(data) > 1:  # Skip if no data
                    # Extract data into a DataFrame
                    df = pd.DataFrame(data[1:], columns=data[0])

                    # Create a subfolder for the state
                    state_folder = os.path.join(base_folder, state)
                    os.makedirs(state_folder, exist_ok=True)

                    # Define output CSV path
                    csv_file = os.path.join(state_folder, f"{state}.csv")

                    # If file exists, append; otherwise, create a new file
                    if os.path.exists(csv_file):
                        existing_df = pd.read_csv(csv_file)
                        df = pd.concat([existing_df, df], ignore_index=True)

                    # Save the DataFrame to a CSV file
                    df.to_csv(csv_file, index=False)
                    print(f"Data for {state} in {year} saved to {csv_file}.")
                else:
                    print(f"No data for {state} in {year}.")

            except requests.exceptions.RequestException as e:
                print(f"Failed to retrieve data for {state} in {year}: {e}")


# Call the function
get_census_data()
