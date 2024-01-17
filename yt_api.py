from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import nltk
import pandas as pd
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('names')
from nltk.tokenize import word_tokenize

from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
nltk.download('punkt')
load_dotenv()


youtube = build('youtube', 'v3', developerKey= os.environ.get("YOUTUBE_API_KEY"))


def get_video_comments_data(video_id: str) -> dict[str, list]:
   
    data = {'dn': [], 'text': [], 'like_counts': [],  'published_at': [], 'neg': [],'pos': [], 'compound': []}
    
    def get_comment_threads(page_token: str):
        response = youtube.commentThreads().list(
        part="id, snippet",
        videoId= video_id,
        maxResults=100,
        pageToken = page_token

        ).execute()
        for comment_thread in response['items']:
            
            comment = comment_thread["snippet"]["topLevelComment"]
            text_original = (comment['snippet']['textOriginal'])
            
            scores = SentimentIntensityAnalyzer().polarity_scores(get_filtered_text(text_original))
            if scores['neg'] + scores['pos'] + scores['compound'] != 0:
                data['neg'].append(scores['neg'])
                data['pos'].append(scores['pos'])
                data['compound'].append(scores['compound'])
            
                data['dn'].append(comment['snippet']['authorDisplayName'])
                data['text'].append(text_original)
                data['like_counts'].append(comment['snippet']['likeCount'])
                data['published_at'].append(pd.to_datetime(comment['snippet']['publishedAt']))
        return response
    
    ## start from the 1st comment threads. If there is a next page token continue going
    match = get_comment_threads('')
    next_page_token = match['nextPageToken'] or ''
    pages = 0
    
    try:
        while next_page_token and pages < 2:
            match = get_comment_threads(next_page_token)
            next_page_token = match["nextPageToken"]
            pages = pages + 1
            
        return data
    except:
        return data
    
    
def queryVideo(query):
    youtube = build('youtube', 'v3', developerKey= os.environ.get("YOUTUBE_API_KEY"))
    response = youtube.search().list(
        part="id,snipper",
        q = query,
        
    ).execute()
    
def get_video_title_data(video_id: str) -> dict[str, str]:
      response = youtube.videos().list(
        part="id, snippet",
        id= video_id,
        maxResults=1,
        ).execute()
      
      
      return {'title': response['items'][0]['snippet']}
    
    

def get_filtered_text(text) -> str:
    return ' '.join(get_filtered_text_list(text))
   
   
def get_filtered_text_list(text) -> list[str]:
    stop_words = set(stopwords.words('english'))
    filtered_text_list = [
        word for word in word_tokenize(text) if word.casefold() not in stop_words and word.isalpha() and word not in nltk.corpus.names.words()]
    return filtered_text_list



