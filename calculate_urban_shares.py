import pandas as pd

def calculate_district_population_shares(blk_grp_urban_join_path, merged_demographic_data_path, output_path):
    # Load the datasets
    blk_grp_urban_join = pd.read_csv(blk_grp_urban_join_path)
    merged_demographic_data = pd.read_csv(merged_demographic_data_path)

    # Merge datasets on the appropriate key
    merged_data = blk_grp_urban_join.merge(
        merged_demographic_data,
        left_on='GEOID',
        right_on='block_group_geoid',
        how='inner'
    )

    # Group by congressional district and urban/suburban/rural classification
    aggregated_data = merged_data.groupby(['NewID', 'block_grp_output_Real_Class'])['T_20_CENS_Total'].sum().reset_index()

    # Pivot the data to have Urban, Suburban, Rural as columns
    district_totals = aggregated_data.pivot(
        index='NewID',
        columns='block_grp_output_Real_Class',
        values='T_20_CENS_Total'
    ).fillna(0)

    district_totals['Total_Population'] = district_totals.sum(axis=1)

    # Calculate shares
    district_totals['Urban_Share'] = district_totals.get('Urban', 0) / district_totals['Total_Population']
    district_totals['Suburban_Share'] = district_totals.get('Suburban', 0) / district_totals['Total_Population']
    district_totals['Rural_Share'] = district_totals.get('Rural', 0) / district_totals['Total_Population']

    # Reset index to make the district ID a column
    district_totals.reset_index(inplace=True)

    # Save the results
    district_totals.to_csv(output_path, index=False)
    
    return f"Results saved to {output_path}"


def calculate_county_population_shares(blk_grp_urban_join_path, merged_demographic_data_path, output_path):
    # Load the datasets with GEOID columns explicitly as strings
    blk_grp_urban_join = pd.read_csv(blk_grp_urban_join_path, dtype={'GEOID': str})
    merged_demographic_data = pd.read_csv(merged_demographic_data_path, dtype={'block_group_geoid': str})

    # Extract county GEOID from block group GEOID
    merged_demographic_data['county_geoid'] = merged_demographic_data['block_group_geoid'].str[:5]

    # Merge datasets on the appropriate key
    merged_data = blk_grp_urban_join.merge(
        merged_demographic_data,
        left_on='GEOID',
        right_on='block_group_geoid',
        how='inner'
    )

    # Group by county and urban/suburban/rural classification
    aggregated_data = merged_data.groupby(['county_geoid', 'block_grp_output_Real_Class'])['T_20_CENS_Total'].sum().reset_index()

    # Pivot the data to have Urban, Suburban, Rural as columns
    county_totals = aggregated_data.pivot(
        index='county_geoid',
        columns='block_grp_output_Real_Class',
        values='T_20_CENS_Total'
    ).fillna(0)

    county_totals['Total_Population'] = county_totals.sum(axis=1)

    # Calculate shares
    county_totals['Urban_Share'] = county_totals.get('Urban', 0) / county_totals['Total_Population']
    county_totals['Suburban_Share'] = county_totals.get('Suburban', 0) / county_totals['Total_Population']
    county_totals['Rural_Share'] = county_totals.get('Rural', 0) / county_totals['Total_Population']

    # Reset index to make the county GEOID a column
    county_totals.reset_index(inplace=True)

    # Save the results
    county_totals.to_csv(output_path, index=False)
    
    return f"Results saved to {output_path}"


def calculate_state_population_shares(blk_grp_urban_join_path, merged_demographic_data_path, output_path):
    # Load the datasets
    blk_grp_urban_join = pd.read_csv(blk_grp_urban_join_path, dtype={'GEOID': str})
    merged_demographic_data = pd.read_csv(merged_demographic_data_path, dtype={'block_group_geoid': str})

    # Normalize GEOID columns to ensure they are 12 characters long
    blk_grp_urban_join['GEOID'] = blk_grp_urban_join['GEOID'].str.zfill(12)
    merged_demographic_data['block_group_geoid'] = merged_demographic_data['block_group_geoid'].str.zfill(12)

    # Extract state GEOID from block group GEOID (first two characters represent the state)
    merged_demographic_data['state_geoid'] = merged_demographic_data['block_group_geoid'].str[:2]

    # Merge datasets on the appropriate key
    merged_data = blk_grp_urban_join.merge(
        merged_demographic_data,
        left_on='GEOID',
        right_on='block_group_geoid',
        how='inner'
    )

    # Group by state and urban/suburban/rural classification
    aggregated_data = merged_data.groupby(['state_geoid', 'block_grp_output_Real_Class'])['T_20_CENS_Total'].sum().reset_index()

    # Pivot the data to have Urban, Suburban, Rural as columns
    state_totals = aggregated_data.pivot(
        index='state_geoid',
        columns='block_grp_output_Real_Class',
        values='T_20_CENS_Total'
    ).fillna(0)

    state_totals['Total_Population'] = state_totals.sum(axis=1)

    # Calculate shares
    state_totals['Urban_Share'] = state_totals.get('Urban', 0) / state_totals['Total_Population']
    state_totals['Suburban_Share'] = state_totals.get('Suburban', 0) / state_totals['Total_Population']
    state_totals['Rural_Share'] = state_totals.get('Rural', 0) / state_totals['Total_Population']

    # Reset index to make the state GEOID a column
    state_totals.reset_index(inplace=True)

    # Save the results
    state_totals.to_csv(output_path, index=False)
    
    return f"Results saved to {output_path}"

blk_grp_class="blk_grp_classes.csv"

blk_grp_pop="merged_demographic_data.csv"

result_message = calculate_state_population_shares(blk_grp_class, blk_grp_pop, 'state_urban.csv')
print(result_message)
result_message = calculate_county_population_shares(blk_grp_class, blk_grp_pop, 'county_urban.csv')
print(result_message)
result_message = calculate_district_population_shares(blk_grp_class, blk_grp_pop, 'house_urban.csv')
print(result_message)