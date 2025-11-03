#!/usr/bin/env python

import requests
import os
from dotenv import load_dotenv, find_dotenv

print(
    requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={
            "X-Subscription-Token": os.environ.get("BRAVE_SEARCH_API_KEY"),
        },
        params={
            "q": "greek restaurants in san francisco",
            "count": 20,
            "country": "us",
            "search_lang": "en",
        },
    ).json()
)