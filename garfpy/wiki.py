import wikipedia

async def wikisum(search_term):
    try:
        summary = wikipedia.summary(search_term)
        return summary
    
    # except wikipedia.exceptions.DisambiguationError as e:
    except Exception as e:
        return e