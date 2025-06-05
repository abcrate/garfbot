import wikipedia
from garfpy import GarfAI

async def wikisum(search_term):
    try:
        summary = wikipedia.summary(search_term)
        garfsum = await GarfAI.generate_chat(f"Please summarize in your own words: {summary}")
        
        return garfsum
    
    except Exception as e:
        return e