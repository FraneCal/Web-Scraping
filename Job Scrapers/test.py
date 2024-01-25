import pandas as pd

# List of filenames
file_names = [
    'job_data_cloud_engineer.xlsx',
    'job_data_devops engineer.xlsx',
    'job_data_site reliability engineer.xlsx',
    'job_data_devops consultant.xlsx'
]

# List to store dataframes
dfs = []

# Read each file and extract relevant columns
for file_name in file_names:
    df = pd.read_excel(file_name, usecols=['Company Name', 'Date of Job Posting', 'Job Title', 'Country'])
    dfs.append(df)

# Concatenate dataframes
final_df = pd.concat(dfs, ignore_index=True)

# Drop duplicate rows based on specified columns
final_df.drop_duplicates(subset=['Company Name', 'Date of Job Posting', 'Job Title', 'Country'], keep='first', inplace=True)

# Save the clean data to an Excel sheet
final_df.to_excel('es_indeed_jobs.xlsx', index=False)
