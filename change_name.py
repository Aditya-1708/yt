from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os
import pandas as pd

# Safer scope for updates
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Step 1: Authenticate and get credentials
creds = None
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",  # replace with your client secret file
        SCOPES
    )
    creds = flow.run_local_server(port=0)
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

# Step 2: Build YouTube service
youtube = build("youtube", "v3", credentials=creds)

# Step 3: Load Excel (no header row)
df = pd.read_excel("videos_with_ids.xlsx", header=None)

# Step 4: Iterate over rows
for idx, row in df.iterrows():
    new_title = row[1]   # 2nd column
    video_id  = row[2]   # 3rd column

    print(f"{video_id}\t{new_title}")

    # Get current snippet so description/tags are not erased
    current = youtube.videos().list(
        part="snippet",
        id=video_id
    ).execute()

    if not current["items"]:
        print(f"⚠️ Video {video_id} not found, skipping")
        continue

    snippet = current["items"][0]["snippet"]
    snippet["title"] = str(new_title)  # update only the title

    request = youtube.videos().update(
        part="snippet",
        body={
            "id": video_id,
            "snippet": snippet
        }
    )
    response = request.execute()

    print(f"✅ Renamed {video_id} -> {new_title}")
