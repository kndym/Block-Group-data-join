# Urban Class
classifies US census block groups as Urban Suburban or Rural based off:
[Urbanization Perceptions Small Area Index
](https://www.huduser.gov/portal/AHS-neighborhood-description-study-2017.html#small-area-tab)

Edit and run urban_class.py to create your own classification by blk group
- loop_length: how many times the program checks for tracts to flip class
- new_urban_cluster: if you want to change population radius of the algorithm, change to True to create csv saving the neighbor tracts
  - only need to be done once for each population radii
- alpha: what percent of the households of neighbor tracts need to be different to flip a tract
- beta: what percent of the households of neighbor tracts need to be the same to not check for a possible flip
    
