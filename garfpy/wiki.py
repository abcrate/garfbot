import wikipedia
from garfpy import generate_chat

async def wikisum(search_term):
    try:
        summary = wikipedia.summary(search_term)
        garfsum = generate_chat(f"Please summarize in your own words: {summary}")
        
        return garfsum
    
    except Exception as e:
        return e