import pandas as pd

# Load 2019 data and deprivation data
df_2019 = pd.read_excel(
    "data/2019 Results.xlsx", sheet_name="2019", skiprows=2, header=[0, 1]
)
deprivation_df = pd.read_csv("data/old_parl_imd.csv")

# Flatten the multi-index columns
df_2019.columns = [
    f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df_2019.columns
]

print("Columns in df_2019:")
print(df_2019.columns)

# Define party columns
party_columns = {
    "Conservative": "Conservative Party_Votes",
    "Labour": "Labour_Votes ",  # Note the space after "Votes"
    "Liberal Democrat": "Liberal Democrats_Votes",
    "SNP": "SNP_Votes",
    "Green": "Green_Votes",
    "Brexit": "Brexit_Votes",
    "Plaid Cymru": "Plaid Cymru_Votes",
    "DUP": "DUP_Votes",
    "Sinn Fein": "Sinn Fein_Votes",
    "SDLP": "SDLP_Votes",
    "UUP": "UUP_Votes",
    "Alliance": "Alliance_Votes",
}

# Merge 2019 data with deprivation data
merged_df = pd.merge(
    df_2019,
    deprivation_df,
    left_on="Unnamed: 1_level_0_ONS id",
    right_on="gss-code",
    how="left",
)

# Convert the decile column to integers
merged_df["pcon-imd-pop-decile"] = (
    merged_df["pcon-imd-pop-decile"].fillna(-1).astype(int)
)

# Calculate percentages for all parties at once
for party, votes_col in party_columns.items():
    if votes_col in merged_df.columns:
        merged_df[f"{party}_pct"] = (
            merged_df[votes_col].fillna(0) / merged_df["Other_Total votes"] * 100
        )
    else:
        print(f"Warning: {votes_col} not found in columns")

# Calculate "Other" percentage
party_votes = merged_df[
    [col for col in party_columns.values() if col in merged_df.columns]
].sum(axis=1)
merged_df["Other_pct"] = (
    (merged_df["Other_Total votes"] - party_votes)
    / merged_df["Other_Total votes"]
    * 100
)

# Group by Decile and calculate mean percentages
grouped = merged_df.groupby("pcon-imd-pop-decile")[
    [f"{party}_pct" for party in party_columns.keys()] + ["Other_pct"]
].mean()

# Rename columns for clarity
grouped.columns = list(party_columns.keys()) + ["Other"]

# Reset index to make Decile a column
grouped = grouped.reset_index()

# Rename the index column to "Decile"
grouped = grouped.rename(columns={"pcon-imd-pop-decile": "Decile"})

# Define the new order of parties
party_order = [
    "Conservative",
    "Liberal Democrat",
    "Labour",
    "Brexit",
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

# Reorder columns
grouped = grouped[["Decile"] + party_order]

# Remove the -1 decile if it's still present
grouped = grouped[grouped["Decile"] != -1]

# Save the results
output_path = "output/2019_percentages_by_decile.csv"
grouped.to_csv(output_path, index=False)

print(f"Saved 2019 percentages by deprivation decile to {output_path}")
print("\nFirst few rows of the grouped data:")
print(grouped.head())
