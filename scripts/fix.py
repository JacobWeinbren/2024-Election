import pandas as pd

# Read the CSV files
new_parl_codes = pd.read_csv("data/new_parl_codes.csv")
new_parl_imd = pd.read_csv("data/new_parl_imd.csv")

# Merge the dataframes on the parl25 column
merged_df = pd.merge(
    new_parl_imd,
    new_parl_codes[["short_code", "gss_code"]],
    left_on="parl25",
    right_on="short_code",
    how="left",
)

# Drop the redundant short_code column
merged_df = merged_df.drop("short_code", axis=1)

# Reorder columns to put gss_code after parl25
columns = ["parl25", "gss_code"] + [
    col for col in merged_df.columns if col not in ["parl25", "gss_code"]
]
merged_df = merged_df[columns]

# Save the result to a new CSV file
merged_df.to_csv("data/new_parl_imd_fixed.csv", index=False)

print("new_parl_imd_fixed.csv has been created successfully.")
