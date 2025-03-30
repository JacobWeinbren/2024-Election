import pandas as pd
import numpy as np

# Load data
df_2024 = pd.read_csv("data/2024_results.csv", header=[0, 1, 2, 3])
deprivation_df = pd.read_csv("data/new_parl_imd_fixed.csv")

# Flatten multi-level columns
df_2024.columns = [" ".join(map(str, col)).strip() for col in df_2024.columns.values]

# Extract turnout column and total votes
turnout_col = next(col for col in df_2024.columns if col.startswith("Turnout"))
total_votes_col = next(col for col in df_2024.columns if "TOTAL VOTES" in col)

# Merge dataframes
merged_df = pd.merge(
    df_2024, deprivation_df, left_on=df_2024.columns[2], right_on="gss_code", how="left"
)


# Process turnout values
def process_turnout(value):
    if pd.isna(value):
        return None
    return float(value.rstrip("%"))


merged_df["Turnout"] = merged_df[turnout_col].apply(process_turnout)

# Process total votes - ensure it's numeric
merged_df["total_votes_numeric"] = (
    merged_df[total_votes_col].astype(str).str.replace(",", "")
)
merged_df["total_votes_numeric"] = pd.to_numeric(
    merged_df["total_votes_numeric"], errors="coerce"
)


# Group by deprivation decile and calculate weighted mean turnout
def weighted_turnout(group):
    return np.average(group["Turnout"], weights=group["total_votes_numeric"])


# Handle deciles safely
merged_df["decile_numeric"] = pd.to_numeric(
    merged_df["parl25-imd-pop-decile"], errors="coerce"
)

# Use only valid data
valid_data = merged_df.dropna(
    subset=["decile_numeric", "Turnout", "total_votes_numeric"]
)

print(f"\nNumber of valid constituencies for turnout calculation: {len(valid_data)}")
print(f"Distribution of valid constituencies by decile:")
print(valid_data["decile_numeric"].value_counts().sort_index())

# Calculate weighted turnout by decile
grouped = valid_data.groupby("decile_numeric").apply(weighted_turnout).reset_index()
grouped.columns = ["Decile", "Turnout"]
grouped["Decile"] = grouped["Decile"].astype(int)
grouped = grouped.set_index("Decile")

# Save results
output_path = "output/2024_turnout_by_decile_weighted.csv"
grouped.to_csv(output_path)
print(f"\nSaved 2024 weighted turnout by Decile to {output_path}")
print("\nWeighted Turnout by Decile:")
print(grouped)
