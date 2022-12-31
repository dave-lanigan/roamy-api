import httpx 

API = "http://127.0.0.1:8000"

def jimbo():
    cities = httpx.get(f"{API}/cities/quick-data?kind=l").json()
    for city in cities:
        tag = city['tag']
        out = httpx.get(f"{API}/stream/{tag}")
        try:
            out.json()
        except Exception as e:
            print(tag)
            print( repr(e) )


if __name__=="__main__":
    jimbo()

