import pandas as pd
import numpy as np

# Read the CSV files
df_2019 = pd.read_csv("output/2019_voteshare_by_decile.csv")
df_2024 = pd.read_csv("output/2024_voteshare_by_decile.csv")

# Rename columns for consistency
df_2019 = df_2019.rename(columns={"pcon-imd-pop-decile": "Decile"})
df_2024 = df_2024.rename(columns={"parl25-imd-pop-decile": "Decile"})

# Create a list of parties in the desired order
parties = [
    "Conservative",
    "Liberal Democrat",
    "Labour",
    "Reform UK",
    "Green",
    "SNP",
    "Plaid Cymru",
    "DUP",
    "Sinn Fein",
    "SDLP",
    "UUP",
    "Alliance",
    "Other",
]


# Add Reform UK / Brexit Party
df_2019["Reform UK"] = df_2019["Brexit"]

# Add TUV (new party)
df_2019["TUV"] = 0

# Calculate the difference
df_diff = df_2024[["Decile"] + parties] - df_2019[["Decile"] + parties]

# Round the results to 2 decimal places
df_diff = df_diff.round(2)

# Ensure deprivation column contains decile values (1-10)
df_diff["Decile"] = range(1, 11)

# Reorder columns to match the desired order
df_diff = df_diff[["Decile"] + parties]

# Print the table
print(df_diff.to_string(index=False))

# Save to a CSV file
df_diff.to_csv("output/percentage_point_changes.csv", index=False, float_format="%.2f")
