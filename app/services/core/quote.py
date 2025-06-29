import requests

def get_quote() -> str:
    """
    Fetch a random motivational quote from ZenQuotes API.
    Returns formatted quote with author or error message.
    """
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        if response.status_code == 200:
            data = response.json()
            quote = data[0]["q"]
            author = data[0]["a"]
            return f'"{quote}" – {author}'
        else:
            return "Could not fetch quote (API error)."
    except Exception as e:
        return f"Could not fetch quote: {str(e)}"
