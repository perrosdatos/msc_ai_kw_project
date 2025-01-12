import requests

url = 'https://query.wikidata.org/sparql'

def get_artist_by_name(artist_name, timeout = 60):
    artist_name = artist_name.lower()
    query = f'''
        SELECT  ?entity ?entityLabel  WHERE {{
            # Filter for humans with a relevant occupation
            ?entity wdt:P31 wd:Q5;         # Instance of human
                    wdt:P106 ?occupation; # Occupation property
                    rdfs:label ?entityLabel .
            
            # Match specific occupations or their subclasses
            ?occupation wdt:P279* ?baseOccupation .
            VALUES ?baseOccupation {{
                wd:Q639669   # Musician
                wd:Q177220   # Singer
                wd:Q753110   # Songwriter
                wd:Q36834    # Composer
                wd:Q488205   # Singer-songwriter
                wd:Q183945   # Record producer
                wd:Q55960555 # Recording artist
                wd:Q2405480  # Voice actor
                wd:Q2490358  # Choreographer
            }}
        
        
            
            # Apply name filter early
            FILTER(LANG(?entityLabel) = "en").  # Filter for English labels
            FILTER(CONTAINS(LCASE(?entityLabel), "{artist_name}")).
        }}
        LIMIT 1
    '''
    try:
        r = requests.get(url, params = {'format': 'json', 'query': query}, timeout = timeout)
        data = r.json()
        if "results" in data:
            if "bindings" in data["results"]:
                if len(data["results"]["bindings"]) > 0:
                    return {"entity": data["results"]["bindings"][0]["entity"]["value"], "entityLabel": data["results"]["bindings"][0]["entityLabel"]["value"]}
    
    except Exception as e:
        print(str(e))
    return None

def get_influenced_by(artist_url, timeout = 60):
    
    artist_id = artist_url.split("/")[-1]  # Extract the ID from the URL
    query = f'''
        SELECT DISTINCT ?influencedBy ?influencedByLabel ?type WHERE {{
            # Branch 1: Music groups
            {{
                wd:{artist_id} wdt:P737 ?influencedBy .
                ?influencedBy wdt:P31 wd:Q215380 .  # Music group
                BIND("Music Group" AS ?type)  # Add type as 'Music Group'
            }}
            UNION
            # Branch 2: Humans with specific occupations
            {{
                wd:{artist_id} wdt:P737 ?influencedBy .
                ?influencedBy wdt:P31 wd:Q5 ;  # Human
                              wdt:P106 ?occupation .
                VALUES ?occupation {{
                    wd:Q639669   # Musician
                    wd:Q177220   # Singer
                    wd:Q753110   # Songwriter
                    wd:Q36834    # Composer
                    wd:Q488205   # Singer-songwriter
                    wd:Q183945   # Record producer
                    wd:Q55960555 # Recording artist
                    wd:Q2405480  # Voice actor
                    wd:Q2490358  # Choreographer
                }}
                BIND("Person" AS ?type)  # Add type as 'Person'
            }}
            
            # Retrieve labels for the influenced entities
            ?influencedBy rdfs:label ?influencedByLabel .
            FILTER(LANG(?influencedByLabel) = "en").  # English labels only
        }}
        LIMIT 20
    '''
    try:
        r = requests.get(url, params = {'format': 'json', 'query': query}, timeout = timeout)
        data = r.json()
        results = []
        if "results" in data:
            if "bindings" in data["results"]:
                for item in data["results"]["bindings"]:
                    results.append(
                            {"influenced_by": item["influencedBy"]["value"],
                            "influenced_by_label": item["influencedByLabel"]["value"],
                            "type": item["type"]["value"]}
                                  )
        return results
    except Exception as e:
        print(str(e))
    return None

