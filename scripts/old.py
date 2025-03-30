import pandas as pd
import numpy as np

# Load data
df_2019 = pd.read_excel(
    "data/2019 Results.xlsx", sheet_name="2019", skiprows=2, header=[0, 1]
)
deprivation_df = pd.read_csv("data/old_parl_imd.csv")

# Flatten multi-index columns
df_2019.columns = [
    f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df_2019.columns
]

# Define party columns
party_columns = {
    "Conservative": "Conservative Party_Votes",
    "Liberal Democrat": "Liberal Democrats_Votes",
    "Labour": "Labour_Votes ",  # Note the space after "Votes"
    "Brexit": "Brexit_Votes",
    "Green": "Green_Votes",
    "SNP": "SNP_Votes",
    "Plaid Cymru": "Plaid Cymru_Votes",
    "DUP": "DUP_Votes",
    "Sinn Fein": "Sinn Fein_Votes",
    "SDLP": "SDLP_Votes",
    "UUP": "UUP_Votes",
    "Alliance": "Alliance_Votes",
}

# Find total votes column
total_votes_col = next(col for col in df_2019.columns if "Total votes" in col)
print(f"\nTotal votes column name: {total_votes_col}")

# Merge data and process
merged_df = pd.merge(
    df_2019,
    deprivation_df,
    left_on="Unnamed: 1_level_0_ONS id",
    right_on="gss-code",
    how="left",
)
merged_df["pcon-imd-pop-decile"] = (
    merged_df["pcon-imd-pop-decile"].fillna(-1).astype(int)
)

# Process total votes - ensure it's numeric
merged_df["total_votes_numeric"] = pd.to_numeric(
    merged_df[total_votes_col], errors="coerce"
)
print(
    f"Number of valid total votes values: {merged_df['total_votes_numeric'].notna().sum()}"
)

# Calculate votes for all parties
for party, votes_col in party_columns.items():
    if votes_col in merged_df.columns:
        merged_df[f"{party}_votes"] = pd.to_numeric(
            merged_df[votes_col], errors="coerce"
        ).fillna(0)
    else:
        print(f"Warning: {votes_col} not found in columns")

# Calculate "Other" votes
party_votes = merged_df[[f"{party}_votes" for party in party_columns.keys()]].sum(
    axis=1
)
merged_df["Other_votes"] = merged_df["total_votes_numeric"] - party_votes

# Calculate vote shares
party_order = list(party_columns.keys()) + ["Other"]
for party in party_order:
    merged_df[f"{party}_share"] = (
        merged_df[f"{party}_votes"] / merged_df["total_votes_numeric"] * 100
    )

# Group by deprivation decile and calculate weighted vote shares
result_dict = {}
for party in party_order:
    # Use only valid data
    valid_data = merged_df.dropna(
        subset=["pcon-imd-pop-decile", f"{party}_share", "total_votes_numeric"]
    )

    # Print diagnostic info for one party
    if party == "Labour":
        print(
            f"\nNumber of valid constituencies for Labour calculation: {len(valid_data)}"
        )
        print(f"Distribution of valid constituencies by decile:")
        print(valid_data["pcon-imd-pop-decile"].value_counts().sort_index())

    # Apply weighted average using total votes as weights
    result = valid_data.groupby("pcon-imd-pop-decile").apply(
        lambda group: np.average(
            group[f"{party}_share"], weights=group["total_votes_numeric"]
        )
    )

    result_dict[party] = result

# Convert results to DataFrame
voteshare = pd.DataFrame(result_dict)
voteshare.index.name = "Decile"
voteshare = voteshare.reset_index()

# Remove -1 decile if present
voteshare = voteshare[voteshare["Decile"] != -1]

# Save results
output_path = "output/2019_voteshare_by_decile_weighted.csv"
voteshare.to_csv(output_path, index=False)
print(f"\nSaved 2019 weighted voteshare by deprivation decile to {output_path}")
