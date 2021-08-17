import requests
import json
import csv
import argparse
import xlwt 
from xlwt import Workbook 

FPL_URL = "https://fantasy.premierleague.com/api/"
USER_SUMMARY_SUBURL = "element-summary/"
LEAGUE_CLASSIC_STANDING_SUBURL = "leagues-classic/"
LEAGUE_H2H_STANDING_SUBURL = "leagues-h2h-standings/"
STANDINGS = "/standings/"
TEAM_ENTRY_SUBURL = "entry/"
PLAYERS_INFO_SUBURL = "bootstrap-static"
PLAYERS_INFO_FILENAME = "allPlayersInfo.json"
PARTICIPANTS_INFO_FILENAME = "allParticipantsInfo.json"

USER_SUMMARY_URL = FPL_URL + USER_SUMMARY_SUBURL
PLAYERS_INFO_URL = FPL_URL + PLAYERS_INFO_SUBURL
START_PAGE = 1

RESULTS_FILE = "GAMEWEEK_RESULTS_"

class TeamDetails (object):

    def __init__(self, teamId, teamName, playerName):
        self.teamId = teamId
        self.teamName = teamName
        self.playerName = playerName
        self.goalsConceded = 0
        self.goalsScored = 0
        self.points = 0
        self.hits = 0
        self.chipUsed = ""
        self.isChipUsed = 0

    def PrintDetails(self):
        print ("TeamId: " + str(self.teamId) + " TeamName: " + self.teamName.encode('utf-8') + " PlayerName: " + str(self.playerName) + " Points: " + str(self.points) + " hits: " + str(self.hits) + " IsChipUsed " + str(self.isChipUsed) + " ChipUsed " + str(self.chipUsed) + " GoalsConceded: " + str(self.goalsConceded) + " GoalsScored: " + str(self.goalsScored) )
        
    def AddTeamDetails(self, points, hits, chipUsed, goalsConceded, goalsScored):
        self.goalsConceded = goalsConceded
        self.goalsScored = goalsScored
        self.points = points
        self.hits = hits
        self.chipUsed = chipUsed
        if chipUsed != "":
            isChipUsed = 1
        
    def __iter__(self):
        return iter([self.teamName, self.playerName, self.points, self.hits, self.chipUsed, self.goalsScored, self.goalsConceded])

def saveJsonResponse(filename, jsonData):
    with open(filename, 'w') as outfile:
        json.dump(jsonData, outfile)

# Get users in league: https://fantasy.premierleague.com/drf/leagues-classic-standings/336217?phase=1&le-page=1&ls-page=5
def getUserEntryIds(league_id, ls_page, league_Standing_Url):
    payload = {"login": "yourlogin@xyz.com", "password": "yourpassword",
           "app": "plfpl-web", "redirect_uri": "https://fantasy.premierleague.com/"}
    
    league_url = league_Standing_Url + str(league_id) + "/standings?page_new_entries=1&page_standings=" + str(ls_page)
    
    with requests.Session() as session:
        session.post("https://users.premierleague.com/accounts/login/", data=payload)
        jsonResponse = session.get(league_url).json()    
        standings = jsonResponse["standings"]["results"]
        if not standings:
            print("no more standings found!")
            return None
        teams = []

        for player in standings:
            teams.append(TeamDetails( player["entry"], player["entry_name"], player["player_name"]))

    return teams

#get points, hits and chip used
def getParticipantDetailedInfoForGameweek(entry_id, GWNumber):
    eventSubUrl = "event/" + str(GWNumber) + "/picks"
    playerTeamUrlForSpecificGW = FPL_URL + TEAM_ENTRY_SUBURL + str(entry_id) + "/" + eventSubUrl + "/"
    # print(playerTeamUrlForSpecificGW)
    r = requests.get(playerTeamUrlForSpecificGW)
    jsonResponse = r.json()    
    #points: actual points - hits if any 
    points = jsonResponse["entry_history"]["points"] - jsonResponse["entry_history"]["event_transfers_cost"]
    hits = 0
    if jsonResponse["entry_history"]["event_transfers_cost"] != "0":
        hits = int(jsonResponse["entry_history"]["event_transfers_cost"]/4)
    chipused = jsonResponse["active_chip"]
    return points, hits, chipused

