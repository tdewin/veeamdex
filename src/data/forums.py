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





class ForumLinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_link = None
        self.forum = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attr_dict = dict(attrs)
            if "class" in attr_dict:
              current_link = {
                    "href": attr_dict.get("href"),
                    "type": "subforum",
                    "main": self.forum,
                    "text": ""
              }

              if "subforum" in attr_dict["class"].split():
                self.current_link = current_link
              if "forumtitle" in attr_dict["class"].split():
                current_link["type"] = "forum"
                self.current_link = current_link
    
    def handle_data(self, data):
        if self.current_link is not None:
            self.current_link["text"] += data.strip()

    def handle_endtag(self, tag):
        if tag == "a" and self.current_link:
            if self.current_link["type"] == "forum":
                self.forum = self.current_link["text"]
            self.links.append(self.current_link)
            self.current_link = None



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
  generated = "forums.json"

  generateddata = []


  cache = ".forums.cache"
  url = "https://forums.veeam.com"

  download_if_missing(url,cache)
 
  links = [] 
  with Path(cache).open("r", encoding="utf-8") as f:
        parser = ForumLinkExtractor()
        parser.feed(f.read())
        for l in parser.links:
                if l["type"] == "forum":
                        links.append({"description":f"General forum for {l['text']}","title":f"{l['text']}","link":l["href"]})
                else:
                        links.append({"description":f"Sub forum {l['text']} for {l['main']}","title":f"{l['text']}","link":l["href"]})


  google = "https://www.google.com/search?q=site%3Aforums.veeam.com"
  
  links.append({"link":google,
    "title": "Deepquery forums",
    "description": "Search directly google in veeam domain by adding q=",
    "deepquery":google+"+$deepquery$"
  })
 


  forums = {"catname":"Forums","catlinks":links}
  generateddata.append(forums)
 
  with open(generated, "w", encoding="utf-8") as f:
    json.dump(generateddata, f, indent=4)
 

if __name__ == "__main__":
    main()

