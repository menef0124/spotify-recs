from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
import spotipy
import json
import os
from spotipy.oauth2 import SpotifyImplicitGrant, SpotifyOAuth, SpotifyPKCE

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('base.html')


@bp.route('/submit', methods=['POST'])
def generateRecs():
    #Retrieves client credentials to generate access token
    credsFile = open("credentials.json")
    creds = json.load(credsFile)
    sp = spotipy.Spotify(auth_manager=SpotifyPKCE(client_id=creds['client_id'],redirect_uri=creds['redirect_uri'], scope="user-library-read,user-top-read,playlist-modify-public,playlist-modify-private", username=request.form['username']))
    #sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=creds["client_id"], client_secret=creds["client_secret"], redirect_uri=creds["redirect_uri"], scope="user-library-read,user-top-read,playlist-modify-public,playlist-modify-private"))


    #Uncomment this definition when post requests from the webpage to this script is written
    clear = lambda: os.system('cls')
    clear()

    #Gets username from user input
    username = request.form['username']


    #Define audio feature variables
    acoustic = 0.0
    danceable = 0.0
    energy = 0.0
    instrumental = 0.0
    live = 0.0
    loud = 0.0
    speech = 0.0
    tempo = 0.0
    valence = 0.0

    #Reccomendation seeds
    #   Web API only allows for a combined total of 5
    #seeds from all three seed types, so I'll probably have
    #the user select up to 5 seeds from a list before submitting
    trackSeed = []
    artistSeed = []
    genreSeed = []

    #Genre seeds are hardcoded for now
    genreSeed.append("hip-hop")
    genreSeed.append("drum-and-bass")
    genreSeed.append("jazz")

    #Get top 50 long-term tracks and their audio features. Only 10 will be displayed to the user, though
    res = sp.current_user_top_tracks(limit=50, time_range="long_term")

    print("Top 10 Long-Term Tracks")
    print("------------------------------------")
    #Display top 10 tracks and accumulate audio feature values from all top 50 tracks
    for i, item in enumerate(res['items']):
        features = sp.audio_features(item['id'])
        acoustic += features[0]['acousticness']
        danceable += features[0]['danceability']
        energy += features[0]['energy']
        instrumental += features[0]['instrumentalness']
        live += features[0]['liveness']
        loud += features[0]['loudness']
        speech += features[0]['speechiness']
        tempo += features[0]['tempo']
        valence += features[0]['valence']

        #Basically hardcoded track and artist seeds
        if i < 1:
            trackSeed.append(item['id'])
            artistSeed.append(item['artists'][0]['id'])
        #Only prints first 10 tracks
        if i < 10:
            print(i+1, item['artists'][0]['name'], "-", item['name'])
    print("------------------------------------")

    #Get average audio feature values
    acoustic /= 50.0
    danceable /= 50.0
    energy /= 50.0
    instrumental /= 50.0
    live /= 50.0
    loud /= 50.0
    speech /= 50.0
    tempo /= 50.0
    valence /= 50.0

    #Print average values
    print("Average acousticness: "  + "{:.2f}".format(acoustic))
    print("Average danceability: "  + "{:.2f}".format(danceable))
    print("Average energy: "  + "{:.2f}".format(energy))
    print("Average instrumentalness: "  + "{:.2f}".format(instrumental))
    print("Average liveness: "  + "{:.2f}".format(live))
    print("Average loudness: "  + "{:.2f}".format(loud))
    print("Average speechiness: "  + "{:.2f}".format(speech))
    print("Average tempo: "  + "{:.2f}".format(tempo))
    print("Average valence: "  + "{:.2f}".format(valence))

    print("Generating recommendations based on top tracks and averaged data...")

    #Retrieves recommendations list based on seeds and average audio feature values
    #   I'm probably gonna add min and max audio feature values by getting the lowest
    #and highest values from the list of top tracks, just for more finetuned recommendations
    recs = sp.recommendations(
        seed_tracks=trackSeed,
        seed_artists=artistSeed,
        seed_genres=genreSeed,
        target_acousticness="{:.2f}".format(acoustic),
        target_danceability="{:.2f}".format(danceable),
        target_energy="{:.2f}".format(energy),
        target_instrumentalness="{:.2f}".format(instrumental),
        target_liveness="{:.2f}".format(live),
        target_loudness="{:.2f}".format(loud),
        target_speechiness="{:.2f}".format(speech),
        target_tempo="{:.2f}".format(tempo),
        target_valence="{:.2f}".format(valence),
        limit=100)

    #Collects track IDs from recommendations
    recIds = []
    for j, item in enumerate(recs['tracks']):
        recIds.append(item['id'])

    print("Done! Creating new playlist...")

    #Creates a blank playlist with metadata
    newPl = sp.user_playlist_create(user=username, name="API Recommendations", public=False, collaborative=False, description="Recommendation playlist generated by the Spotify Web API based on user's all-time top 10 tracks")

    print("Done! Populating playlist with recommendations...")

    #Adds all recommendation tracks to the playlist
    sp.user_playlist_add_tracks(user=username, playlist_id=newPl['id'], tracks=recIds)

    return f'''
    Done! Happy listening!<br>
    <a href="https://open.spotify.com/playlist/{newPl["id"]}">Here is the link to your playlist!</a>
    '''
