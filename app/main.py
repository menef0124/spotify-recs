from flask import Blueprint
from flask import render_template
from flask import Flask, request, session, redirect
from flask_session import Session
from spotipy import cache_handler
import spotipy
import os
import uuid
from spotipy.oauth2 import SpotifyClientCredentials

bp = Blueprint('main', __name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

scope = "user-library-read,user-top-read,playlist-modify-public,playlist-modify-private"
sp = None
username = ""

cachesFolder = './.spotifyCache/'

if not os.path.exists(cachesFolder):
    os.makedirs(cachesFolder)


def session_cache_path():
    return cachesFolder + session.get('uuid')

@bp.route('/')
def index():
    return render_template('base.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        global username
        username = request.form['username']
        return redirect('/login')

    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler, show_dialog=True)

    if request.args.get('code'):
        auth_manager.get_access_token(request.args.get('code'))
        return redirect('/login')
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    global sp
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return redirect('/submit')


@bp.route('/submit')
def generateRecs():

    #Retrieves spotify client
    global sp
    global username

    #Gets username from user input
    #username = request.form['username']

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

    #Display top 10 tracks and accumulate audio feature values from all top 50 tracks
    for i, item in enumerate(res['items']):
        features = sp.audio_features(item['id'])
        if i < 1:
            minAcoustic = features[0]['acousticness']
            minDanceable = features[0]['danceability']
            minEnergy = features[0]['energy']
            minInstrumental = features[0]['instrumentalness']
            minLive = features[0]['liveness']
            minLoud = features[0]['loudness']
            minSpeech = features[0]['speechiness']
            minTempo = features[0]['tempo']
            minValence = features[0]['valence']
            maxAcoustic = features[0]['acousticness']
            maxDanceable = features[0]['danceability']
            maxEnergy = features[0]['energy']
            maxInstrumental = features[0]['instrumentalness']
            maxLive = features[0]['liveness']
            maxLoud = features[0]['loudness']
            maxSpeech = features[0]['speechiness']
            maxTempo = features[0]['tempo']
            maxValence = features[0]['valence']
        
        acoustic += features[0]['acousticness']
        danceable += features[0]['danceability']
        energy += features[0]['energy']
        instrumental += features[0]['instrumentalness']
        live += features[0]['liveness']
        loud += features[0]['loudness']
        speech += features[0]['speechiness']
        tempo += features[0]['tempo']
        valence += features[0]['valence']

        if i >= 1:
            if features[0]['acousticness'] <= minAcoustic:
                minAcoustic = features[0]['acousticness']
            if features[0]['acousticness'] >= maxAcoustic:
                maxAcoustic = features[0]['acousticness']
            if features[0]['danceability'] <= minDanceable:
                minDanceable = features[0]['danceability']
            if features[0]['danceability'] >= maxDanceable:
                maxDanceable = features[0]['danceability']
            if features[0]['energy'] <= minEnergy:
                minEnergy = features[0]['energy']
            if features[0]['energy'] >= maxEnergy:
                maxEnergy = features[0]['energy']
            if features[0]['instrumentalness'] <= minInstrumental:
                minInstrumental = features[0]['instrumentalness']
            if features[0]['instrumentalness'] >= maxInstrumental:
                maxInstrumental = features[0]['instrumentalness']
            if features[0]['liveness'] <= minLive:
                minLive = features[0]['liveness']
            if features[0]['liveness'] >= maxLive:
                maxLive = features[0]['liveness']
            if features[0]['loudness'] <= minLoud:
                minLoud = features[0]['loudness']
            if features[0]['loudness'] >= maxLoud:
                maxLoud = features[0]['loudness']
            if features[0]['speechiness'] <= minSpeech:
                minSpeech = features[0]['speechiness']
            if features[0]['speechiness'] >= maxSpeech:
                maxSpeech = features[0]['speechiness']
            if features[0]['tempo'] <= minTempo:
                minTempo = features[0]['tempo']
            if features[0]['tempo'] >= maxTempo:
                maxTempo = features[0]['tempo']
            if features[0]['valence'] <= minValence:
                minValence = features[0]['valence']
            if features[0]['valence'] >= maxValence:
                maxValence = features[0]['valence']

        #Basically hardcoded track and artist seeds
        if i < 1:
            trackSeed.append(item['id'])
            artistSeed.append(item['artists'][0]['id'])

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
        min_accousticness="{:.2f}".format(minAcoustic),
        min_danceability="{:.2f}".format(minDanceable),
        min_energy="{:.2f}".format(minEnergy),
        min_instrumentalness="{:.2f}".format(minInstrumental),
        min_liveness="{:.2f}".format(minLive),
        min_loudness="{:.2f}".format(minLoud),
        min_speechiness="{:.2f}".format(minSpeech),
        min_tempo="{:.2f}".format(minTempo),
        min_valence="{:.2f}".format(minValence),
        target_acousticness="{:.2f}".format(acoustic),
        target_danceability="{:.2f}".format(danceable),
        target_energy="{:.2f}".format(energy),
        target_instrumentalness="{:.2f}".format(instrumental),
        target_liveness="{:.2f}".format(live),
        target_loudness="{:.2f}".format(loud),
        target_speechiness="{:.2f}".format(speech),
        target_tempo="{:.2f}".format(tempo),
        target_valence="{:.2f}".format(valence),
        max_accousticness="{:.2f}".format(maxAcoustic),
        max_danceability="{:.2f}".format(maxDanceable),
        max_energy="{:.2f}".format(maxEnergy),
        max_instrumentalness="{:.2f}".format(maxInstrumental),
        max_liveness="{:.2f}".format(maxLive),
        max_loudness="{:.2f}".format(maxLoud),
        max_speechiness="{:.2f}".format(maxSpeech),
        max_tempo="{:.2f}".format(maxTempo),
        max_valence="{:.2f}".format(maxValence),
        limit=100,
        )

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
