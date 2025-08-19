import pandas as pd

# Load the first file (title and video_id)
df_videos = pd.read_excel("youtube_videos.xlsx")  # columns: title, video_id

# Load the second file (no headers, just columns A and B)
df_titles = pd.read_excel("P4U - Nagaraj sir.xlsx", header=None, names=["A", "B"])

# Remove duplicates in df_titles (keep first)
df_titles = df_titles.drop_duplicates(subset="A")

# Merge on title = A
df_merged = pd.merge(df_videos, df_titles, left_on="title", right_on="A", how="left")

# Rename the new column B to 'new_title' and drop column A
df_merged = df_merged.drop(columns=["A"]).rename(columns={"B": "new_title"})

# Save to Excel
df_merged.to_excel("videos_with_new_titles.xlsx", index=False)

print("Merged Excel created without duplicates: videos_with_new_titles.xlsx")
