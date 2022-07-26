# -*- coding: utf-8 -*-




import pandas as pd


# from google.colab import drive
# drive.mount('/content/drive')


dataGames = pd.read_csv('./metacritics/metacrawl_gameinfo_final.csv')

dataGames.head()



dataGames=dataGames.drop(columns=['Unnamed: 0'])

dataGames.head()

dataGames_pc=dataGames[dataGames['platform']=='pc']
dataGames_pc.head()

dataGames_pc=dataGames_pc.drop(columns=['metascore','metareviews'])
dataGames_pc.head()

data_pc=dataGames_pc.drop(columns=['platform','userscore','userreviews','players','age'])
data_pc.head()

import re

data_pc['title'][0]

from tqdm.notebook import tqdm

data_pc['title'] = data_pc['title'].str.replace("[^A-Za-z0-9]+","")

data_pc['title'] = data_pc['title'].str.lower()

data_pc.head()



data_pc.info()

"""# 1. title 을 기준으로 steam data와 merge 한 후 title 전처리(공백 없애고 소문자로)"""

steam_df=pd.read_csv('./steam/steam_info.csv')
steam_df.head()

steam_df.columns

steam_df=steam_df.drop(columns=['Unnamed: 0','franchise','image_link','grade','language_interface','language_fullaudio','language_subtitles'])
steam_df.head()

steam_df['recent_reviews'].value_counts()

steam_df2=steam_df.drop(columns=['appid','release_date','recent_reviews','recent_reviews_ratio','recent_reviews_voted_users','all_reviews','all_reviews_ratio','all_reviews_voted_users'])
steam_df2.head()

steam_df2['title'] = steam_df2['title'].str.replace("[^A-Za-z0-9]+","")
steam_df2['title'] = steam_df2['title'].str.lower()

steam_df2.head()

steam_df2['title'].value_counts()

steam_df2.info()

"""스팀과 메타에 모두 있는 게임으로 merge"""

game_pc=pd.merge(steam_df2,data_pc,on='title',how='inner')
game_pc.head()

game_pc.info()

game_pc=game_pc.drop_duplicates("title")
game_pc.head()

game_pc=game_pc.reset_index()

game_pc[game_pc['title'].isna()==True].index

game_pc=game_pc.drop(21046, axis=0)

game_pc.head()

game_pc.info()

game_pc2=game_pc.drop(columns=['index','releasedate'])
game_pc2.head()

game_pc3=game_pc2.drop(columns=['summary','developer_x','genre_y'])
game_pc3.head()

game_pc3.info()

game_pc3 = game_pc3.rename(
    columns={
        "genre_x": "genre",
          
    }
)

game_pc4=game_pc3.dropna(axis=0)
game_pc4=game_pc4.reset_index()
game_pc4=game_pc4.drop(columns='index')

game_pc4.head()

game_pc4.info()

"""# 2. 여러가지 조합의 정보를 새로운 열에 추가함
 - ex) 장르 + 태그 + 개발사
"""



game_pc4

# 새로운 컬럼 추가
game_pc4['genre_tag']=game_pc4['genre']+','+game_pc4['tag']
game_pc4["genre_tag_developer_publisher"] = game_pc4['genre']+','+ game_pc4['tag'] + ","+ game_pc4['developer_y']+ "," + game_pc4['publisher']
game_pc4["tag_developer_info"] = game_pc4['tag']+ "," + game_pc4['developer_y']+ "," + game_pc4['info']
game_pc4["tag_about_game"] = game_pc4['tag'] + ","+ game_pc4['about_this_game']
game_pc4["tag_developer_publisher_info"] = game_pc4['tag']+ "," + game_pc4['developer_y']+ "," + game_pc4['publisher']+ "," + game_pc4['info']
game_pc4["tag_developer_publisher_info_about_game"] = game_pc4['tag']+ "," + game_pc4['developer_y']+ "," + game_pc4['publisher']+ "," + game_pc4['info']+ "," + game_pc4['about_this_game']

game_pc4.head()

"""# 3. 벡터화 후 코사인 유사도 계산(bag of words/countvector/tf - idf)"""

import string
import nltk
import re

nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

game_pc5=game_pc4.copy()
game_pc5.head()



vectorizer=CountVectorizer(min_df=10, max_df=0.7,stop_words='english')
dtm2 = vectorizer.fit_transform(game_pc5['genre_tag'])
dtm2.head()

tf2 = pd.DataFrame(dtm2.toarray(), columns = vectorizer.get_feature_names())
tf2.head()

df2 = tf2.astype(bool).sum(axis = 0)
df2.head()

df2.sort_values(ascending=False).head(20)

similarity_rate = cosine_similarity(tf2, tf2)

import numpy as np

np.fill_diagonal(similarity_rate,0)
similarity_rate

similarity_rate2=pd.DataFrame(data=similarity_rate,index=game_pc5['title'],columns=game_pc5['title'])
similarity_rate2

def recommend_steam_game(title):
  return similarity_rate2[title]

rec=recommend_steam_game(['goosegooseduck']).sort_values(by=['goosegooseduck'],ascending=False)
rec.head(20)

rec=recommend_steam_game(['pummelparty','tabletopsimulator','goosegooseduck']).sort_values(by=['pummelparty','tabletopsimulator','goosegooseduck'],ascending=False)
rec.head(20)

rec['mean']=rec.mean(axis=1)
rec.sort_values(by='mean',ascending=False).head(20)

rec2=recommend_steam_game(['apexlegends','dontstarvetogether','stardewvalley']).sort_values(by=['apexlegends','dontstarvetogether','stardewvalley'],ascending=False)
rec2.head(20)

rec2['mean']=rec2.mean(axis=1)
rec2.sort_values(by='mean',ascending=False).head(20)

game_pc5['tag']
