import pandas as pd
from collections import OrderedDict

# Load data
df_2024 = pd.read_csv("data/2024_results.csv", header=[0, 1, 2, 3])
deprivation_df = pd.read_csv("data/new_parl_imd_fixed.csv")

# Flatten multi-level columns
df_2024.columns = [" ".join(map(str, col)).strip() for col in df_2024.columns.values]

# Select vote columns (H:X)
vote_columns = df_2024.iloc[:, 7:24]

# Define party mapping (unchanged)
party_mapping = OrderedDict(
    {
        "CON": "Conservative",
        "LDM": "Liberal Democrat",
        "LAB": "Labour",
        "RFM": "Reform UK",
        "GRN": "Green",
        "SNP": "SNP",
        "PLC": "Plaid Cymru",
        "DUP": "DUP",
        "SF": "Sinn Fein",
        "SDLP": "SDLP",
        "UUP": "UUP",
        "ALL": "Alliance",
    }
)

# Merge dataframes (unchanged)
merged_df = pd.merge(
    df_2024, deprivation_df, left_on=df_2024.columns[2], right_on="gss_code", how="left"
)


# Process vote values
def process_votes(value):
    if pd.isna(value):
        return 0
    if isinstance(value, str):
        return pd.to_numeric(value.split()[-1], errors="coerce")
    return value


# Get total votes column
total_votes_col = (
    "TOTAL VOTES Unnamed: 34_level_1 Unnamed: 34_level_2 Unnamed: 34_level_3"
)

# Map parties and process votes
for old_name, new_name in party_mapping.items():
    col = next((col for col in vote_columns.columns if col.startswith(old_name)), None)
    if col:
        merged_df[new_name] = vote_columns[col].apply(process_votes)
    else:
        print(f"Warning: No column found for {old_name}")

# Calculate "Other" votes
main_parties = list(party_mapping.values())
merged_df["Other"] = merged_df[total_votes_col] - merged_df[main_parties].sum(axis=1)

# Calculate vote shares
party_order = main_parties + ["Other"]
for party in party_order:
    merged_df[f"{party} Share"] = merged_df[party] / merged_df[total_votes_col] * 100

# Group by deprivation decile and calculate mean vote shares
grouped = (
    merged_df.groupby("parl25-imd-pop-decile")[
        [f"{party} Share" for party in party_order]
    ]
    .mean()
    .reset_index()
)
grouped["parl25-imd-pop-decile"] = grouped["parl25-imd-pop-decile"].astype(int)
grouped = grouped.rename(columns={"parl25-imd-pop-decile": "Decile"}).set_index(
    "Decile"
)

# Rename columns to remove " Share" suffix
grouped.columns = [col.replace(" Share", "") for col in grouped.columns]

# Save results
output_path = "output/2024_voteshare_by_decile.csv"
grouped.to_csv(output_path)
print(f"Saved 2024 vote shares by Decile to {output_path}")
print("\nFirst few rows of the grouped data:")
print(grouped.head())
