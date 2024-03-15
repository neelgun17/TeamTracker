from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, support_credentials=True)

favorite_teams = [] 

@app.route('/favorite_teams', methods=['POST'])
def set_favorite_teams():
    global favorite_teams
    data = request.get_json()
    print(data)
    favorite_teams = data.get('favoriteTeams')
    return jsonify(favorite_teams)


@app.route('/favorite_teams', methods=['GET'])
def get_favorite_teams():
    return jsonify(favorite_teams)

# return list of games only including favorite teams
def filter_games(games, matches):
    teams = [team.lower() for team in games]
    filtered_list = []

    for game in matches:
        game_teams = game.split(" vs ")
        games = game_teams[0]
        matches = game_teams[1].split(" at ")[0]

        if games.lower() in teams or matches.lower() in teams:
            filtered_list.append(game)

    return filtered_list

# code to get the game schedule
def get_schedule():
    a = requests.get('https://www.skysports.com/football-fixtures')
    soup = BeautifulSoup(a.text, features="html.parser")
    teams = []
    times = []
    for date in soup.find_all(class_='fixres__header2'): # searching in that date
        for j in soup.find_all(class_='matches__date'): # gets all of the times
            times.append(j.text)
        for i in soup.find_all(class_='swap-text--bp30')[1:]:  # gets all of the teams
            if i.text != "\n\n\n\n\n\n":
                teams.append(i.text)

    # strips teams and times of all white spaces and new lines
    teams = [i.strip() for i in teams]
    times = [s.strip() for s in times]

    #appends final so it is in the format team1 vs team2 at time
    count = 0
    final = []
    for x in range(0,len(teams),2):
        final.append(teams[x]+ ' vs ' + teams[x+1] + ' at ' + times[count])
        count+=1
    return final

@app.route('/')
def home():
    return 'Welcome to the Football Schedule API!'

# Route to get all games with the user's favorite teams
@app.route('/games')
def get_games():
    # get the users favorite teams
    user_picks = favorite_teams

    # Get the game schedule
    games = get_schedule()

    # Filter the games to include only those with the user's favorite teams
    output = filter_games(user_picks, games)

    # Check if output is empty and adjust the response accordingly
    if len(output) == 0:
        response = [{"message": "None of your teams are playing"}]
    else:
        response = [{"game": game} for game in output]

    print("Returning games:", response)  # Print for debugging

    # Return the games as JSON
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=5001)