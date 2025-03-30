import pandas as pd
import numpy as np


def process_turnout(value):
    if pd.isna(value):
        return None
    return float(value) * 100


def process_year(year, id_column):
    # Load data
    df = pd.read_excel(
        f"data/2019 Results.xlsx", sheet_name=str(year), skiprows=2, header=[0, 1]
    )
    deprivation_df = pd.read_csv("data/old_parl_imd.csv")

    # Flatten multi-index columns
    df.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df.columns]

    # Find total votes column
    total_votes_col = next(col for col in df.columns if "Total votes" in col)

    # Merge data
    merged_df = pd.merge(
        df,
        deprivation_df,
        left_on=id_column,
        right_on="gss-code",
        how="left",
    )

    # Process turnout values
    merged_df["Turnout"] = merged_df["Other_Turnout "].apply(process_turnout)

    # Process total votes - ensure it's numeric
    merged_df["total_votes_numeric"] = pd.to_numeric(
        merged_df[total_votes_col], errors="coerce"
    )

    # Use only valid data
    valid_data = merged_df.dropna(
        subset=["pcon-imd-pop-decile", "Turnout", "total_votes_numeric"]
    )

    print(
        f"\nNumber of valid constituencies for {year} turnout calculation: {len(valid_data)}"
    )
    print(f"Distribution of valid constituencies by decile:")
    print(valid_data["pcon-imd-pop-decile"].value_counts().sort_index())

    # Group by deprivation decile and calculate weighted mean turnout
    def weighted_turnout(group):
        return np.average(group["Turnout"], weights=group["total_votes_numeric"])

    grouped = (
        valid_data.groupby("pcon-imd-pop-decile").apply(weighted_turnout).reset_index()
    )
    grouped.columns = ["Decile", "Turnout"]
    grouped["Decile"] = grouped["Decile"].astype(int)
    grouped = grouped.set_index("Decile")

    # Remove -1 decile if present
    grouped = grouped[grouped.index != -1]

    # Save results
    output_path = f"output/{year}_turnout_by_decile_weighted.csv"
    grouped.to_csv(output_path)
    print(f"\nSaved {year} weighted turnout by Decile to {output_path}")
    print(f"\nWeighted Turnout by Decile for {year}:")
    print(grouped)
    print("\n")


# Process each year
for year in [2010, 2015, 2017, 2019]:
    if year == 2019:
        id_column = "Unnamed: 1_level_0_ONS id"
    elif year == 2017:
        id_column = "Unnamed: 1_level_0_id"
    else:
        id_column = "id_Unnamed: 1_level_1"
    process_year(year, id_column)
