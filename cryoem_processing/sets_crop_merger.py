from itertools import product

# Define desired box sizes and crop box size ranges (in pixels)
DATA_BOX1 = range(1800, 2000, 2)
DATA_BOX2 = range(1200, 1900, 2)
CROP_TO = range(300, 500, 2) # must be smaller than box size with larger pixel size

# Define pixel sizes for the two datasets (in Angstroms, fetched from the info of data collection)
ps1, ps2 = 0.83, 1.06

ROUND_TO = 4 # CryoSPARC requires final pixel size to be rounded to 4 decimal places

for bs1, bs2, crop in product(DATA_BOX1, DATA_BOX2, CROP_TO):
    if crop >= bs1 or crop >= bs2: # to surpass the situation when the user provides overlapping ranges
        continue
    ps1_new = round(bs1/crop*ps1, ROUND_TO)
    ps2_new = round(bs2/crop*ps2, ROUND_TO)

    if (ps1_new == ps2_new):
        print(f"\nboxsize 1 = {bs1}", 
              f"\nboxsize 2 = {bs2}", 
              f"\nfourier crop to: {crop}", 
              f"\nnew pixel size = {ps1_new:.4f}",
              "\n", "-------"
              )