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

# Refresh or re-authenticate if invalid
if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret_749870873148-1tcaath33kiso9gpligdisolqj3ur2pu.apps.googleusercontent.com.json",  # replace with your file
        SCOPES
    )
    creds = flow.run_local_server(port=0)
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

# Step 2: Build YouTube service
youtube = build("youtube", "v3", credentials=creds)

# Step 3: Load Excel (no header row)
df = pd.read_excel("videos_with_ids.xlsx", header=None)

# Set the starting index (manually adjust if resuming later)
START_INDEX = 10  

# Step 4: Iterate over rows, starting from START_INDEX
for idx, row in df.iloc[START_INDEX:].iterrows():
    old_title = str(row[0]) if pd.notna(row[0]) else ""   # col 0
    new_title = str(row[1]) if pd.notna(row[1]) else ""   # col 1
    video_id  = str(row[2]) if pd.notna(row[2]) else ""   # col 2

    if not video_id:
        print(f"⚠️ Row {idx} has no video_id, skipping")
        continue

    print(f"{idx}: {video_id}\t{old_title} -> {new_title}")

    # Get current snippet
    current = youtube.videos().list(
        part="snippet",
        id=video_id
    ).execute()

    if not current.get("items"):
        print(f"⚠️ Video {video_id} not found, skipping")
        continue

    current_snippet = current["items"][0]["snippet"]

    # Build updated snippet
    snippet = {
        "title": new_title[:100],  # enforce 100-char max
        "description": current_snippet.get("description", ""),
        "categoryId": current_snippet.get("categoryId", "22"),
    }

    # Preserve tags if they exist
    if "tags" in current_snippet:
        snippet["tags"] = current_snippet["tags"]

    # Update video
    request = youtube.videos().update(
        part="snippet",
        body={
            "id": video_id,
            "snippet": snippet
        }
    )
    response = request.execute()

    print(f"✅ Renamed {video_id} -> {new_title}")
