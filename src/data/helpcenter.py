#!/usr/bin/env python3

from urllib.request import urlopen
from pathlib import Path

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
  generated = "helpcenter.json"

  generateddata = []


  cache = ".helpcenter.cache"
  url = "https://helpcenter.veeam.com/services/component/technical_documentation_table/select?productId=&version=&resourceType=&localeCode=en&isInitial=&initialLocaleCode=en&queryPrdCode=&offset=0&limit=10"

  download_if_missing(url,cache)
 
  links = [] 
  saw = {}

  with Path(cache).open("r", encoding="utf-8") as f:
    data = json.load(f)
    for product in data["payload"]["products"]:
        title = strip_tags(product["productTitle"])
        for dg in product['documentGroups']:
          documents = dg['documents']
          dt = dg['documentGroupType']
          for doc in documents:
            doctitle = strip_tags(doc['documentTitle'])
            doclinks = doc['links']
            print(title,doctitle)
            for n,v in doclinks.items():
                if not v in saw:
                        links.append({"link":v,"title":f"{doctitle}","description":f"Helpcenter link to {doctitle} for product {title} in format {n} of type {dt}"})
                else:
                        print("duplicate",v)
                saw[v] = True

  links.append({"link":"https://www.google.com/search?q=site%3Ahelpcenter.veeam.com",
    "title": "Deepquery helpcenter",
    "description": "Search directly google in helpcenter domain by adding q=",
    "deepquery":"https://www.google.com/search?q=site%3Ahelpcenter.veeam.com+$deepquery$"
  })
  helpcenter = {"catname":"Helpcenter","catlinks":links}
  generateddata.append(helpcenter)
 
  with open(generated, "w", encoding="utf-8") as f:
    json.dump(generateddata, f, indent=4)
 

if __name__ == "__main__":
    main()

