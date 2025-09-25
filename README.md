# Spotify Song Tracker 🎵

A Python application that tracks your Spotify listening history and maintains a count of your most played songs. Perfect for music enthusiasts who want to keep track of their favorite tracks and discover their listening patterns.

## ✨ Features

- Tracks currently playing songs from your Spotify account
- Maintains a local database of played songs with play counts
- Handles song repeats and play tracking intelligently
- Graceful error handling and automatic retries
- Simple CSV-based storage for easy data analysis
- Clean, object-oriented codebase

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Spotify Developer Account
- `pip` (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/your-username/Spotify_API.git](https://github.com/your-username/Spotify_API.git)
   cd Spotify_API
   ```
2. **Create and activate a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up Spotify Developer Application**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Note down your `Client ID` and `Client Secret`
   - Add `http://127.0.0.1:3000/callback` as a Redirect URI in your app settings

5. **Configure Environment Variables Create a .env file in the project root with**
    ```python
    CLIENT_ID="your_client_id_here"
    CLIENT_SECRET="your_client_secret_here"
    REDIRECT_URI="http://127.0.0.1:3000/callback"
    ```
## 🎯 Usage
1. **Run the application**
   ```bash
   python main.py
   ```
2. **First-time setup**
    - The first time you run the app, it will open a browser window asking you to log in to Spotify
    - After logging in, you'll be redirected to a localhost URL (this is expected)
    - The app will now start tracking your currently playing songs
3. **Viewing your song data**
    - Your listening history is saved to Data/songs.csv
    - The CSV contains columns: Song_ID, Song , Artists, and Count

## 📊 Data Format
The application maintains a CSV file with the following structure:

| Song_ID |       Song       | Artists | Count  |
|:-----|:----------------:|:-------:|:------:|
| 1E4TxDKyJXBp0DZVUwURdG   |Hot Hot Racing Car| ['Go2'] |   1    |
| 7kXporKYnFeKSnoMBbvwYL   |      Dancing On The Street	      |   ['David Dima']   | 2 |

## 🙏 Acknowledgments
 - Spotify Web API

Made with ❤️ by **Andrzej Nowak** 
