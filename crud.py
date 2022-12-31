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


def get_reddit_streams(city:str):
    
    city = city.replace("-","")

    URL: str = f"https://www.reddit.com/r/{city}/hot.json"

    #URL: str = f"https://www.reddit.com/t/{city}/hot.json" # topic need to weed out different countries tho

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
    rs = get_reddit_streams(city)
    ts = get_twitter_streams( q )
    s = rs + ts
    random.shuffle(s)
    return s


key = "AIzaSyB_Q6wpMTf6C7Ic6JiSTi88qama4ZofIjs"


def get_place_details(place_id: str):
    URL: str = "https://maps.googleapis.com/maps/api/place/details/json?"
    qps = {
        "place_id": place_id,
        "key": key
    }
    resp = httpx.get(URL, params=qps)
    results = resp.json()['result']
    return results.get('website',None)


def get_place_photo(photo_ref: str):
    if photo_ref:
        URL: str = "https://maps.googleapis.com/maps/api/place/photo"

        qps = {
            "maxwidth":400,
            "photo_reference": photo_ref,
            "key": key
        }

        resp = httpx.get(URL, params=qps)
        soup = BeautifulSoup(resp.content, features="html.parser")
        tag = soup.findAll('a', href=True)[0]
        return tag['href']


def get_places_info(
    city: str,
    kind: str,
    db,
):
    URL = f"https://maps.googleapis.com/maps/api/place/textsearch/json"

    T = CityShortData
    q = select(T).where(T.tag==city)
    row = db.exec(q).one()

    location = f"{row.lat},{row.lon}"

    print(location)
    
    qps = {
        "location": location,
        "radius": 6000,
        "key":key,
    }

    if kind=="food":
        qps["type"]="restaurant"
        qps["query"]="best restaurant"
    elif kind=="coffee":
        qps["type"]="cafe"
        qps["query"]="coffee shop"
    elif kind=="fun":
        qps["type"]="tourist_attraction"

    
    resp = httpx.get(URL, params=qps)
    out = resp.json()
    places=[]
    for place in out['results']:
        if 'photos' in place and 'point_of_interest' in place['types'] and place["user_ratings_total"]>10 and place["rating"]>4.5:
            info = {
                "name": place['name'],
                "lat": place['geometry']['location']['lat'],
                "lon": place['geometry']['location']['lng'],
                #"blurb": "This is a quick blurb about the restaurent.",
                "address": place['formatted_address'].split(",")[0],
                "img": get_place_photo( place['photos'][0]['photo_reference'] ),
                "link": get_place_details( place['place_id'] ),
                "rating": place["rating"]
            }
            places.append( info )
    return places
