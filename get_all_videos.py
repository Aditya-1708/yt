from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os
import pandas as pd

# Scopes for accessing YouTube data
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# Step 1: Authenticate and get credentials
creds = None
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",  # replace with your JSON file
        SCOPES
    )
    creds = flow.run_local_server(port=0)
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

# Step 2: Build YouTube service
youtube = build("youtube", "v3", credentials=creds)

# Step 3: Get channel uploads playlist
handle = "nagarajdd86"  # no @ needed
request = youtube.channels().list(
    part="id,snippet,contentDetails",
    forHandle=handle
)
response = request.execute()

if not response["items"]:
    raise Exception(f"Channel not found with handle {handle}")

uploads_playlist = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# Step 4: Fetch all videos from the playlist
def get_all_videos(youtube, playlist_id):
    videos = []
    next_page_token = None
    while True:
        playlist_request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()
        for item in playlist_response["items"]:
            videos.append({
                "title": item["snippet"]["title"],
                "video_id": item["snippet"]["resourceId"]["videoId"]
            })
        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break
    return videos

yt_videos = get_all_videos(youtube, uploads_playlist)
yt_df = pd.DataFrame(yt_videos)

# Step 5: Load your Excel file (no header)
my_df = pd.read_excel("P4U - Nagaraj sir.xlsx", header=None)

# First column = titles
my_df.columns = ["title"] + [f"col{i}" for i in range(2, len(my_df.columns)+1)]

# Step 6: Merge to get video_id
merged = my_df.merge(yt_df, on="title", how="left")
merged = merged.drop_duplicates(subset=["video_id"], keep="first")
# Step 7: Insert video_id as the 3rd column
col_order = []
if len(merged.columns) >= 2:
    col_order = [merged.columns[0], merged.columns[1], "video_id"] + [c for c in merged.columns if c not in ["title", "col2", "video_id"]]
    merged = merged[col_order]

# Step 8: Save to Excel
merged.to_excel("videos_with_ids.xlsx", index=False, header=False)

print("✅ Matching complete! Saved to videos_with_ids.xlsx")