# writes the results to csv file
def writeResultsToFile(results, GWnumber):
    with open(RESULTS_FILE + str(GWnumber) + ".csv", 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['Team Name', 'Player Name', 'Points', 'Hits', 'Chip Used', 'Goals scored', 'Goals Conceded'])
        for row in results:
            b = []
            for index, val in enumerate(list(row)):
                if index == 0:
                    b.append(val.encode('utf-8'))
                else:
                    b.append(str(val))
            csv_out.writerow(b)
       
# writes the results to csv file
def writeResultsToExcel(results, GWnumber):
    wb = Workbook(RESULTS_FILE + str(GWnumber) + ".xlsx") 
    worksheet = wb.add_sheet('Sheet 1')     
    row = 1
    col = 0    
    
    worksheet.write(0, col, 'Team Name') 
    worksheet.write(0, col + 1, 'Player Name') 
    worksheet.write(0, col + 2, 'Points') 
    worksheet.write(0, col + 3, 'Hits') 
    worksheet.write(0, col + 4, 'Chip Used') 
    worksheet.write(0, col + 5, 'Goals scored') 
    worksheet.write(0, col + 6, 'Goals Conceded') 
    
    for row in (results):         
        worksheet.write(row, col, row.teamName) 
        worksheet.write(row, col + 1, row.playerName) 
        worksheet.write(row, col + 2, row.points) 
        worksheet.write(row, col + 3, row.hits) 
        worksheet.write(row, col + 4, row.chipUsed) 
        worksheet.write(row, col + 5, row.goalsScored) 
        worksheet.write(row, col + 6, row.goalsConceded) 
        row += 1
    
    workbook.close() 

#get goals conceded and goals scored
def getGoalDetailsForTeam(entry_id, GWNumber, benchboostUsed =0):
    eventSubUrl = "event/" + str(GWNumber) + "/picks"
    playerTeamUrlForSpecificGW = FPL_URL + TEAM_ENTRY_SUBURL + str(entry_id) + "/" + eventSubUrl + "/"
    r = requests.get(playerTeamUrlForSpecificGW)
    jsonResponse = r.json()
    picks = jsonResponse["picks"]
    elements = []
    playerSubUrl =  "https://fantasy.premierleague.com/api/element-summary/"
    goalsConceded = 0
    goalsScored = 0
    for pick in picks:
        url = playerSubUrl + str(pick["element"]) +"/"
        if int(pick["position"]) > 11 and benchboostUsed == 0:
            continue
        r= requests.get(url)
        jsonResponse = r.json()        
        history = jsonResponse["history"]
        for week in history: 
            if int(week["round"]) == int(GWNumber):
                goalsConceded = goalsConceded + int(week["goals_conceded"]) 
                goalsScored = goalsScored + int(week["goals_scored"])
    
    return goalsConceded, goalsScored


# Main Script
parser = argparse.ArgumentParser(description='Get players picked in your league in a certain GameWeek')
parser.add_argument('-l','--league', help='league entry id', required=True)
parser.add_argument('-g','--gameweek', help='gameweek number', required=True)
args = vars(parser.parse_args())

totalNumberOfPlayersCount = 0
pageCount = START_PAGE
GWNumber = args['gameweek']
leagueIdSelected = args['league']
leagueStandingUrl = FPL_URL + LEAGUE_CLASSIC_STANDING_SUBURL
teams = []

while (True):
    teams = getUserEntryIds(leagueIdSelected, pageCount, leagueStandingUrl)    
    
    if teams is None:
        print("breaking as no more player entries")
        break

    totalNumberOfPlayersCount += len(teams)
    print("parsing pageCount: " + str(pageCount) + " with total number of players so far:" + str(
        totalNumberOfPlayersCount))
        
    for team in teams:
        points, hits, chipused = getParticipantDetailedInfoForGameweek(team.teamId, GWNumber)   
        print("Step 1 done")
        goalsConceded, goalsScored = getGoalDetailsForTeam(team.teamId, GWNumber,(chipused=="bboost")) 
        print ("Step 2 done")
        team.AddTeamDetails(points, hits, chipused, goalsConceded, goalsScored)
    
    teams.sort(key = lambda x: x.goalsConceded, reverse=False)
    teams.sort(key = lambda x: x.goalsScored, reverse=True)
    teams.sort(key = lambda x: x.hits, reverse=False)
    teams.sort(key = lambda x: x.isChipUsed, reverse=False)
    teams.sort(key = lambda x: x.points, reverse=True)   
        
    for team in teams:
        team.PrintDetails()
        
    writeResultsToFile(teams, GWNumber)
    
    # writeResultsToExcel(teams, GWNumber)
    
    pageCount += 1

