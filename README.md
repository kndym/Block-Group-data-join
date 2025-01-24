# Block-Group-data-join
gets all election and demographic data by block groups

process:

get_blk_demo_data.py: download block demographic data from DRA
    /downloads

block_to_block_grp_convert: convert state blk data to state blk grp data
    /block_groups

join_state_to_csv: create national blk grp csv
    merged_demographic_data.csv

calculate_urban_shares.py: calculate urban shares by CD, County, and State 
    house_urban.csv, state_urban.csv, district_urban.csv