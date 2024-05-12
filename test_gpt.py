import requests
import json

url = "http://24e89c9e7d36:1337/v1/chat/completions"
body = {'model': '', 'provider': 'Bing', 'stream': True, 'messages': [{'role': 'assistant', 'content': 'What can you do? Who are you?'}]}
lines = requests.post(url, json=body, stream=True).iter_lines()

print(lines)