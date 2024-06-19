from flask import Flask, render_template, request
from pymongo import MongoClient
import application.qu as qu
import math

app = Flask(__name__)


## Setup mongo

client = MongoClient('mongodb://localhost:27017/')
db = client['BDII-NBAstats'] 
players_collection = db['Players']
games_collection = db['Games']
teams_collection = db['Teams']


@app.route('/') #url dinamico
def index():
    
    #recuperiamo i dati dalla collezione
    
   
    return render_template('index.html')


@app.route('/topPlayer') #top player
def topPlayer():
    topPoint=list(qu.top_scorer(client))
    topAssists=list(qu.top_assists(client))
    top3Points=list(qu.top_3_pointers(client))
    topRebound=list(qu.top_rebounds(client))
    table_rows_point=""
    table_rows_assist=""
    table_rows_3point=""
    table_rows_rebound=""
    for item in topPoint:    
            table_rows_point += "<tr>\n"
            for key, value in item.items():
                table_rows_point += f"    <td> {value} </td>\n"
            table_rows_point += "</tr>\n"
    for item in topAssists:    
            table_rows_assist += "<tr>\n"
            for key, value in item.items():
                table_rows_assist += f"    <td> {value} </td>\n"
            table_rows_assist += "</tr>\n"
    for item in top3Points:    
            table_rows_3point += "<tr>\n"
            for key, value in item.items():
                table_rows_3point += f"    <td> {value} </td>\n"
            table_rows_3point += "</tr>\n"
    for item in topRebound:    
            table_rows_rebound += "<tr>\n"
            for key, value in item.items():
                table_rows_rebound += f"    <td> {value} </td>\n"
            table_rows_rebound += "</tr>\n"
    return render_template('topPlayers.html',table_rows_point=table_rows_point,table_rows_assist=table_rows_assist,table_rows_3point=table_rows_3point,table_rows_rebound=table_rows_rebound)


@app.route('/listPlayer') #list players
def listPlayer():
    players=players_collection.find()
    return render_template('listPlayers.html', players=players)


@app.route('/classificaEst')
def classificaEst():
    
    teamsEast = teams_collection.find({"conference": "East"})       #prendiamo le squadre del campionato di Est
    
    #INIZIALIZIAMO I DIZIONARI
    tutto = {"_id": None, "valori": []}
    result = list(qu.vittorie_tot(client))
    result2 = list(qu.vittorie_casa(client))
    result3 = list(qu.vittorie_transf(client))

    #DEVE ITERARE SULLE SQUADRE DI EST
    for team in teamsEast:
        singolo = {"Nome": None, "VittorieTot": None, "SconfitteTot": None, "PercVittore": None, "RisultCasa": None, "RisultTrans": None}
        for res in result:
            #print(team["_id"])
            #print(res["_id"]["team_id"],"\n")
                
            if team["_id"] == res["_id"]["team_id"]:               
                tutto["_id"] = res["_id"]["team_id"]
                singolo["Nome"] = (res["_id"]["team_name"])
                singolo["VittorieTot"] = (res["games_won"])
                singolo["SconfitteTot"] = (res["games_lost"])

                temp = singolo["VittorieTot"]
                percentualeVit = temp/82
                percentualeForm = f"{percentualeVit:.3f}"
                singolo["PercVittore"] = percentualeForm
                #print("singolo(nome):   ",singolo["Nome"])
                #print("singolo(vittorietot):   ",singolo["VittorieTot"])    
                #print("singolo(sconfittetot):   ",singolo["SconfitteTot"])
                #print("singolo(percentuale):    ",singolo["PercVittore"])                         
                break   
            
        for res in result2: 
            if team["_id"] == res["_id"]:
                temp1 = res["games_won"]
                temp2 = res["games_lost"]
                singolo["RisultCasa"] = f"{temp1}-{temp2}"
                #print("singolo(casa): ",singolo["RisultCasa"])
                break

        for res in result3:
            ''' print(team["_id"])
             print(res["_id"],"\n")'''
            if team["_id"] == res["_id"]:
                temp1 = res["games_won"]
                temp2 = res["games_lost"]
                singolo["RisultTrans"] = f"{temp1}-{temp2}"
                #print("singolo(transf): ",singolo["RisultTrans"])
                break
     
        #print(singolo)
        tutto["valori"].append(singolo)
   
    #for item in tutto['valori']:
    #    for key, value in item.items():
    #        print(f'Chiave: {key}, Valore: {value}')
    #    print()
    
    
    #print(tutto)

    # Ordiniamo la lista di dizionari dentro la chiave 'valori' in base a 'VittorieTot'
    tutto["valori"] = sorted(tutto["valori"], key=lambda x: x["VittorieTot"], reverse=True)
    
    #Creazione dinamica delle righe della tabella che formerà la classifica
    table_rows = ""
    for item in tutto['valori']:
        table_rows += "<tr>\n"
        for key, value in item.items():
            table_rows += f"    <td> {value} </td>\n"
        table_rows += "</tr>\n"
    return render_template('classificaEst.html',table_rows=table_rows)


