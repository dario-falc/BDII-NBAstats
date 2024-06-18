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


def insert_player(client, player):
    col_players = client["BDII-NBAstats"]["Players"]
    col_teams = client["BDII-NBAstats"]["Teams"]
    
    col_players.insert_one(player)
    
    col_teams.update_one( { "abbreviation" : player["Tm"] }, { "$push" : { "Players" : player["_id"] } } )


def update_player(client, player):
    col_players = client["BDII-NBAstats"]["Players"]
    
    for key, value in player.items():
        col_players.update_one( { "Name" : player["Name"], "Tm" : player["Tm"] }, { "$set" : { key : value } } )


def remove_player(client, player):
    col_players = client["BDII-NBAstats"]["Players"]
    col_teams = client["BDII-NBAstats"]["Teams"]
    
    get_to_remove_player = col_players.find( { "Name" : player["Name"] } )
    for player in get_to_remove_player:
        col_players.delete_one( { "_id" : player["_id"] } )
        
        col_teams.update_one( { "abbreviation" : player["Tm"] }, { "$pull" : { "Players" : player["_id"] } } )



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
    remove_player(client, player_dict)