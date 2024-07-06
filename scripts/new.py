import pandas as pd
import numpy as np
from collections import OrderedDict

# Load 2024 data and new deprivation data
df_2024 = pd.read_csv("data/2024_results.csv", header=[0, 1, 2, 3])
deprivation_df = pd.read_csv("data/new_parl_imd_fixed.csv")

# Flatten the multi-level columns
df_2024.columns = [" ".join(map(str, col)).strip() for col in df_2024.columns.values]

print("\nColumns in df_2024 after flattening:")
print(df_2024.columns)

# Select only the percentage columns (AP:BH)
percentage_columns = df_2024.iloc[
    :, 41:59
]  # Assuming AP is the 42nd column (0-indexed)

print("\nColumns in percentage_columns:")
print(percentage_columns.columns)

# Define party names with full names and specify which ones to group as "Other"
party_mapping = OrderedDict(
    [
        ("LAB", "Labour"),
        ("CON", "Conservative"),
        ("RFM", "Reform UK"),
        ("LDM", "Liberal Democrat"),
        ("GRN", "Green"),
        ("SNP", "SNP"),
        ("PLC", "Plaid Cymru"),
        ("Others", "Other"),
        ("Top IND", "Other"),
        ("WPGB", "Other"),
        ("SDP", "Other"),
        ("Localist", "Other"),
        ("DUP", "DUP"),
        ("SF", "Sinn Fein"),
        ("ALL", "Alliance"),
        ("SDLP", "SDLP"),
        ("UUP", "UUP"),
        ("TUV", "Other"),
    ]
)

# Merge 2024 data with deprivation data
merged_df = pd.merge(
    df_2024, deprivation_df, left_on=df_2024.columns[2], right_on="gss_code", how="left"
)


# Function to process percentage values
def process_percentage(value):
    if isinstance(value, pd.Series):
        return value.apply(process_percentage)
    if pd.isna(value):
        return 0
    if isinstance(value, str):
        value = value.rstrip("%")
        return 0 if value == "#DIV/0!" else pd.to_numeric(value, errors="coerce")
    return value


# Use the percentage columns directly
for old_name, new_name in party_mapping.items():
    # Find the column that starts with the old_name
    matching_columns = [
        col for col in percentage_columns.columns if col.startswith(old_name)
    ]
    if matching_columns:
        merged_df[new_name] = process_percentage(
            percentage_columns[matching_columns[0]]
        )
    else:
        print(f"Warning: No column found for {old_name}")

# Sum up "Other" parties
other_parties = [
    name for name, mapped_name in party_mapping.items() if mapped_name == "Other"
]
merged_df["Other"] = merged_df[
    [
        party_mapping[party]
        for party in other_parties
        if party_mapping[party] in merged_df.columns
    ]
].sum(axis=1)

# Remove individual columns for parties grouped under "Other"
merged_df = merged_df.drop(
    columns=[
        party_mapping[party]
        for party in other_parties
        if party_mapping[party] in merged_df.columns and party_mapping[party] != "Other"
    ]
)

# Define the desired order of parties
party_order = [
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

# Group by deprivation decile and calculate mean percentages
grouped = merged_df.groupby("parl25-imd-pop-decile")[
    list(OrderedDict.fromkeys(party_mapping.values()))
].mean()

# Rename the index to "Decile" and convert it to integers
grouped = grouped.rename_axis("Decile").reset_index()
grouped["Decile"] = grouped["Decile"].astype(int)

# Reorder columns according to the specified order
grouped = grouped[["Decile"] + [col for col in party_order if col in grouped.columns]]

# Set "Decile" as the index again
grouped = grouped.set_index("Decile")

# Save the results
output_path = "output/2024_percentages_by_decile.csv"
grouped.to_csv(output_path)
print(f"\nSaved 2024 percentages by Decile to {output_path}")
print("\nFirst few rows of the grouped data:")
print(grouped.head())
