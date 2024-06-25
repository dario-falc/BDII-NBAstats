from pymongo import MongoClient
import pandas as pd
import chardet

def insert_players(col_players):
    # Lettura dati
    players_path = ".\\data\\players.csv"

    with open(players_path, "rb") as f:
        result = chardet.detect(f.read())

    players_df = pd.read_csv(players_path, encoding=result["encoding"], delimiter=";")

    ## Rimozione colonne inutili
    players_df = players_df.drop(["Rk", "GS", "TOV"], axis=1)

    ## Rinomino "Player" in "Name"
    players_df = players_df.rename( columns = {"Player" : "Name"} )

    ## Inserimento dati
    for _ , row in players_df.iterrows():
        col_players.insert_one(row.to_dict())


def insert_teams(col_teams):
    ## Lettura dati
    teams_path = ".\\data\\teams.csv"

    with open(teams_path, "rb") as f:
        result = chardet.detect(f.read())

    teams_df = pd.read_csv(teams_path, encoding=result["encoding"], delimiter=",")

    ## Aggiunta colonna "conference"
    eastern = ["BOS", "NYK", "MIL", "CLE", "ORL", "IND", "PHI", "MIA", "CHI", "ATL", "BKN", "TOR", "CHA", "WAS", "DET"]
    western = ["OKC", "DEN", "MIN", "LAC", "DAL", "PHX", "NOP", "LAL", "SAC", "GSW", "HOU", "UTA", "MEM", "SAS", "POR"]

    conference = list()
    for _ , row in teams_df.iterrows():
        conference.append("East" if row["abbreviation"] in eastern else "West")

    teams_df.insert(loc=6, column="conference", value=conference)

    ## Rimozione colonne inutili
    teams_df = teams_df.drop(["team_id", "arenacapacity"], axis=1)
    
    ## Cambio yearfounded da double a int
    teams_df["yearfounded"] = teams_df["yearfounded"].astype(int)
    
    ## Inserimento dati
    for _ , row in teams_df.iterrows():
        col_teams.insert_one(row.to_dict())


def insert_games(col_games):
    ## Lettura dati
    games_path = ".\\data\\games.csv"

    with open(games_path, "rb") as f:
        result = chardet.detect(f.read())

    games_df = pd.read_csv(games_path, encoding=result["encoding"], delimiter=",")
    
    # Selezione partite della stagione 2022-2023
    games_df = games_df[games_df["season_id"] == 22022]

    # Rimozione colonne inutili
    games_df = games_df.drop(["season_id", "team_id_home", "game_id", "min", "plus_minus_home", "video_available_home",
                            "team_id_away", "matchup_away", "plus_minus_away", "video_available_away", "season_type"], axis=1)

    # Sostituisco le colonne "wl_home" e "wl_away" con un'unica colonna "winner" che ha valore "Home" se ha vinto la squadra in casa, "Away" altrimenti 
    winner = games_df["wl_home"].where(games_df["wl_home"] == "W", "Away")
    winner = winner.where(winner == "Away", "Home")

    games_df.insert(loc=44, column="winner", value=winner)
    games_df = games_df.drop(["wl_home", "wl_away"], axis=1)
    
    # Inserimento dati
    for _ , row in games_df.iterrows():
        col_games.insert_one(row.to_dict())


def embed_players_in_teams(col_players, col_teams):
    # Prendo le abbreviazioni di tutti i team dalla collection teams
    get_teams = col_teams.find()

    team_abbreviations = list()
    for res in get_teams:
        team_abbreviations.append(res["abbreviation"])

    # Per ogni squadra
    for team in team_abbreviations:
        # Prendo tutti i giocatori di quella squadra dalla collection players
        get_players_from_team = {"Tm" : team}
        
        players_from_team = col_players.find(get_players_from_team)
        
        #print(f"Team: {team}")
        player_ids = list()

        # Per ogni giocatore della squadra team
        for player in players_from_team:
            # Prendo l'id del giocatore e lo aggiungo alla lista di id dei giocatori della squadra team
            player_ids.append(player["_id"])
        
        # Per la squadra con abbreviation = team, creo un nuovo campo (con $set) chiamato "Players" che come valore avrà la lista di id di giocatori di quella squadra 
        col_teams.update_one({"abbreviation" : team}, {"$set" : {"Players" : player_ids}})


def embed_teams_in_games(col_teams, col_games):
    # Prendo le abbreviazioni e gli id di tutti i team dalla collection teams
    get_teams = col_teams.find()

    team_abbreviations = list()
    team_ids = list()

    for res in get_teams:
        team_abbreviations.append(res["abbreviation"])
        team_ids.append(res["_id"])

    # E li aggiungo ad un dizionario
    teams = dict()
    teams["abbreviations"] = team_abbreviations
    teams["_ids"] = team_ids

    # Per ogni coppia abbreviazione-id nel dizionario creato
    for team_abbr, team_id in zip(teams["abbreviations"], teams["_ids"]):
        # Se team_abbr è la squadra in casa, aggiunge un campo chiamato "team_id_home" con valore "team_id"
        col_games.update_many({"team_abbreviation_home" : team_abbr}, {"$set" : {"team_id_home" : team_id}})

        # Se team_abbr è la squadra fuori casa, aggiunge un campo chiamato "team_id_away" con valore "team_id"
        col_games.update_many({"team_abbreviation_away" : team_abbr}, {"$set" : {"team_id_away" : team_id}})


def embedding(col_players, col_teams, col_games):
    ## Embedding di players in teams
    embed_players_in_teams(col_players, col_teams)
    
    ## Embedding di teams in games
    embed_teams_in_games(col_teams, col_games)    


def createDB():
    # Connessione al client
    client = MongoClient("mongodb://localhost:27017/")

    # Creazione database
    db = client["BDII-NBAstats"]

    # Creazione collection
    col_players = db["Players"]

    # Creazione collection
    col_teams = db["Teams"]

    # Creazione collection
    col_games = db["Games"]
    
    ## Inserimento players
    insert_players(col_players)
    
    ## Inserimento teams
    insert_teams(col_teams)
    
    ## Inserimento games
    insert_games(col_games)
    
    ## Embedding
    embedding(col_players, col_teams, col_games)


    ## Chiusura del client
    client.close()

if __name__ == "__main__":
    createDB()