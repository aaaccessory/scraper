import requests
import json
from utils import get_text_by_max_length
COPYMATICAPI = "0c029afb5a52b9cc15efdb3b4"


class SentenceRewriter:
    def __init__(self):
        print("Sentence Rewriter")

    @staticmethod
    def rewrite(text):
        header = {
            "Authorization": "Bearer " + COPYMATICAPI,
            'Content-Type': 'application/json'
        }
        data = {
            "model": "sentence-rewriter",
            "tone": "professional",
            "creativity": "high",
            "sentence": text,
            "language": "English (US)"
        }

        res = requests.post('https://api.copymatic.ai', json=data, headers=header)
        try:
            content = json.loads(res.content)
            best_text = get_text_by_max_length(content["ideas"])
        except:
            best_text = text

        return best_text
