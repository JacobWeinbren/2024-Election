import pandas as pd

# Load data
df_2024 = pd.read_csv("data/2024_results.csv", header=[0, 1, 2, 3])
deprivation_df = pd.read_csv("data/new_parl_imd_fixed.csv")

# Flatten multi-level columns
df_2024.columns = [" ".join(map(str, col)).strip() for col in df_2024.columns.values]

# Extract turnout column
turnout_col = next(col for col in df_2024.columns if col.startswith("Turnout"))

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

# Group by deprivation decile and calculate mean turnout
grouped = merged_df.groupby("parl25-imd-pop-decile")["Turnout"].mean().reset_index()
grouped["parl25-imd-pop-decile"] = grouped["parl25-imd-pop-decile"].astype(int)
grouped = grouped.rename(columns={"parl25-imd-pop-decile": "Decile"}).set_index(
    "Decile"
)

# Save results
output_path = "output/2024_turnout_by_decile.csv"
grouped.to_csv(output_path)
print(f"Saved 2024 turnout by Decile to {output_path}")
print("\nTurnout by Decile:")
print(grouped)
