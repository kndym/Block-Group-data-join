import os
import requests

# List of state abbreviations for the US
states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]


def download():

    
    # Base URL
    base_url = "https://data.dra2020.net/file/dra-block-data/Demographic_Data_Block_{}.v01.zip"

    # Directory to save the downloaded files
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    # Download each state's ZIP file
    for state in states:
        url = base_url.format(state)
        print(f"Downloading: {url}")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Save the file
            zip_path = os.path.join(output_dir, f"Demographic_Data_Block_{state}.v01.zip")
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded: {zip_path}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")

    print("All downloads complete.")

def unzip():
    for state in states:
        zip_path = os.path.join(output_dir, f"Demographic_Data_Block_{state}.v01.zip")
        if os.path.exists(zip_path):
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(unzip_dir)
                    print(f"Unzipped: {zip_path} to {unzip_dir}")
            except zipfile.BadZipFile as e:
                print(f"Failed to unzip {zip_path}: {e}")

    print("All downloads and extractions complete.")
