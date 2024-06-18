from flask import Flask
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['BDII-NBAstats'] 
players_collection = db['Players']
col_games = db['Games']
teams_collection = db['Teams']

def vittorie_tot():
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
    '''
    for res in query:
        print(res)
    '''
    return query
def vittorie_casa():
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
def vittorie_transf():
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