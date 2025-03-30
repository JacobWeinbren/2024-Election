import pandas as pd
import numpy as np


def process_year(year, id_column):
    print(f"\n--- Processing {year} Election Data ---")

    # Load data
    df = pd.read_excel(
        f"data/2019 Results.xlsx", sheet_name=str(year), skiprows=2, header=[0, 1]
    )
    deprivation_df = pd.read_csv("data/old_parl_imd.csv")

    # Flatten multi-index columns
    df.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df.columns]

    # Define party columns based on year
    party_columns = {
        "Conservative": next(
            (col for col in df.columns if "Conservative" in col and "Votes" in col),
            None,
        ),
        "Liberal Democrat": next(
            (col for col in df.columns if "Liberal Democrat" in col and "Votes" in col),
            None,
        ),
        "Labour": next(
            (col for col in df.columns if "Labour" in col and "Votes" in col), None
        ),
        "Green": next(
            (col for col in df.columns if "Green" in col and "Votes" in col), None
        ),
        "SNP": next(
            (col for col in df.columns if "SNP" in col and "Votes" in col), None
        ),
        "Plaid Cymru": next(
            (col for col in df.columns if "Plaid Cymru" in col and "Votes" in col), None
        ),
        "DUP": next(
            (col for col in df.columns if "DUP" in col and "Votes" in col), None
        ),
        "Sinn Fein": next(
            (col for col in df.columns if "Sinn Fein" in col and "Votes" in col), None
        ),
        "SDLP": next(
            (col for col in df.columns if "SDLP" in col and "Votes" in col), None
        ),
        "UUP": next(
            (col for col in df.columns if "UUP" in col and "Votes" in col), None
        ),
        "Alliance": next(
            (col for col in df.columns if "Alliance" in col and "Votes" in col), None
        ),
    }

    # Add the appropriate party name based on year
    if year in [2010, 2015, 2017]:
        ukip_col = next(
            (col for col in df.columns if "UKIP" in col and "Votes" in col), None
        )
        if ukip_col:
            party_columns["UKIP"] = ukip_col
    elif year == 2019:
        brexit_col = next(
            (col for col in df.columns if "Brexit" in col and "Votes" in col), None
        )
        if brexit_col:
            party_columns["Brexit"] = brexit_col

    # Check which party columns are missing
    for party, col in party_columns.items():
        if col is None:
            print(f"Warning: No column found for {party}")
            party_columns.pop(party)

    # Find total votes column
    total_votes_col = next((col for col in df.columns if "Total votes" in col), None)
    if total_votes_col is None:
        print("Error: Could not find total votes column")
        return

    # Merge data
    merged_df = pd.merge(
        df, deprivation_df, left_on=id_column, right_on="gss-code", how="left"
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
        merged_df[f"{party}_votes"] = pd.to_numeric(
            merged_df[votes_col], errors="coerce"
        ).fillna(0)

    # Calculate "Other" votes
    party_votes = merged_df[[f"{party}_votes" for party in party_columns.keys()]].sum(
        axis=1
    )
    merged_df["Other_votes"] = merged_df["total_votes_numeric"] - party_votes

    # Add Other to party list
    party_columns["Other"] = "Other_votes"

    # Calculate vote shares
    for party in party_columns.keys():
        vote_col = f"{party}_votes"
        merged_df[party] = merged_df[vote_col] / merged_df["total_votes_numeric"] * 100

    # Use only valid data
    valid_data = merged_df.dropna(subset=["pcon-imd-pop-decile", "total_votes_numeric"])
    valid_data = valid_data[valid_data["pcon-imd-pop-decile"] != -1]

    # Group by deprivation decile and calculate weighted vote shares
    result_dict = {}
    for party in party_columns.keys():
        # Apply weighted average using total votes as weights
        result = valid_data.groupby("pcon-imd-pop-decile").apply(
            lambda group: np.average(group[party], weights=group["total_votes_numeric"])
        )
        result_dict[party] = result

    # Convert results to DataFrame
    voteshare = pd.DataFrame(result_dict)
    voteshare.index.name = "Decile"
    voteshare = voteshare.reset_index()

    # Save results
    output_path = f"output/{year}_voteshare_by_decile_weighted.csv"
    voteshare.to_csv(output_path, index=False)
    print(f"Saved {year} weighted voteshare by deprivation decile to {output_path}")

    return voteshare


# Process each year
years = {
    2010: "id_Unnamed: 1_level_1",
    2015: "id_Unnamed: 1_level_1",
    2017: "Unnamed: 1_level_0_id",
    2019: "Unnamed: 1_level_0_ONS id",
}

for year, id_column in years.items():
    process_year(year, id_column)
