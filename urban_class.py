import pandas as pd
import numpy as np
from tqdm.auto import tqdm

import geopandas as gpd



def data_clean(gpkg_path):
    global df_Rural, df_Urbanized, df_SmallMetro  # Declare the variables as global

    # Load GeoPackage
    df = gpd.read_file(gpkg_path)
    print("read gpkg")

    # Ensure numeric columns are handled properly
    numeric_columns = ["ACS17_Occupied_Housing_Units_Es", "UPSAI_urban", "UPSAI_suburban", "UPSAI_rural"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Split Data
    df_Rural = df[df["NAME20"].isnull()].copy()
    df_Urbanized = df[df["NAME20"].notnull()].copy()
    df_Rural.loc[:, "Class"] = "Rural"

    # Classify Urban and Suburban based on UPSAI
    df_Urbanized.loc[df_Urbanized["UPSAI_urban"] > df_Urbanized["UPSAI_suburban"], "Class"] = "Urban"
    df_Urbanized.loc[df_Urbanized["UPSAI_urban"] <= df_Urbanized["UPSAI_suburban"], "Class"] = "Suburban"

    if False:
        # Calculate total households for each urban area
        urban_area_totals = df_Urbanized.groupby("NAME20")["ACS17_Occupied_Housing_Units_Es"].sum()

        # Identify urban areas with fewer than 100,000 households
        small_urban_areas = urban_area_totals[urban_area_totals < 100000].index

        # Reclassify tracts in small urban areas as "Small Metro"
        df_Urbanized.loc[df_Urbanized["NAME20"].isin(small_urban_areas), "Class"] = "Small Metro"

        # Split Small Metro into a separate DataFrame
        df_SmallMetro = df_Urbanized[df_Urbanized["Class"] == "Small Metro"].copy()

    df_Urbanized = df_Urbanized[df_Urbanized["Class"] != "Small Metro"].copy()
    df_Urbanized["Homogenity"]=0



def flip_classes_based_on_neighbors_vectorized(df, alpha=0.6, beta=0.75):
    """
    Flips the class of each census tract if more than 75% of the nearest households
    and at least 15,000 of the nearest households belong to a different class.

    Parameters:
    df (gpd.GeoDataFrame): GeoDataFrame containing urbanized census tract data
        with 'Nearest_Neighbors' column.

    Returns:
    gpd.GeoDataFrame: The GeoDataFrame with updated 'Class' column.
    """
    # Precompute household totals and class groupings
    household_totals = df.set_index("GEOID")["ACS17_Occupied_Housing_Units_Es"]
    class_lookup = df.set_index("GEOID")["Class"]

    # Convert 'Nearest_Neighbors' to lists for efficient lookup
    df["Nearest_Neighbors_List"] = df["Nearest_Neighbors"].apply(lambda x: x.split(",") if x else [])

    # Store class updates
    class_updates = {}

    homo_updates ={}

    # Iterate over all rows with a progress bar
    for index, row in tqdm(df[df["Homogenity"]<beta].iterrows() , total=df.shape[0], desc="Flipping Classes"):
        if not row["Nearest_Neighbors_List"]:
            continue  # Skip if no neighbors


        # Get neighbor GEOIDs
        neighbor_ids = row["Nearest_Neighbors_List"]

        # Calculate total households and class proportions using precomputed data
        neighbor_classes = class_lookup.loc[neighbor_ids]
        neighbor_households = household_totals.loc[neighbor_ids]

        total_households = neighbor_households.sum()
        if total_households == 0:
            continue  # Skip if no households

        urban_households = neighbor_households[neighbor_classes == "Urban"].sum()

        urban_ratio = urban_households / total_households

        # Determine flip conditions
        if row["Class"] == "Urban":  
            homo_updates[index]=urban_ratio
            if urban_ratio < (1-alpha):
                class_updates[index] = "Suburban"
        elif row["Class"] == "Suburban": 
            homo_updates[index]=1-urban_ratio
            if urban_ratio > alpha:
                class_updates[index] = "Urban"

    # Apply class updates in bulk
    for idx, new_class in class_updates.items():
        df.at[idx, "Class"] = new_class
    
    for idx, new_homo in homo_updates.items():
        df.at[idx, "Homogenity"] = new_homo

    # Drop temporary columns
    df.drop(columns=["Nearest_Neighbors_List"], inplace=True)

    return df


def add_nearest_household_columns_grouped(df, household_radius):
    """
    Adds columns for the total number of households from the nearest tracts 
    for all census tracts in the GeoDataFrame, grouped by urban area for improved performance.
    Also stores nearest neighbors' GEOIDs.

    Parameters:
    df (gpd.GeoDataFrame): GeoDataFrame containing urbanized census tract data.

    Returns:
    gpd.GeoDataFrame: The GeoDataFrame with a new column for nearest neighbors' GEOIDs.
    """
    # Enable tqdm progress bar
    tqdm.pandas()

    # Initialize a column to store nearest neighbors' GEOIDs
    df["Nearest_Neighbors"] = ""  # Stores IDs as a comma-separated string

    # Group the DataFrame by urban area (NAME20)
    grouped = df.groupby("NAME20")

    # Iterate over each urban area
    for name20, group in tqdm(grouped, desc="Processing Urban Areas"):
        group = group.copy()  # Avoid modifying the original group

        for index, target_row in group.iterrows():
            # Compute distances from the target tract
            distances = group.geometry.distance(target_row.geometry)

            # Sort by distance
            sorted_group = group.assign(distance=distances).sort_values(by="distance")

            # Accumulate households until 20,000 threshold is reached
            total_households = 0
            nearest_neighbors = []  # List to store IDs of nearest neighbors

            for _, row in sorted_group.iterrows():
                total_households += row["ACS17_Occupied_Housing_Units_Es"]
                nearest_neighbors.append(row["GEOID"])  # Store GEOID of the neighbor

                if total_households >= household_radius:
                    break
            nearest_neighbors.append(df["GEOID"][index])      
            # Update the original DataFrame
            df.loc[index, "Nearest_Neighbors"] = ",".join(nearest_neighbors)  # Store as comma-separated string

    return df


def find_classes(loop_length=5, tract_geopkg="urban full join.gpkg", new_urban_cluster=False, household_radius=20000):
    #create dataframes

    data_clean(tract_geopkg)

    # create your

    if new_urban_cluster:
        df_Urbanized = add_nearest_household_columns_grouped(df_Urbanized, household_radius)
        df_Urbanized.to_csv("Urbanized Save.csv")

    df_Urbanized=pd.read_csv("Urbanized Save.csv", dtype={"GEOID": str})

    # Perform multiple class-flip iterations
    for _ in range(loop_length):  # Run multiple iterations as needed
        df_Urbanized = flip_classes_based_on_neighbors_vectorized(df_Urbanized)

    # Combine DataFrames
    final_df = pd.concat([df_Rural, df_Urbanized], ignore_index=True)

    # Ensure 'GEOID' is a string
    final_df["GEOID"] = final_df["GEOID"].astype(str)

    final_df["AFFGEOID"] = "1500000US"+final_df["GEOID"]

    # Specify the list of columns to keep
    columns_to_keep = [
        "GEOID", "AFFGEOID", "ACS17_Occupied_Housing_Units_Es", "UPSAI_urban", "UPSAI_suburban", 
        "UPSAI_rural", 
        "NAME20", "Class"
    ]

    final_df = final_df[columns_to_keep]

    blkgroup_tract_df=pd.read_csv("assignments.csv", dtype={"tract_2010_GEOID": str, 
                                                            "STATEFP": str,
                                                            "COUNTYFP": str,
                                                            "TRACTCE": str,
                                                            "BLKGRPCE":str,
                                                            "blk_grp_GEOID":str,
                                                            "tract_2010_GEOID":str})

    columns_to_keep=["STATEFP","COUNTYFP","TRACTCE","BLKGRPCE", "blk_grp_GEOID", "tract_2010_GEOID"]

    blkgroup_tract_df=blkgroup_tract_df[columns_to_keep]

    blkgroup_tract_df["tract_2010_GEOID"]=blkgroup_tract_df["tract_2010_GEOID"].astype(str)

    print("read assignment.csv")

    final_blk_df=blkgroup_tract_df.merge(final_df, left_on="tract_2010_GEOID", right_on="GEOID", how="left")

    # Save as GeoPackage
    output_name= "my_blk_grp_final_output.csv"

    final_blk_df.to_csv(output_name)
    print(f"file saved as {output_name}")

find_classes()