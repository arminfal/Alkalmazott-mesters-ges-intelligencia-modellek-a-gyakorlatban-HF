import base64
import sys
import requests
import webbrowser
import time
import threading
from flask import Flask, request
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from flask import Flask, request, render_template, redirect, session
from werkzeug.serving import make_server
import csv
from werkzeug.serving import run_simple

app = Flask(__name__)
code = None
app.secret_key = 'asdsadsadsadsad'

client_id = '769557ef33434314b3b5260275e7d407'
client_secret = '156228aa0dc0409c94512f394f7ba441'
redirect_uri = 'http://localhost:8000/callback'
@app.route('/authorize', methods=['GET', 'POST'])
def authorize():
    authorization_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=user-top-read'
    return redirect(authorization_url, code=302)

@app.route('/callback')
def callback():
    global code
    code = request.args.get('code')

    if code is None:
        print("Failed to get authorization code")
        return redirect("/", code=302)

    # Get the access token using the authorization code
    tokens = get_access_token()
    if tokens is None:
        print("Failed to get access token")
        return redirect("/", code=302)

    access_token, refresh_token = tokens
    session['access_token'] = access_token  # Store the access token in a session variable

    return redirect("/search", code=302)
def get_access_token():
    global code

    if code is None:
        print("Failed to get authorization code")
        return None

    encoded = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('ascii')
    headers = {'Authorization': f'Basic {encoded}',}

    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=payload)
    data = response.json()


    if 'access_token' not in data:
        print(f"'access_token' not found in the response: {data}")
        if 'error' in data and data['error'] == 'invalid_grant':
            print("Invalid authorization code. Please try again.")
        return None

    return data['access_token'], data['refresh_token']
def get_top_artists(access_token):  # Add an access_token parameter
    headers = {'Authorization': f'Bearer {access_token}',}
    url = 'https://api.spotify.com/v1/me/top/artists'
    all_artists = []
    try:
        with open('music_preferences.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["artist", "genre"])  # Write header

            while url:
                # Send request to Spotify API
                response = requests.get(url, headers=headers)

                # Parse response
                data = response.json()
                print(data)  # Print the response   

                # Extract artists from this page and add them to the list
                if 'items' in data:
                    for artist in data['items']:
                        if 'name' in artist and 'genres' in artist:
                            all_artists.append(artist['name'])
                            writer.writerow([artist['name'], artist['genres'][0] if artist['genres'] else ""])  # Write artist name and first genre
                        else:
                            print("'name' or 'genres' key not found in the artist object")
                            return None
                else:
                    print("'items' key not found in the response")
                    return None
                # Get the URL for the next page
                url = data['next']
            with open('music_preferences.csv', 'r') as file:
                print(file.read())  # Print the contents of the file
    except Exception as e:
        print(f"Failed to write to CSV file: {e}")
        return None

    return all_artists
'''
# Extract needed data
top_artists = get_top_artists()
if top_artists is None:
    print("Failed to get top artists")
    sys.exit()  # Stop the script

# Load data
try:
    data = pd.read_csv('music_preferences.csv')  #spotify kód
except pd.errors.EmptyDataError:
    print("The 'music_preferences.csv' file is empty or doesn't exist.")
    sys.exit()  # Stop the script

# Preprocess data
data.drop_duplicates(inplace=True)
data.fillna(0, inplace=True)

# Extract features
try:
    features = data[['artist', 'genre']]
except KeyError:
    print("The 'artist' column is not in the DataFrame.")
    sys.exit()  # Stop the script
    
# Check if features DataFrame is empty
if features.empty:
    print("The 'features' DataFrame is empty.")
    sys.exit()  # Stop the script

# Scale features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Split data into training and test sets
X_train, X_test = train_test_split(scaled_features, test_size=0.2, random_state=42)

# Train model
model = NearestNeighbors(n_neighbors=5)
model.fit(X_train)
'''
@app.route('/search', methods=['GET', 'POST'])
def search():
    artist_name = request.form.get('artist')
        # Check if the session has an access token
    if request.method == 'POST':
        # Store the artist name in the session so it can be used after the user is redirected back from the Spotify authorization page
        session['artist'] = request.form.get('artist')

        # Redirect the user to the Spotify authorization page
        return redirect('/authorize', code=302)

    # Check if the session has an access token
    if 'access_token' not in session:
        # No access token in the session, redirect to the authorize route
        return redirect('/authorize', code=302)
    artist_name = session.get('artist')
    # Get access token
    tokens = get_access_token()
    if tokens is None:
        print("Failed to get access token")
        return render_template('search_results.html', error="Failed to get access token")

    access_token, refresh_token = tokens
    headers = {'Authorization': f'Bearer {access_token}',}

    # Search for the artist
    search_url = f'https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1'
    response = requests.get(search_url, headers=headers)
    data = response.json()

    if 'artists' not in data or not data['artists']['items']:
        return render_template('search_results.html', error="Artist not found")

    artist = data['artists']['items'][0]

    # Get the artist's genres
    genres = artist['genres']

    if not genres:
        return render_template('search_results.html', error="No genres found for this artist")

    # Search for artists of the same genre
    genre = genres[0]  # Use the first genre
    search_url = f'https://api.spotify.com/v1/search?q=genre:{genre}&type=artist&limit=5'
    response = requests.get(search_url, headers=headers)
    data = response.json()

    if 'artists' not in data or not data['artists']['items']:
        return render_template('search_results.html', error="No artists found for this genre")

    similar_artists = [artist['name'] for artist in data['artists']['items']]

    # Return a response
    return render_template('search_results.html', artist_name=artist_name, similar_artists=similar_artists)

@app.route('/', methods=['GET', 'POST'])
def index():
        # Check if the session has an access token

    artist = None  # Define artist here
    genres = None
    if request.method == 'POST':
        # Get user input
        artist_name = request.form.get('artist')

        # Get access token
        tokens = get_access_token()
        if tokens is None:
            print("Failed to get access token")
            return render_template('index.html', error="Failed to get access token")

        access_token, refresh_token = tokens
        headers = {'Authorization': f'Bearer {access_token}',}

        # Search for the artist
        search_url = f'https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1'
        response = requests.get(search_url, headers=headers)
        data = response.json()

        if 'artists' not in data or not data['artists']['items']:
            return render_template('index.html', error="Artist not found")

        artist = data['artists']['items'][0]

        # Get the artist's genres
        if artist is not None and 'genres' in artist:
            genres = artist['genres']
    if not genres:
        return render_template('index.html', error="No genres found for this artist")

    # Search for artists of the same genre
    genre = genres[0]  # Use the first genre
    search_url = f'https://api.spotify.com/v1/search?q=genre:{genre}&type=artist&limit=5'
    response = requests.get(search_url, headers=headers)
    data = response.json()

    if 'artists' not in data or not data['artists']['items']:
        return render_template('index.html', error="No artists found for this genre")

    similar_artists = [artist['name'] for artist in data['artists']['items']]

    return render_template('index.html', similar_artists=similar_artists)
if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)