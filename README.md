# Block-Group-data-join
gets all election and demographic data by block groups

process:

get_blk_demo_data.py: download block demographic data from DRA

block_to_block_grp_convert: convert state blk data to state blk grp data

join_state_to_csv: create national blk grp csv

calculate_urban_shares.py: calculate urban shares by CD, County, and State