@app.route('/classificaOvest') 
def classificaOvest():
      
    teamsWest = teams_collection.find({"conference": "West"})       #prendiamo le squadre del campionato di Est
    
    #INIZIALIZIAMO I DIZIONARI
    tutto={"_id":None,"valori":[]}
    result=list(qu.vittorie_tot(client))
    result2=list(qu.vittorie_casa(client))
    result3=list(qu.vittorie_transf(client))

    #DEVE ITERARE  SULLE SQUADRE DI EST
    for team in  teamsWest:
        singolo = {"Nome": None, "VittorieTot": None, "SconfitteTot": None, "PercVittore": None, "RisultCasa": None, "RisultTrans": None}
        for res in result:
            
            #print(team["_id"])
            #print(res["_id"]["team_id"],"\n")
                
            if team["_id"] == res["_id"]["team_id"]:               
                    tutto["_id"] = res["_id"]["team_id"]
                    singolo["Nome"] = (res["_id"]["team_name"])
                    singolo["VittorieTot"] = (res["games_won"])
                    singolo["SconfitteTot"] = (res["games_lost"])

                    temp = singolo["VittorieTot"]
                    percentualeVit = temp/82
                    percentualeForm = f"{percentualeVit:.3f}"
                    singolo["PercVittore"] = percentualeForm
                   # print("singolo(nome):   ",singolo["Nome"])
                    #print("singolo(vittorietot):   ",singolo["VittorieTot"])    
                    #print("singolo(sconfittetot):   ",singolo["SconfitteTot"])
                    #print("singolo(percentuale):    ",singolo["PercVittore"])                         
                    break   
            
        for res in result2: 
            if team["_id"] == res["_id"]:
                temp1 = res["games_won"]
                temp2 = res["games_lost"]
                singolo["RisultCasa"] = f"{temp1}-{temp2}"
                #print("singolo(casa): ",singolo["RisultCasa"])
                break

        for res in result3:
            ''' print(team["_id"])
             print(res["_id"],"\n")'''
            if team["_id"] == res["_id"]:
                temp1 = res["games_won"]
                temp2 = res["games_lost"]
                singolo["RisultTrans"] = f"{temp1}-{temp2}"
                #print("singolo(transf): ",singolo["RisultTrans"])
                break
     
        #print(singolo)
        tutto["valori"].append(singolo)
    '''
    for item in tutto['valori']:
        for key, value in item.items():
            print(f'Chiave: {key}, Valore: {value}')
        print()
    '''

    
    # Ordiniamo la lista di dizionari dentro la chiave 'valori' in base a 'VittorieTot'
    tutto["valori"] = sorted(tutto["valori"], key=lambda x: x["VittorieTot"], reverse=True)
    
    #Creazione dinamica delle righe della tabella che formerà la classifica
    table_rows = ""
    for item in tutto['valori']:
        table_rows += "<tr>\n"
        for key, value in item.items():
            table_rows += f"    <td> {value} </td>\n"
        table_rows += "</tr>\n"
    return render_template('classificaWest.html',table_rows=table_rows)
    
    
@app.route('/cercaSquadra')
def cercaSquadra():
   
    return render_template('cercaSquadra.html')

@app.route('/cercaSquadra2',methods=['POST'])
def cercaSquadra2():
    team=None
    if request.method == 'POST':
        selected_team = request.form['team']
        
        team = teams_collection.find({"abbreviation": selected_team})
        
        players=list(qu.find_players_from_team(client,team[0]))
        table_rows = ""
        giocatori=list();
        for p in players:
            singolo = {"Nome": None, "Posizione": None, "Eta": None, "PartGioc": None, "MinGioc": None, "Punti": None, "Rimbalzi": None, "Assist": None, "Stoppate": None, "Perc3": None, "Perc2": None } 
            singolo["Nome"]=p["Name"]
            singolo["Posizione"]=p["Pos"]
            singolo["Eta"]=p["Age"]
            singolo["PartGioc"]=p["G"]
            singolo["MinGioc"]=p["MP"]
            singolo["Punti"]=p["PTS"]
            singolo["Rimbalzi"]=p["TRB"]
            singolo["Assist"]=p["AST"]
            singolo["Stoppate"]=p["BLK"]
            singolo["Perc3"]=p["3P%"]
            singolo["Perc2"]=p["2P%"]
            giocatori.append(singolo)
        #print(giocatori)
        giocatori = sorted(giocatori, key=lambda x: x["Posizione"])
        ''' table_rows += "<tr>\n"
        for key, value in singolo.items():
            table_rows += f"    <td> {value} </td>\n"
        table_rows += "</tr>\n"

         '''   
        table_rows = ""
        for item in giocatori:
            table_rows += "<tr>\n"
            for key, value in item.items():
                table_rows += f"    <td> {value} </td>\n"
            table_rows += "</tr>\n"
    return render_template('cercaSquadra.html',team=team,table_rows=table_rows)