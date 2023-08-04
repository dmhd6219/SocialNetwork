# Flask-Spotify-Social Network

![License](https://img.shields.io/github/license/dmhd6219/SocialNetwork)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Flask](https://img.shields.io/badge/flask-2.0%2B-blue.svg)](https://flask.palletsprojects.com/en/2.0.x/)

A social network web application built on Flask that allows users to log in via their Spotify account.
The web app seamlessly integrates with Spotify's API to enable users to share their favorite music tracks, playlists,
and discover new music with their friends.

## Features

- User authentication via Spotify account
- View and follow friends' music activities
- Share music tracks and playlists on the feed
- Like, comment, and repost music posts
- User profile customization
- Search for music tracks, albums, and artists on Spotify

## Installation

1. Clone this repository to your local machine:

```bash
git clone https://github.com/dmhd6219/SocialNetwork.git
```

2. Set up a virtual environment (optional but recommended):

```bash
cd SocialNetwork
python -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

To run the web application, you will need to set up a Spotify Developer account and obtain the necessary API
credentials. Follow these steps:

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and log in with your Spotify
   account.
2. Create a new application and note down the `Client ID` and `Client Secret`.
3. In the project directory, create a new file named `.env` and add the following lines:

```env
SPOTIPY_CLIENT_ID = 'your_spotify_client_id'
SPOTIPY_CLIENT_SECRET = 'your_spotify_client_secret'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080/callback'  # Change this if required
```

Replace `your_spotify_client_id` and `your_spotify_client_secret` with the credentials obtained in step 2.

## Usage

1. Run the Flask development server:

```bash
python main.py
```

2. Open your web browser and go to `http://localhost:8080`.

## Deployment

To deploy the web app for public use, consider using platforms like Heroku, AWS, or others that support Flask
applications.

## Contributing

Contributions are welcome! If you want to add new features, fix bugs, or improve the existing codebase, feel free to
open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---

# Screenshots

![Profile page](/screenshots/Screenshot_3.png)
![Weather page](/screenshots/Screenshot_4.png)
![Music page](/screenshots/Screenshot_5.png)
![Music Artist page](/screenshots/Screenshot_6.png)
![Music Album page](/screenshots/Screenshot_7.png)