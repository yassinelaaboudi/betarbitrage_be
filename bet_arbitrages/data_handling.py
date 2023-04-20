import pandas as pd
import numpy as np
import logger as log

logger = log.get_logger("data handling")

def standardize_quotes(dict_quotes, col_locators):
    """
    Standardizes a dictionary of raw quote (lists) by selecting and renaming columns according to
    the specified locators in `col_locators`. The resulting dataframes will have standardized column
    names of the form "<name>_<colname>" and will only include rows with valid quotes.

    Args:
        dict_quotes (dict): A dictionary of raw quote dataframes, where the keys are website names and
            the values are the corresponding dataframes.
        col_locators (dict): A dictionary of column locators, where the keys are website names and the
            values are lists of integer indices representing the columns to select from the corresponding
            raw dataframes.

    Returns:
        dict: A dictionary of standardized quote dataframes, where the keys are website names and the
        values are the corresponding standardized dataframes.
    """
    # Create new dict to not alter the first one
    dict_quotes_sc = {}
    # Standardize each dataframes
    for name, li in dict_quotes.items():

        logger.info(f"dataframe transformation for {name}")
        if len(li) == 0:
            logger.error(f"No data for {name}")
            continue

        cols = ["home", "away", "1", "X", "2"]
        cols = [f"{name}_{i}" for i in cols]

        # Transformation to dataFrame - starcasino remove "Endirect"
        df = pd.DataFrame([[j for j in i if j != "EN DIRECT"] for i in li])
        # rename columns
        try:
            df_temp = df.iloc[:, col_locators[name]].copy()
            df_temp.columns = cols
        # Some websites can include the game but the quotes are not available yet
        # Insert copy of the DF in the log to investigate
        except IndexError as err:
            logger.error("Data has not been parse correctly")
            logger.error("dataframe head\n{}".format(df.head().to_string()))
            # For now return an empty DataFrame
            df_temp = pd.DataFrame(columns=["home", "away", "1", "X", "2"])

        # drop columns without Quotes
        del_row = df_temp[df_temp.applymap(lambda x: x is None).sum(axis=1) > 0].index
        df_temp.drop(index=del_row, inplace=True)
        dict_quotes_sc[name] = df_temp

    return dict_quotes_sc


def concatenate_quotes(dict_quotes_sc, df_keys):
    """
    Gather all quotes from a dictionary of standardized quote dataframes with names as keys
    and dataframes as values into one dataframe. This function is used to merge quote data
    from multiple sources for the same event.

    Args:
        dict_quotes_sc (dict): A dictionary of standardized quote dataframes, where the keys are
            website names and the values are the corresponding dataframes.
        df_keys (DataFrame): A dataframe that contains the home and away team names for each
            event, with one row for each event.

    Returns:
        DataFrame: A dataframe that contains all quotes for all events from all sources, with
        columns of the form "<name>_home", "<name>_away", "<name>_1", "<name>_X", "<name>_2",
        where "<name>" is the name of the website that the quote came from.
    """
    # Go trough each dataframes in dict_quotes
    for index, (name, df) in enumerate(dict_quotes_sc.items()):
        # USe the first one as a basis
        if index == 0:
            df_allquotes = df.copy()
            ref = name
        elif df.shape[0] == 0:
            logger.warning(f"No quotes for {name}")
            continue
        else:
            # Add the Keys for home away regarding the first dataframe
            df_temp = df.merge(
                df_keys[[name, ref]].dropna(),
                left_on=[name + "_home"],
                right_on=name,
                how="left",
            )
            df_temp.drop(columns=name, inplace=True)
            df_temp = df_temp.merge(
                df_keys[[name, ref]].dropna(),
                left_on=[name + "_away"],
                right_on=name,
                suffixes=["_home", "_away"],
                how="left",
            )
            # Merge this dataframe with the first one
            df_temp.drop(columns=[name, name + "_home", name + "_away"], inplace=True)
            df_allquotes = df_allquotes.merge(df_temp, how="outer")

    # Remove None
    df_allquotes = df_allquotes.applymap(lambda x: np.NaN if x is None else x)
    # Define cols
    col_win = [i for i in df_allquotes.columns if "_1" in i]
    col_drawn = [i for i in df_allquotes.columns if "_X" in i]
    col_loose = [i for i in df_allquotes.columns if "_2" in i]
    # Compute the min Margin if you do surebet valuation
    df_allquotes["margin"] = (
        1 / np.nanmax(df_allquotes[col_win].astype(float), axis=1)
        + 1 / np.nanmax(df_allquotes[col_drawn].astype(float), axis=1)
        + 1 / np.nanmax(df_allquotes[col_loose].astype(float), axis=1)
    )
    return df_allquotes
