import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.title("IMDb Top 250 Movie Analysis")

# Load pre-scraped CSV
df = pd.read_csv("movies.csv")

# Clean and preprocess
df = df.dropna().drop_duplicates()
df['Fan Rating'] = pd.to_numeric(df['Fan Rating'], errors='coerce')
df['Release Year'] = pd.to_numeric(df['Release Year'], errors='coerce')

# Analysis
st.subheader("Summary Statistics")
st.write(df.describe())

st.subheader("Average Fan Rating Over the Years")
yearly_trend = df.groupby('Release Year')['Fan Rating'].mean()
st.line_chart(yearly_trend)

st.subheader("Average Fan Rating by Age Rating")
age_rating_trend = df.groupby('Age Rating')['Fan Rating'].mean()
st.bar_chart(age_rating_trend)

st.subheader("Correlation Matrix")
st.write(sns.heatmap(df[['Fan Rating', 'Release Year']].corr(), annot=True, cmap='coolwarm').get_figure())