import pandas as pd


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
    print(df.columns)
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

    # Group by deprivation decile and calculate mean turnout
    grouped = merged_df.groupby("pcon-imd-pop-decile")["Turnout"].mean().reset_index()
    grouped["pcon-imd-pop-decile"] = grouped["pcon-imd-pop-decile"].astype(int)
    grouped = grouped.rename(columns={"pcon-imd-pop-decile": "Decile"}).set_index(
        "Decile"
    )

    # Remove -1 decile if present
    grouped = grouped[grouped.index != -1]

    # Save results
    output_path = f"output/{year}_turnout_by_decile.csv"
    grouped.to_csv(output_path)
    print(f"Saved {year} turnout by Decile to {output_path}")
    print(f"\nTurnout by Decile for {year}:")
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
