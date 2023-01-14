import re
import random
import httpx
import uuid
#from dataclasses import dataclass, asdict
from typing import Optional
from schema import StreamItem
from bs4 import BeautifulSoup
from sqlmodel import Session, select

from models import CityShortData, Place


def get_cities_short_data(db: Session):
    q = select(CityShortData)
    rows = db.exec(q).all()
    return rows


def remove_url(text):
    regex = r"(?i)\b((?:https://t.co/|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))$"
    url = re.findall(regex, text)
    if url:
        url = url[0][0]
        return text.replace(url,"")
    else:
        return text


def get_reddit_topic(city:str):
    
    city = city.replace("-","")
    
    URL: str = f"https://www.reddit.com/t/{city}/hot.json"

    resp_data = httpx.get(URL).json()
    if 'data' in resp_data:
        posts = resp_data['data']['children'][1:]

        formatted_posts = []
        for post in posts:
            content = post['data']['selftext']
            
            pd = StreamItem(
                title=post['data']['title'],
                content=post['data']['selftext'],
                link=post['data']['url'],
                source="reddit"
            )
            formatted_posts.append( pd )
        return formatted_posts
    else:
        return []


def get_reddit_sub(city:str):
    
    city = city.replace("-","")

    if city=="lisbon":
        city="lisboa"

    URL: str = f"https://www.reddit.com/r/{city}/hot.json"

    resp_data = httpx.get(URL).json()
    if 'data' in resp_data:
        posts = resp_data['data']['children'][1:]

        formatted_posts = []
        for post in posts:
            pd = StreamItem(
                title=post['data']['title'],
                content=post['data']['selftext'],
                link=post['data']['url'],
                source="reddit"
            )
            formatted_posts.append( pd )
        return formatted_posts
    else:
        return []


def parse_twitter_v1(json_resp):
    data = json_resp.get("data", None)
    if data:
        formatted_posts = []
        for tweet in data:
            if "retweeted_status" not in tweet:
                img: str = None
                full_text = tweet['full_text']
                regex = r"(?i)\b((?:https://t.co/|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))$"
                url = re.findall(regex, full_text)[0][0]
                full_text = full_text.replace(url,"")
                if "entities" in tweet:
                    if "media" in tweet['entities']:
                        img=tweet['entities']['media'][0]['media_url']
                if "extended_entities" in tweet:
                    img=tweet['extended_entities']['media'][0]['media_url']
                
                t = StreamItem(
                    title=full_text,
                    img=img,
                    link=url,
                    source="twitter"
                )
                
                formatted_posts.append( t )
        return formatted_posts


def parse_twitter_v2(json_resp) -> list:
    data = json_resp.get("data", None)
    if data:
        formatted_posts = []
        for tweet in data:

            img = tweet.get("entities")
            if img:
                img = img["urls"]["images"]["url"]
            _id = tweet["id"]

            t = StreamItem(
                        title = remove_url( tweet['text'] ),
                        img = img,
                        link = f"https://twitter.com/twitter/status/{ _id }",
                        source="twitter"
                    )
            formatted_posts.append( t )
        return formatted_posts
    return []


def get_twitter_streams(query: str):
    URL: str = "https://api.twitter.com/2/tweets/search/recent"
    
    params={
        "query":f"{query}",
        "max_results": 20
    }
    headers = {
        "Authorization":"Bearer AAAAAAAAAAAAAAAAAAAAAMoekgEAAAAABzsAvAikE00imEFiZgY2MfajbVo%3DofGZGFf6ZeC4zm3JMpKscRF3ez0Mx017JxYgtmmLF85pv04Htf"
    }
    resp = httpx.get(URL, params=params, headers=headers)

    try:
        data = resp.json()
        #print(data)
        return parse_twitter_v2( data )
    except Exception as e:
        print( repr(e) )
        return []


def get_city_streams(city, db):
    T = CityShortData
    q = select(T).where(T.tag==city)
    row = db.exec(q).one()
    q = f"{row.name} {row.country}"
    rs = get_reddit_sub(city)
    ts = get_twitter_streams( q )
    s = rs + ts
    random.shuffle(s)
    return s


def get_places_info(
    city: str,
    kind: str,
    db,
):
    q = select(Place).where(Place.city_tag==city).where(Place.kind==kind)
    return db.exec(q).all()
