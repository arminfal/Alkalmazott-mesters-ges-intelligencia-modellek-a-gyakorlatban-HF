import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import requests
import base64
import webbrowser
from flask import Flask, jsonify, request, render_template
import threading
import time
from flask import Flask, request
from multiprocessing import Process

client_id = 'x'
client_secret = 'x'

# Define a function to start the Flask server
def start_server():
    app.run(port=8000)

# Start the Flask server in a separate process
server_process = Process(target=start_server)
server_process.start()

# Wait for the redirect to occur
while code is None:
    time.sleep(10)

def refresh_access_token(refresh_token):
    # Prepare the header
    encoded = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('ascii')
    headers = {
        'Authorization': f'Basic {encoded}',
    }

    # Prepare the payload
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    # Send the request
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=payload)

    # Parse the response
    data = response.json()

    # Return the access token and the refresh token
    return data['access_token'], data['refresh_token']

def get_authorization_code():
    # Spotify API credentials
    client_id = 'x'
    redirect_uri = 'http://localhost:8000/callback'
    scope = 'user-top-read'  # Replace with the scopes you need

    # Prepare the authorization URL
    url = f'https://accounts.spotify.com/authorize?response_type=code&client_id=x&redirect_uri=http://localhost:8000/callback&scope=user-top-read'

    # Open the authorization URL in the user's browser
    webbrowser.open(url)



app = Flask(__name__)
code = None

@app.route('/callback')
def callback():
    global code
    code = request.args.get('code')
    access_token, refresh_token = get_access_token()
    
    # Set up the headers for the API requests
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Fetch the user's top artists
    response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers)
    data = response.json()
    artist_ids = [artist['id'] for artist in data['items']]

    # Use the artist IDs to get recommendations
    params = {
        'seed_artists': ','.join(artist_ids),
    }
    response = requests.get('https://api.spotify.com/v1/recommendations', headers=headers, params=params)
    data = response.json()
    recommendations = [track['name'] for track in data['tracks']]

    return jsonify(recommendations)

while code is None:
    try:
        # This is just an example, replace with your actual authorization URL    client_id = 'x'
        client_secret = 'x' 
        redirect_uri = 'http://localhost:8000/callback'
        scope = 'user-top-read' 

        # Prepare the authorization URL
        authorization_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}'

        webbrowser.open(authorization_url)
        time.sleep(10)  # wait for some time for the user to authorize the app
    except Exception as e:
        print(f"An error occurred: {e}")
def get_access_token():
     # Spotify API credentials
    client_id = 'x'
    client_secret = 'x' 
    redirect_uri = 'http://localhost:8000/callback'
    scope = 'user-top-read' 

    # Prepare the authorization URL
    authorization_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}'

    # Prepare the header
    encoded = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('ascii')
    headers = {
        'Authorization': f'Basic {encoded}',
    }
    
    print(authorization_url)
    print(headers)
    # Open the authorization URL in the user's browser
    webbrowser.open(authorization_url)

    # Start a web server to listen for the redirect
    threading.Thread(target=app.run, kwargs={'port': 8000}).start()

    # Wait for the redirect to occur
    while code is None:
        time.sleep(10000)

    # Prepare the payload
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }

    # Send the request
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=payload)
    # Parse response
    data = response.json()


    # Check if 'access_token' is in the response
    if 'access_token' not in data:
        print(f"'access_token' not found in the response: {data}")
        return None
    # Return the access token and the refresh token
    return data['access_token'], data['refresh_token']
def get_top_artists():
    # Get access token
    tokens = get_access_token()
    if tokens is None:
        print("Failed to get access token")
        return None

    access_token, refresh_token = tokens
    # Define headers
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Initialize URL for the first request
    url = 'https://api.spotify.com/v1/me/top/artists'

    # Initialize list to store all artists
    all_artists = []

    while url:
        # Send request to Spotify API
        response = requests.get(url, headers=headers)

        # Parse response
        data = response.json()

        # Extract artists from this page and add them to the list
        all_artists.extend([artist['name'] for artist in data['items']])

        # Get the URL for the next page
        url = data['next']

    return all_artists

# Get access token
access_token = get_access_token()

# Define headers
headers = {
    'Authorization': f'Bearer {access_token}',
}

response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers)

# Parse response
data = response.json()

# Extract needed data

top_artists = get_top_artists()

# Print top artists
for artist in top_artists:
    print(artist)
# Load data
#data = pd.read_csv('music_preferences.csv')  #spotify kód
data = pd.DataFrame({
    'genre': ['pop', 'rock', 'jazz', 'pop', 'blues'],
    'artist': ['Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5'],
    'song_name': ['Song1', 'Song2', 'Song3', 'Song4', 'Song5']
})

# Preprocess data
data.drop_duplicates(inplace=True)
data.fillna(0, inplace=True)

# Extract features
features = data[['genre', 'artist']]

# Scale features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Split data into training and test sets
X_train, X_test = train_test_split(scaled_features, test_size=0.2, random_state=42)

# Train model
model = NearestNeighbors(n_neighbors=5)
model.fit(X_train)

@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        # Get user input
        genre = request.form.get('genre')
        artist = request.form.get('artist')

        # Make a recommendation
        song = [genre, artist]  # User input
        song = scaler.transform([song])  # Scale user input
        recommendation = model.kneighbors(song, return_distance=False)

        # Get recommendation
        recommended_songs = data.iloc[recommendation[0]]

        return render_template('index.html', recommended_songs=recommended_songs)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
