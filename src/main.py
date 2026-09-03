from enum import Enum
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from src.data_loader import get_wsl_data
from src.recommender import filter_data, get_similar_players



app = FastAPI(title="WSL recommender API")
data_df = get_wsl_data()
data_df = filter_data(data_df)

player_list=data_df.index

Playerchoice=Enum("Playerchoice", {name: name for name in player_list}, type=str)

class SimilarToPlayer(BaseModel):
    Player: str
    Similarity: float
    Goals: int
    Expected_Goals: float
    Shots: int
    Assists: int

class ScoutingReport(BaseModel):
    target_player_stats: SimilarToPlayer
    recommendations: list[SimilarToPlayer]






@app.get("/status")
def get_status():
    # Eh not exactly a professional status message but
    # I like throwing some personality into my personal projects
    return {"status": "everything's good YAY", "code": 200}


@app.post("/recommend", response_model=ScoutingReport)
def recommend_player(playername: Playerchoice, numberofrecs: int=Query(default=5, ge=1, le=10)):
    target_player = playername
    try:
        results=get_similar_players(data_df, target_player, numberofrecs)
        target_stats=data_df.loc[target_player].to_dict()
        target_stats["Player"]=target_player
        target_stats["Similarity"]=100.0
        return {"target_player_stats": target_stats, "recommendations": results}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/strikers")
def get_strikers():
    return {"strikers": list(data_df.index)}
