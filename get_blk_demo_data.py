import os
import requests
import zipfile

# List of state abbreviations for the US
states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

# Base URL
base_url = "https://data.dra2020.net/file/dra-block-data/Demographic_Data_Block_{}.v01.zip"

# Directories for downloads and extractions
output_dir = "downloads"
unzip_dir = "unzipped"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(unzip_dir, exist_ok=True)

def download_and_unzip():
    for state in states:
        url = base_url.format(state)
        print(f"Processing: {state}")
        
        # Download the file
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save the ZIP file
            zip_path = os.path.join(output_dir, f"Demographic_Data_Block_{state}.v01.zip")
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {zip_path}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")
            continue

        # Unzip the file
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(unzip_dir, state))
                print(f"Unzipped: {zip_path} to {os.path.join(unzip_dir, state)}")
        except zipfile.BadZipFile as e:
            print(f"Failed to unzip {zip_path}: {e}")

    print("All downloads and extractions complete.")

# Run the function
download_and_unzip()
