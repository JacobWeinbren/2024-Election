import pandas as pd

# Load data
df_2019 = pd.read_excel(
    "data/2019 Results.xlsx", sheet_name="2019", skiprows=2, header=[0, 1]
)
deprivation_df = pd.read_csv("data/old_parl_imd.csv")

# Flatten multi-index columns
df_2019.columns = [
    f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df_2019.columns
]

print(df_2019.columns)

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

# Calculate votes for all parties
for party, votes_col in party_columns.items():
    if votes_col in merged_df.columns:
        merged_df[f"{party}_votes"] = merged_df[votes_col].fillna(0)
    else:
        print(f"Warning: {votes_col} not found in columns")

# Calculate "Other" votes
party_votes = merged_df[[f"{party}_votes" for party in party_columns.keys()]].sum(
    axis=1
)
merged_df["Other_votes"] = merged_df["Other_Total votes"] - party_votes

# Group by Decile and calculate total votes and voteshare
party_order = list(party_columns.keys()) + ["Other"]
grouped = merged_df.groupby("pcon-imd-pop-decile")

total_votes = grouped["Other_Total votes"].sum()
party_votes = {party: grouped[f"{party}_votes"].sum() for party in party_order}

# Calculate voteshare
voteshare = pd.DataFrame(
    {party: votes / total_votes * 100 for party, votes in party_votes.items()}
)
voteshare["Decile"] = voteshare.index

# Reorder columns and remove -1 decile
voteshare = voteshare[["Decile"] + party_order]
voteshare = voteshare[voteshare["Decile"] != -1]

# Save results
output_path = "output/2019_voteshare_by_decile.csv"
voteshare.to_csv(output_path, index=False)
print(f"Saved 2019 voteshare by deprivation decile to {output_path}")
