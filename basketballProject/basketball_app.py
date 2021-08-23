import base64
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
#Imports are in virtual environment folder env

st.title('NBA Player Per Game Stats')

st.markdown("""
This app performs a quick analysis of NBA player per game statistics.
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950,2022))))

# Web scraping of NBA player stats
@st.cache
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header = 0)

# "MP" "FG" "FGA" "FT" "FTA" "TRB" "AST" "STL" "BLK" "TOV" "PTS"       
    df = html[0] #select 1 and only table
    raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    
    playerstats=playerstats.iloc[1:]

    playerstats.columns=['Player','Pos','Age','Tm','G','GS','MP','FG','FGA','FG%','3P','3PA','3P%','2P','2PA','2P%','eFG%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS']
    colstoround=["FG", "FGA", "FT", "FTA", "TRB", "AST", "STL", "BLK", "TOV", "PTS","G"]

    #Efficiency basketball formula
    playerstats[colstoround]=playerstats[colstoround].astype(np.float16)
    playerstats['EFF']=(playerstats['PTS']+playerstats['TRB']+playerstats['STL']+playerstats['AST']+playerstats['BLK']-playerstats['TOV']-(playerstats['FGA']-playerstats['FG'])-(playerstats['FTA']-playerstats['FT']))/playerstats['G']
    playerstats['EFF']=np.where(playerstats['G']<=30,0,playerstats['EFF'])
    return playerstats
playerstats = load_data(selected_year)

# Sidebar - Team selection
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['C','PF','SF','PG','SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# Filtering data
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]
st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.write('( '+ '*'+ ' ) Player is in the Hall of Fame')
st.write("Player must have played at least 30 games for EFF to be calculated.")
st.write("BLK and STL started to be recorded in 1973-1974 Season")
st.write("3p statistics started to be recorded in 1979-80")
st.dataframe(df_selected_team)
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')

    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot()

# Scatterplot
if st.button('Scatterplot'):
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')
    st.header('Scatterplot')
    st.write("Compares the Amount of Assists to Turnover, Demonstrating that with more assists comes with more turnovers for most players")

    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.scatterplot(x='AST', y='TOV', data=df)
    st.pyplot()
# Boxplot
if st.button('Boxplot'):
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')
    st.header('Boxplot')
    st.write("Boxplot of players position and Points scored, showing which position on average scores the most points. Indicating to teams where plays should be focused on for the most points in a possession")
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.boxplot(x='Pos', y='PTS', data=df)
    st.pyplot()

#Line plot
if st.button('Line Plot'):
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')
    st.header('Line Plot')
    st.write("Line Plot of Player's Age vs their EFF. Finding the majority of players prime in the NBA. Only players who have played at least 30 games have their EFF calculated")
    ageEFF=df[(df["G"]>=30)]
    
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.lineplot(x='Age', y='EFF', data=ageEFF)
    st.pyplot()

