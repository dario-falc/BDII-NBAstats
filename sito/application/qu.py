from pymongo import MongoClient

def vittorie_tot(client):
    col_games = client["BDII-NBAstats"]["Games"]
    
    query = col_games.aggregate([
        #{ "$match" : { "$or" : [ {"winner" : "Home"}, {"winner" : "Away"}]}},
        { "$group" : { "_id" : {
            "team_id" : {
                "$cond" : { "if" : { "$eq" : [ "$winner", "Home" ] }, "then" : "$team_id_home" , "else" : "$team_id_away" }
                },
                "team_name" : {
                "$cond" : { "if" : { "$eq" : [ "$winner", "Home" ] }, "then" : "$team_name_home" , "else" : "$team_name_away" }
                }

            },
                    "games_won" : { "$sum" : 1 }
                    }
        },
        { "$set" : { "games_lost" : { "$subtract" :  [ 82,  "$games_won" ]  } } }, 
        { "$sort" : { "games_won" : -1 } }
    ])
    
    return query


def vittorie_casa(client):
    col_games = client["BDII-NBAstats"]["Games"]
    
    query = col_games.aggregate([
        { "$match" : { "winner" : "Home" }},
        { "$group" : { "_id" : "$team_id_home",
                    "games_won" : { "$sum" : 1 }
                    }
        },
        { "$set" : { "games_lost" : { "$subtract" :  [ 41,  "$games_won" ]  } } },
        { "$sort" : { "games_won" : -1 } }
    ])
    
    return query


def vittorie_transf(client):
    col_games = client["BDII-NBAstats"]["Games"]
    
    query = col_games.aggregate([
        { "$match" : { "winner" : "Away" }},
        { "$group" : { "_id" : "$team_id_away",
                    "games_won" : { "$sum" : 1 }
                    }
        },
        { "$set" : { "games_lost" : { "$subtract" :  [ 41,  "$games_won" ]  } } }, 
        { "$sort" : { "games_won" : -1 } }
    ])
    
    return query


def inserimento_giocatore(client, player):
    col_players = client["BDII-NBAstats"]["Players"]
    col_teams = client["BDII-NBAstats"]["Teams"]
    
    col_players.insert_one(player)
    col_teams.update_one( { "abbreviation" : player["Tm"] }, { "$push" : { "Players" : player["_id"] } } )
    giocatore_creato=col_players.find_one({"id": player["_id"]})
    return giocatore_creato
    

def modifica_giocatore(client, player):

    col_players = client["BDII-NBAstats"]["Players"]
    
    for key, value in player.items():
        print(key," ", value)
        col_players.update_one( { "Name" : player["Name"], "Tm" : player["Tm"] }, { "$set" : { key : value } } )
    giocatore_mod=col_players.find_one({"Name": player["Name"], "Tm" : player["Tm"]})
    return giocatore_mod

def rimozione_giocatore(client, player):
    col_players = client["BDII-NBAstats"]["Players"]
    col_teams = client["BDII-NBAstats"]["Teams"]
    
    get_to_remove_player = col_players.find( { "Name" : player["Name"] } )
    for player in get_to_remove_player:
        col_players.delete_one( { "_id" : player["_id"] } )
        
        col_teams.update_one( { "abbreviation" : player["Tm"] }, { "$pull" : { "Players" : player["_id"] } } )


def top_scorer(client):
    col_players = client["BDII-NBAstats"]["Players"]

    query = col_players.find( {}, { "_id" : 0, "Name" : 1, "Tm" : 1, "PTS" : 1 } ).sort( { "PTS" : -1} ).limit(5)

    return query


def top_3_pointers(client):
    col_players = client["BDII-NBAstats"]["Players"]

    query = col_players.find( {}, { "_id" : 0, "Name" : 1, "Tm" : 1, "3P" : 1 } ).sort( { "3P" : -1} ).limit(5)

    return query


def top_assists(client):
    col_players = client["BDII-NBAstats"]["Players"]

    query = col_players.find( {}, { "_id" : 0, "Name" : 1, "Tm" : 1, "AST" : 1 } ).sort( { "AST" : -1} ).limit(5)

    return query
    

def top_rebounds(client):
    col_players = client["BDII-NBAstats"]["Players"]

    query = col_players.find( {}, { "_id" : 0, "Name" : 1, "Tm" : 1, "TRB" : 1 } ).sort( { "TRB" : -1} ).limit(5)

    return query
    

def find_players_from_team(client, team):
    col_players = client["BDII-NBAstats"]["Players"]
    col_teams = client["BDII-NBAstats"]["Teams"]
    
    query = col_teams.find( { "abbreviation" : team["abbreviation"] } )

    players_list = list()
    
    for res in query:
        #print(res)
        for playerID in res["Players"]:
            for player_from_team in col_players.find( { "_id" : playerID } ):
                players_list.append(player_from_team)
    

    return players_list


if __name__ == "__main__":
    
    client = MongoClient("mongodb://localhost:27017/")
    
    ## Prova tabellone partite
    #res = get_game_results_away(client)
    
    #for r in res:
    #    print(r)


    ## Prova inserimento/cancellazione giocatore
    player_dict = { "Name" : "Prova123",
                    "Pos" : "nu cazz",
                    "Age" : "16",
                    "Tm": "ATL"}
    
    
    #insert_player(client, player_dict)
    #remove_player(client, player_dict)

    player_update = { "Name" : "Prova123",
                      "Mangiato" : "Si",
                      "fessrmammt" : "Pure",
                      "AAAAAAAa" : "aaaaaaAAA"}

    #update_player(client, player_update)
    #remove_player(client, player_dict)
    
    #for res in top_scorer(client):
    #    print(res)
    
    #for res in top_3_pointers(client):
    #    print(res)
    
    #for res in top_assists(client):
    #    print(res)
    
    #for res in top_rebounds(client):
    #    print(res)
    
    cerca = { "abbreviation" : "GSW" }
    
    for res in find_players_from_team(client, cerca):
        print(res)