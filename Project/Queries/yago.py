import SPARQLWrapper
import random
import numpy as np

def get_entity_for_musician(artist):
    # YAGO SPARQL endpoint
    endpoint_url = "https://yago-knowledge.org/sparql/query"

    # Randomly select an artist from the list
    artist = artist.lower()

    # SPARQL query template
    query_template = f"""
    PREFIX yago: <http://yago-knowledge.org/resource/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>

    SELECT DISTINCT ?entity ?type ?influencedBy WHERE {{
      {{
        ?entity a ?type ;
                rdfs:label ?label .
        FILTER(CONTAINS(LCASE(STR(?label)), \"{artist}\")).
        ?type rdfs:subClassOf* schema:MusicGroup .
      }}
      UNION
      {{
        ?entity a yago:Musician ;
                rdfs:label ?label .
        FILTER(CONTAINS(LCASE(STR(?label)), \"{artist}\")).
      }}
      UNION      
      {{
        ?entity a ?type ;
                rdfs:label ?label .
        FILTER(CONTAINS(LCASE(STR(?label)), \"{artist}\")).
        ?type rdfs:subClassOf* yago:Musician .
      }}
      OPTIONAL {{
        ?entity schema:influencedBy ?influencedBy .
      }}
    }} LIMIT 10
    """

    # Setup SPARQL
    sparql = SPARQLWrapper.SPARQLWrapper(endpoint_url)
    sparql.setQuery(query_template)
    sparql.setReturnFormat("json")

    try:
        # Execute the query
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]
        results = []
        for binding in  bindings:
            entity = binding["entity"]["value"]
            #label = binding.get("label", {}).get("value", "Unknown Label")
            type_ = binding.get("type", {}).get("value", "Unknown Type")
            influenced_by = binding.get("influencedBy", {}).get("value", "None")

            results.append( {
                "artist": artist,
                "entity": entity,
               # "label": label,
                "type": type_,
                "influenced_by": influenced_by
            })
        return results

    except Exception as e:
        return None
    
def get_songs_by_artist_url(artist_url):
    # YAGO SPARQL endpoint
    endpoint_url = "https://yago-knowledge.org/sparql/query"

    # SPARQL query template
    query_template = f"""
    PREFIX schema: <http://schema.org/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?entity (SAMPLE(?label) AS ?label) ?type WHERE {{
      ?entity a ?type ;
              schema:musicBy <{artist_url}> ;
              rdfs:label ?label .
      ?type rdfs:subClassOf* schema:MusicComposition .
      FILTER(LANG(?label) = "en")
    }} GROUP BY ?entity ?type LIMIT 50
    """

    # Setup SPARQL
    sparql = SPARQLWrapper.SPARQLWrapper(endpoint_url)
    sparql.setQuery(query_template)
    sparql.setReturnFormat("json")

    try:
        # Execute the query
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]

        songs = []
        for binding in bindings:
            entity = binding.get("entity", {}).get("value", "Unknown Entity")
            label = binding.get("label", {}).get("value", "Unknown Label")
            type_ = binding.get("type", {}).get("value", "Unknown Type")
            songs.append({"entity": entity, "label": label, "type": type_})

        return songs

    except Exception as e:
        print(str(e))
        return None


def get_label_by_entity_url(entity_url):
    # YAGO SPARQL endpoint
    endpoint_url = "https://yago-knowledge.org/sparql/query"

    # SPARQL query template
    query_template = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?label WHERE {{
      <{entity_url}> rdfs:label ?label .
      
      FILTER(LANG(?label) = "en")
    }} LIMIT 1
    """

    # Setup SPARQL
    sparql = SPARQLWrapper.SPARQLWrapper(endpoint_url)
    sparql.setQuery(query_template)
    sparql.setReturnFormat("json")

    try:
        # Execute the query
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]

        if bindings:
            sampled_label = bindings[0].get("label", {}).get("value", None)
            return {"entity": entity_url, "label": sampled_label}
        else:
            return {"entity": entity_url, "label": "No label found."}

    except Exception as e:
        return {"error": str(e)}

def get_recommendations_based_on_influencedBy(artist_str, max_influences = 2):
    results = []
    print("Getting influencedBy entities...")
    getting_items = get_entity_for_musician(artist_str)
    if getting_items == []:
        print("No entity for musician")
        return results
    print(getting_items[0])
    influences = np.unique(list(map(lambda item: item["influenced_by"], getting_items))).tolist()
    influences = random.choices(influences, k=min(max_influences, len(influences)))
    
    print(f"Choosing first {max_influences} artists...")
    for influence in influences:
        print(f"Processing {influence}...")
        dict_item = get_label_by_entity_url(influence)
        songs = get_songs_by_artist_url(influence)
        results.append({"artist":influence, "label":dict_item["label"], "songs":songs})
        
    return results

#kendrick = get_entity_for_musician("Kendrick")
#print("kendrick")
#kendrick_songs = get_songs_by_artist_url(kendrick[0]["entity"])
#print("kendrick_songs")
influencied_by_songs = get_recommendations_based_on_influencedBy("Xutos e Pontapes")
print(influencied_by_songs)