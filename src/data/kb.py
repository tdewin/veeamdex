#!/usr/bin/env python3

from urllib.request import urlopen
from pathlib import Path

from html import unescape
import json


from html.parser import HTMLParser

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, data):
        self.text.append(data)
    def get_data(self):
        return "".join(self.text)

def strip_tags(html):
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_data().replace("\u00a0", " ")






def download_if_missing(url, file_path):
    file = Path(file_path)
    if not file.exists():
        print(f"Downloading {url}...")
        with urlopen(url) as response, open(file_path, "wb") as out_file:
            out_file.write(response.read())
        print(f"Saved to {file}")
    else:
        print(f"File already exists: {file}")

def main():
  generated = "kb.json"

  generateddata = []


  cache = ".kb.cache"
  url = "https://www.veeam.com/services/kb-articles?product=&version=&type=&fromModificationDate=&toModificationDate=&search=&offset=0&limit=1"

  download_if_missing(url,cache)
 
  links = [] 
  with Path(cache).open("r", encoding="utf-8") as f:
        content = json.load(f)
        for filtr in content["filters"]:
          if filtr["name"] == "product":
            for p in filtr["items"]:
              t = strip_tags(unescape(p['text']))
              v = strip_tags(unescape(p['value']))
              links.append({"description":f"Knowledge Base for {t} - {v}","title":f"{t}",
                "link":f"https://www.veeam.com/knowledge-base.html?product={v}",
                "deepquery":f"https://www.veeam.com/knowledge-base.html?product={v}&search=$deepquery$"})

  kb = {"catname":"Knowledge Base","cattags":["kb"],"catlinks":links}
  generateddata.append(kb)

  google = "https://www.google.com/search?q=site%3Aveeam.com+%22KB+ID%22"
  
  links.append({"link":google,
    "title": "Deepquery kb article",
    "description": "Search directly google in veeam domain by adding q=",
    "deepquery":google+"+$deepquery$"
  })
 
  with open(generated, "w", encoding="utf-8") as f:
    json.dump(generateddata, f, indent=4)
 

if __name__ == "__main__":
    main()

