from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import time
import matplotlib.pyplot as plt
import seaborn as sns
import re
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


# Launch browser and load page
url = 'https://www.imdb.com/chart/top/?ref_=nv_mv_250'
driver = webdriver.Chrome()
driver.get(url)
time.sleep(5)
html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, 'html.parser')

# Locate all movie containers
movies = soup.select('li.ipc-metadata-list-summary-item')
age_rating_keywords = ['G', 'PG', 'PG-13', 'R', 'NC-17', 'Approved', 'Not Rated', 'Unrated', 'TV-MA', 'TV-PG']
movie_list = []

for movie in movies:
    title_tag = movie.select_one('h3')
    title = title_tag.text.strip() if title_tag else None

    rating_tag = movie.select_one('span.ipc-rating-star--rating')
    fan_rating = rating_tag.text.strip() if rating_tag else None

    metadata_tags = movie.select('span.cli-title-metadata-item')

    year = None
    duration = None
    age_rating = None

    for meta in metadata_tags:
        text = meta.text.strip()
        if text.isdigit() and len(text) == 4:
            year = text
        elif 'h' in text or 'm' in text:
            duration = text
        elif text in age_rating_keywords:
            age_rating = text

    movie_list.append({
        'Title': title,
        'Fan Rating': fan_rating,
        'Release Year': year,
        'Duration': duration,
        'Age Rating': age_rating
    })

# Create dataframe
df = pd.DataFrame(movie_list)
df.to_csv('movies.csv', index=False)

print(df)

#cleaning
newDf = df.dropna()
newDf = newDf.drop_duplicates()


#regex section
#1: find all movies released in a certain year

pattern = rf"\b{1984}\b"  # word boundary to match exactly 2015

# Apply regex across the column
# Change 'title' to whatever column actually holds the year
filtered_df = df[df['Release Year'].str.contains(pattern, regex=True)]
print("Movies releaseds in 1984:")
print(filtered_df)


#return pg-13 movies
pattern = r"\bPG-13\b"  # exact match for PG-13

# Again, replace 'rating' with the correct column name
pg13_movies = df[df['Age Rating'].str.contains(pattern, regex=True, na=False)]
print("PG-13 MOVIES:")
print(pg13_movies)

newDf.to_csv('moviesCleaned.csv', index=False)

#changes from string to numerical
newDf['Fan Rating'] = pd.to_numeric(newDf['Fan Rating'], errors='coerce')
newDf['Release Year'] = pd.to_numeric(newDf['Release Year'], errors='coerce')
numeric_df = newDf.select_dtypes(include='number') #only numeric values

#Data Analysis
print(newDf.describe())
print(newDf['Fan Rating'].value_counts())
print(newDf['Fan Rating'].mean())
print(newDf['Fan Rating'].median())
print(newDf['Fan Rating'].mode())
print(newDf['Fan Rating'].var())
print(newDf['Fan Rating'].std())
print(newDf.isnull().sum())

#grouping
#average Fan Rating per Release Year
yearly_trend = newDf.groupby('Release Year')['Fan Rating'].mean()
print("\nAverage Fan Rating per Year:")
print(yearly_trend)
#average Fan Rating per Age Rating
age_rating_trend = newDf.groupby('Age Rating')['Fan Rating'].mean()
print("\nAverage Fan Rating per Age Rating:")
print(age_rating_trend)
#Fan Rating vs Release Year
print("\nCorrelation between Release Year and Fan Rating:")
print(newDf[['Release Year', 'Fan Rating']].corr())

#visulization
#Average Fan Rating over the years
plt.figure(figsize=(10,6))
yearly_trend.plot(kind='line', marker='o', color='green')
plt.title('Average Fan Rating Over the Years')
plt.xlabel('Release Year')
plt.ylabel('Average Fan Rating')
plt.grid(True)
plt.show()

#Average Fan Rating per Age Rating
plt.figure(figsize=(8,5))
age_rating_trend.plot(kind='bar', color='skyblue')
plt.title('Average Fan Rating by Age Rating')
plt.xlabel('Age Rating')
plt.ylabel('Average Fan Rating')
plt.xticks(rotation=45)
plt.show()

#Correlation between numeric features
plt.figure(figsize=(8,6))
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation between Numerical Features')
plt.show()

#Distribution of Fan Ratings
plt.figure(figsize=(8,5))
newDf['Fan Rating'].hist(bins=20, color='orange')
plt.title('Distribution of Fan Ratings')
plt.xlabel('Fan Rating')
plt.ylabel('Number of Movies')
plt.show()

#Fan Rating distribution by Age Rating
plt.figure(figsize=(10,6))
sns.boxplot(data=newDf, x='Age Rating', y='Fan Rating', palette='Set3')
plt.title('Fan Rating distribution by Age Rating')
plt.xlabel('Age Rating')
plt.ylabel('Fan Rating')
plt.xticks(rotation=45)
plt.show()







uri = "mongodb+srv://ahmedtheeditor:eZWM3zA9bqiDd6bo@toolscluster.mom07ap.mongodb.net/?retryWrites=true&w=majority&appName=toolsCluster"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# Insert data
movie_records = newDf.to_dict(orient='records')
db = client['imdb_data']
collection = db['top_movies']
collection.insert_many(movie_records)
print("Data inserted successfully!")