def get_influenced_by(artist_url, timeout=60):
    """
    Fetches entities that influenced a given artist, filtering only for humans or music groups.

    Args:
        artist_url (str): Wikidata URL of the artist.
        timeout (int): Timeout for the request in seconds.

    Returns:
        list: A list of dictionaries containing influenced entities, their labels, and types.
    """
    artist_id = artist_url.split("/")[-1]  # Extract the ID from the URL
    query = f'''
        SELECT DISTINCT ?influencedBy ?type WHERE {{
            wd:{artist_id} wdt:P737 ?influencedBy .
            ?influencedBy wdt:P31 ?type
        }}
        LIMIT 20
    '''
    try:
        response = requests.get(
            "https://query.wikidata.org/sparql",
            params={"format": "json", "query": query},
            timeout=timeout,
        )
        response.raise_for_status()
        return [
            {
                "influenced_by": item["influencedBy"]["value"],
                "type": item["type"]["value"],
            }
            for item in response.json().get("results", {}).get("bindings", [])
        ]
    except Exception as e:
        print(f"Error: {e}")
        return None 

def get_label_by_entity_url(entity_url, timeout=10):
    query = f'''
        SELECT ?label WHERE {{
            <{entity_url}> rdfs:label ?label .
            FILTER(LANG(?label) = "en").
        }}
    '''
    url = "https://query.wikidata.org/sparql"
    try:
        r = requests.get(url, params={"format": "json", "query": query}, timeout=timeout)
        r.raise_for_status()
        results = r.json().get("results", {}).get("bindings", [])
        if results:
            
            return {"entity": entity_url, "label": results[0]["label"]["value"]}
    except Exception as e:
        print(f"Error: {e}")
    return None

def get_music_band_by_name(band_name, timeout=60):
    band_name = band_name.lower()
    query = f'''
        SELECT DISTINCT ?entity ?entityLabel WHERE {{
            # Filter for entities that are instances or subclasses of "music band"
            ?entity wdt:P31/wdt:P279* wd:Q215380;  # Instance of or subclass of music band
                    rdfs:label ?entityLabel .
            
            # Apply name filter
            FILTER(LANG(?entityLabel) = "en").  # Filter for English labels
            FILTER(CONTAINS(LCASE(?entityLabel), "{band_name}")).
        }}
        LIMIT 1
    '''
    url = "https://query.wikidata.org/sparql"
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, timeout=timeout)
        r.raise_for_status()  # Raise HTTP errors if any
        data = r.json()
        if "results" in data and "bindings" in data["results"] and len(data["results"]["bindings"]) > 0:
            return {
                "entity": data["results"]["bindings"][0]["entity"]["value"],
                "entityLabel": data["results"]["bindings"][0]["entityLabel"]["value"]
            }
    except Exception as e:
        print(f"Error: {e}")
    return None

def get_songs_by_artist_url(artist_url, timeout = 60):
    
    query = f'''
    SELECT DISTINCT ?song ?songLabel WHERE {{
    # Retrieve songs where the artist is a composer
    {{
        ?song wdt:P31 wd:Q7366;  # Instance of a musical work (song)
              wdt:P86 wd:{artist_url.split("/")[-1]} .  # Composer is Michael Jackson (Q2831)
    }}
    UNION
    {{
        ?song wdt:P31 wd:Q7366;  # Instance of a musical work (song)
              wdt:P175 wd:{artist_url.split("/")[-1]} .  # Performer is Michael Jackson
    }}
    UNION
    {{
        ?song wdt:P31 wd:Q7366;  # Instance of a musical work (song)
              wdt:P457 wd:{artist_url.split("/")[-1]} .  # Lyricist is Michael Jackson
    }}

    # Retrieve English labels for the songs
    ?song rdfs:label ?songLabel .
    FILTER(LANG(?songLabel) = "en").
    }}
    LIMIT 50
    '''
    try:
        r = requests.get(url, params = {'format': 'json', 'query': query}, timeout = timeout)
        data = r.json()
        results = []
        if "results" in data:
            if "bindings" in data["results"]:
                for item in data["results"]["bindings"]:
                    results.append(
                            {"entity": item["song"]["value"],
                            "label": item["songLabel"]["value"]}
                                  )
        return results
    except Exception as e:
        print(str(e))
    return None

