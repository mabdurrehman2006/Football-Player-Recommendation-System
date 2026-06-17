#data_loader.py
import warnings
from statsbombpy.api_client import NoAuthWarning
warnings.simplefilter("ignore", NoAuthWarning) #ignores NoAuthWarning as I"m using the free version 

from statsbombpy import sb
import pandas as pd
from pathlib import Path



def fetch_match_events(m_id):
    try:
        return sb.events(match_id=m_id)
    except Exception:
        return None
    
def get_wsl_data(filename="WSL_2023-2024.parquet"):
    filepath=Path(filename)
    if filepath.is_file():
        print("File found, reading data")
        return pd.read_parquet(filename)
    
    print("No file found, connecting to statsbomb API")
    #WSL competition ID and the 2023/2024 season ID
    comp_id=37
    season_id=281

    #matches=sb.matches(competition_id=comp_id, season_id=season_id)

    #match_ids=matches["match_id"].unique()

    print("downloading all fixtures")
    
    final_df=sb.competition_events(country="England", division="FA Women's Super League", season="2023/2024", gender="female")
    final_df.to_parquet(filename)
    print("saved data to file")
    return final_df





