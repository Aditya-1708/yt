import pandas as pd

# Read the Excel file
df = pd.read_excel('videos_with_new_titles.xlsx')

# Remove rows where new_title is empty or contains only whitespace
df_cleaned = df[df['new_title'].notna() & (df['new_title'].str.strip() != '')]

# Save the cleaned data
df_cleaned.to_excel('cleaned_data.xlsx', index=False)

print(f'Removed {len(df) - len(df_cleaned)} rows with empty new_title column')
print(f'Remaining rows: {len(df_cleaned)}')