import random
import numpy as np
def get_recommendations_based_on_influencedBy(artist_str, timeout=30, max_influences = 2):
    results = []
    print("get entities")
    item_artist = None
    print("searching a band")
    item_band = get_music_band_by_name(artist_str, timeout)
    
    if item_band is None:
        print("searching by human")
        item_artist = get_artist_by_name(artist_str, timeout)
    else:
        item_artist = item_band
    print("Getting influencedBy entities...")
    print(item_artist)
    if item_artist is None:
        print("No Artist found")
        return []
    getting_items = get_influenced_by(item_artist["entity"], timeout)
    print(getting_items[0])
    influences = random.choices(getting_items, k=min(max_influences, len(getting_items)))
    
    print(f"Choosing first {max_influences} artists...")
    for influence in influences:
        dict_item = get_label_by_entity_url(influence["influenced_by"])
        print(f"Processing {dict_item["label"]}...")
        songs = get_songs_by_artist_url(influence["influenced_by"], timeout)
        results.append({"artist":influence["influenced_by"], "type":influence["type"], "label":dict_item["label"], "songs":songs})
        
    return results


def get_randomly_weighted(items, k):
    artists = list(items.keys())
    weights = list(items.values())
    selected = {}

    for _ in range(k):
        total_weight = sum(weights)
        probabilities = [w / total_weight for w in weights]

        chosen_index = random.choices(range(len(artists)), probabilities, k=1)[0]
        selected[artists[chosen_index]] =  weights[chosen_index]

        artists.pop(chosen_index)
        weights.pop(chosen_index)

    return selected
    
def get_recommendarions_based_on_influencedBy_likes_dislikes(likes = [], dislikes = [], max_influences=4, timeout=30, debug=False):
    influencedByCounters  = {}
    results = []
    for artist in likes:
        if debug:
            print(f"Processing liked artist: {artist} ") 
        print("searching a band")
        
        item_band = get_music_band_by_name(artist, timeout)
        
        if item_band is None:
            if debug:
                print("searching by human")
            item_artist = get_artist_by_name(artist, timeout)
        else:
            item_artist = item_band
        if item_artist is None:
            continue
                
        if debug:
            print("Getting influencedBy entities...")
            print(item_artist)
        
        getting_items = get_influenced_by(item_artist["entity"], timeout)
        
        for item in getting_items:
            if item["influenced_by"] is not None:
                if item["influenced_by"] not in influencedByCounters:
                    influencedByCounters[item["influenced_by"]] = 1
                else:
                    influencedByCounters[item["influenced_by"]] += 1
    for artist in dislikes:
        if debug:
            print(f"Processing disliked artist: {artist} ")   
            print("searching a band")
        
        item_band = get_music_band_by_name(artist, timeout)
        
        if item_band is None:
            if debug:
                print("searching by human")
            item_artist = get_artist_by_name(artist, timeout)
        else:
            item_artist = item_band
            
        if item_artist is None:
            continue
        if debug:
            print("Getting influencedBy entities...")
            print(item_artist)
        
        getting_items = get_influenced_by(item_artist["entity"], timeout)
        
        
        for item in getting_items:
            if item["influenced_by"] is not None:
                if item["influenced_by"] in influencedByCounters:
                    influencedByCounters[item["influenced_by"]] -= 1
                    
                    if debug:
                        print(f'{item["influenced_by"]} was penalized')
                    if influencedByCounters[item["influenced_by"]] == 0:
                        del influencedByCounters[item["influenced_by"]]
    if len(influencedByCounters) == 0:
        return None
    
    influenced_by_dict = get_randomly_weighted(influencedByCounters,max_influences)   
    
    for influence, count in influenced_by_dict.items():
        if debug:
            print(f"Processing {influence}...")
        dict_item = get_label_by_entity_url(influence)
        songs = get_songs_by_artist_url(influence)
        results.append({"artist":influence, "label":dict_item["label"], "songs":songs, "weight":count})
    return sorted(results, key=lambda item: item["weight"], reverse=True)

"""

likes = ["beatles", "Bruno Mars", "Michael Jackson", "Britney Spears"]
dislikes = ["Sam Smith"]
songs = get_recommendarions_based_on_influencedBy_likes_dislikes(likes, dislikes, max_influences=4, timeout=15, debug=True)
print(songs)
"""