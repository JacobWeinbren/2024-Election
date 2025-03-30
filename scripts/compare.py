import pandas as pd
import numpy as np

# Read the CSV files
df_2019 = pd.read_csv("output/2019_voteshare_by_decile_weighted.csv")
df_2024 = pd.read_csv("output/2024_voteshare_by_decile_weighted.csv")

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

# Add Reform UK / Brexit Party for 2019 data if needed
if "Brexit" in df_2019.columns and "Reform UK" not in df_2019.columns:
    df_2019["Reform UK"] = df_2019["Brexit"]

# Ensure TUV is in 2019 data if needed
if "TUV" not in df_2019.columns and "TUV" in parties:
    df_2019["TUV"] = 0

# Calculate the difference
df_diff = pd.DataFrame()
df_diff["Decile"] = range(1, 11)

# Calculate differences for each party
for party in parties:
    if party in df_2019.columns and party in df_2024.columns:
        df_diff[party] = df_2024[party] - df_2019[party]
    else:
        print(f"Warning: {party} not found in both datasets")

# Round the results to 2 decimal places
df_diff = df_diff.round(2)

# Print the table
print(df_diff.to_string(index=False))

# Save to a CSV file
output_path = "output/percentage_point_changes_weighted.csv"
df_diff.to_csv(output_path, index=False, float_format="%.2f")
print(f"\nSaved percentage point changes to {output_path}")
