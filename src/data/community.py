#!/usr/bin/env python3

from urllib.request import urlopen
from pathlib import Path

from urllib.parse import urlparse, parse_qs, unquote
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


class DescriptionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_p = False
        self.p_content = None
        self.ps = []
        self.links = []
        self.blog = None
        self.social = []
        self.p_count = 0
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            self.in_p = True
            self.p_count += 1
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    h = attr[1]
                    parsed = urlparse(h)
                    if parsed.netloc == 'nam10.safelinks.protection.outlook.com':
                      query_params = parse_qs(parsed.query)
                      #print("\n\norig",h)
                      h = unquote(query_params.get("url", [""])[0])
                      #print("unpa",h)
                    elif parsed.netloc == 'customerconnect.vmware.com':
                      print("removing!!",h)
                      h = ""
                    self.current_link = {"href": h, "text": ""}

    def handle_endtag(self, tag):
        if tag == "p":
            if self.p_content != "":
              p=self.p_content.strip()
              if not p[len(p)-1] in [".","!","?"]:
                p += "."
              self.ps.append(p)
              self.p_content = ""
            self.in_p = False
        if tag == "a" and self.current_link:
          linktype = self.current_link["text"].strip().lower() 
          if linktype == "blog":
            self.blog = self.current_link
          elif linktype in ["community hub","bluesky","mastodon","linkedin","twitter","reddit"]:
            self.social.append(self.current_link)
          elif linktype and linktype != "":
            self.links.append(self.current_link)
          self.current_link = None


    def handle_data(self, data):
        if self.in_p: 
            if self.p_content is None:
                self.p_content = strip_tags(data.strip())
            else:
                self.p_content += strip_tags(" " + data.strip())
        
        if self.current_link is not None:
            self.current_link["text"] += strip_tags(data.strip())






class CommunityLinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = []
        self.lookfor = "mega-menu/index"
        
    #data-preact="mega-menu/index"
    def handle_starttag(self, tag, attrs):
        if tag == "div":
            attr_dict = dict(attrs)
            if "data-preact" in attr_dict:
              if self.lookfor in attr_dict["data-preact"].split():
                self.data.append(attr_dict)
    


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
  generated = "community.json"

  generateddata = []


  cache = ".community.cache"
  url = "https://community.veeam.com"

  download_if_missing(url,cache)
 
  links = [] 
  with Path(cache).open("r", encoding="utf-8") as f:
        parser = CommunityLinkExtractor()
        parser.feed(f.read())
        if len(parser.data) > 0:
          if "data-props" in parser.data[0]:
            dp = json.loads(parser.data[0]["data-props"])
            #with open(".community.dp.cache", "w", encoding="utf-8") as f:
            #  json.dump(dp, f, indent=4)
            #cat .community.dp.cache | jq '.communityCategoriesV2[] | .children[] | .title,.url'
            for comm in dp["communityCategoriesV2"]:
              commtitle = comm["title"]
              for child in comm["children"]:
                childtitle = child["title"]
                childurl = child["url"]
                links.append({"link":childurl,"title":f"{commtitle} {childtitle}","description":f"{commtitle} {childtitle}"})

  cache = ".community.groups.cache"
  url = "https://community.veeam.com/groups"
  #

  download_if_missing(url,cache)


  with Path(cache).open("r", encoding="utf-8") as f:
        parser = CommunityLinkExtractor()
        parser.lookfor = "groups-destination/GroupOverview"
        parser.feed(f.read())
        if len(parser.data) > 0:
         if "data-props" in parser.data[0]:
          dp = json.loads(parser.data[0]["data-props"])
          with open(".community.dp.cache", "w", encoding="utf-8") as f:
            json.dump(dp, f, indent=4)
          #cat .community.dp.cache | jq '.communityCategoriesV2[] | .children[] | .title,.url'
          for g in dp["groups"]["otherGroups"]:
            gtitle = g["title"]
            gurl = g["url"]
            links.append({"link":gurl,"title":f"{gtitle}","description":f"User Group {gtitle}"})



  cachen = ".community.mvp.$name$.cache"
  mvps = [ {"name":"Vanguard","url":"https://community.veeam.com/p/veeamvanguard2025"},
        {"url":"https://community.veeam.com/p/veeammvp2025","name":"MVP"},
        {"url":"https://community.veeam.com/p/veeamlegends2025","name":"Veeam Legend"}]
  

  for m in mvps:
   name = m["name"]
   cache = cachen.replace("$name$",name.replace(" ","_"))
   download_if_missing(m["url"],cache)


   with Path(cache).open("r", encoding="utf-8") as f:
        parser = CommunityLinkExtractor()
        parser.lookfor = "widget-banner/index"
        parser.feed(f.read())
        for mvp in parser.data:
         if "data-props" in mvp and "content" in mvp["data-props"]:
          dp = json.loads(mvp["data-props"])["content"]
          title = dp["title"]
          desc = dp["description"]
          parser = DescriptionParser()
          parser.feed(desc)
          c = " ".join(parser.ps[0:parser.p_count-1])
          ls = parser.links
          blog = parser.blog
          if c != "" and (len(ls) > 0 or blog != None):
                if blog != None:
                  links.append({"link":blog['href'],"title":f"{name} Blog {title}","description":f"{c}","addlinks":ls})
                else:
                  links.append({"link":ls[0]['href'],"title":f"{name} {title}","description":f"{c}","addlinks":ls[1:]})
                 
          #else:
          #      print("no links",title,desc)

  google = "https://www.google.com/search?q=site%3Acommunity.veeam.com"
  
  links.append({"link":google,
    "title": "Deepquery community",
    "description": "Search directly google in veeam domain by adding q=",
    "deepquery":google+"+$deepquery$"
  })
 


  forums = {"catname":"Community","catlinks":links}
  generateddata.append(forums)
 
  with open(generated, "w", encoding="utf-8") as f:
    json.dump(generateddata, f, indent=4)
 

if __name__ == "__main__":
    main()

