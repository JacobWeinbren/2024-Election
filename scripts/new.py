import pandas as pd
import numpy as np
from collections import OrderedDict

# Load data
df_2024 = pd.read_csv("data/2024_results.csv", header=[0, 1, 2, 3])
deprivation_df = pd.read_csv("data/new_parl_imd_fixed.csv")

# Flatten multi-level columns
df_2024.columns = [" ".join(map(str, col)).strip() for col in df_2024.columns.values]

# Select vote columns
vote_columns = df_2024.iloc[:, 7:24]

# Define party mapping
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

# Merge dataframes
merged_df = pd.merge(
    df_2024, deprivation_df, left_on=df_2024.columns[2], right_on="gss_code", how="left"
)

# Get total votes column
total_votes_col = next(col for col in df_2024.columns if "TOTAL VOTES" in col)

# Clean total votes values
merged_df["total_votes_numeric"] = (
    merged_df[total_votes_col].astype(str).str.replace(",", "")
)
merged_df["total_votes_numeric"] = pd.to_numeric(
    merged_df["total_votes_numeric"], errors="coerce"
)

print(f"\nTotal votes column name: {total_votes_col}")
print(
    f"First few total votes values after cleaning: {merged_df['total_votes_numeric'].head().tolist()}"
)
print(
    f"Number of valid total votes values: {merged_df['total_votes_numeric'].notna().sum()}"
)


# Process vote values
def process_votes(value):
    if pd.isna(value):
        return 0
    if isinstance(value, str):
        try:
            return pd.to_numeric(value.replace(",", ""), errors="coerce")
        except:
            return 0
    return value


# Map parties and process votes
for old_name, new_name in party_mapping.items():
    col = next((col for col in vote_columns.columns if col.startswith(old_name)), None)
    if col:
        merged_df[new_name] = vote_columns[col].apply(process_votes)
    else:
        print(f"Warning: No column found for {old_name}")

# Calculate "Other" votes
main_parties = list(party_mapping.values())
merged_df["Other"] = merged_df["total_votes_numeric"] - merged_df[main_parties].sum(
    axis=1
)

# Calculate vote shares
party_order = main_parties + ["Other"]
for party in party_order:
    merged_df[f"{party} Share"] = (
        merged_df[party] / merged_df["total_votes_numeric"]
    ) * 100

# Handle deciles safely
merged_df["decile_numeric"] = pd.to_numeric(
    merged_df["parl25-imd-pop-decile"], errors="coerce"
)

# Group by deprivation decile and calculate weighted mean vote shares
result_dict = {}
for party in party_order:
    # Group only where we have valid data for all required columns
    valid_data = merged_df.dropna(
        subset=["decile_numeric", f"{party} Share", "total_votes_numeric"]
    )

    # Print diagnostic info for one party to check data distribution
    if party == "Labour":
        print(
            f"\nNumber of valid constituencies for Labour calculation: {len(valid_data)}"
        )
        print(f"Distribution of valid constituencies by decile:")
        print(valid_data["decile_numeric"].value_counts().sort_index())

    # Apply weighted average using total votes as weights
    result = valid_data.groupby("decile_numeric").apply(
        lambda group: np.average(
            group[f"{party} Share"], weights=group["total_votes_numeric"]
        )
    )

    result_dict[party] = result

# Convert results to DataFrame
grouped = pd.DataFrame(result_dict)
grouped.index.name = "Decile"
grouped = grouped.reset_index()

# Save results
output_path = "output/2024_voteshare_by_decile_weighted.csv"
grouped.to_csv(output_path, index=False)
print(f"\nSaved 2024 weighted vote shares by Decile to {output_path}")
