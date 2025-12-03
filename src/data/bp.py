#!/usr/bin/env python3

from urllib.request import urlopen
import urllib.parse
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


def baseurl(url):
      p = urllib.parse.urlparse(url)
      new_path = p.path
      if new_path.endswith(".html") or new_path.endswith(".html") :
        new_path = new_path.rsplit("/", 1)[0]
      p._replace(path=new_path)
      base_url = urllib.parse.urlunparse((p.scheme, p.netloc,new_path,"","","")).strip("/")
      return base_url


class MetaRefreshExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refresh_info = None
        self.refresh = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "meta":
            attrs_dict = dict((k.lower(), v) for k, v in attrs)
            if attrs_dict.get("http-equiv", "").lower() == "refresh":
                content = attrs_dict.get("content", "")
                self.refresh_info = self.parse_content(content)
                self.refresh = True

    def parse_content(self, content):
        # Example: "5; url=https://example.com"
        parts = content.split(";")
        delay = None
        url = None
        if parts:
            delay = parts[0].strip()
        if len(parts) > 1 and "url=" in parts[1].lower():
            url = parts[1].split("=", 1)[1].strip()
        return {"delay": delay, "url": url}



def download_if_missing(url, file_path):
    file = Path(file_path)
    if not file.exists():
        print(f"Downloading {url}...")
        data = ""
        with urlopen(url) as response:
          data = response.read()

          parser = MetaRefreshExtractor()
          parser.feed(data.decode("utf-8"))
          
          if parser.refresh:
            url = "/".join([baseurl(url).strip("/"), parser.refresh_info["url"].strip("/")]);
            print("!!!redirect",url) 
            with urlopen(url) as response:
              data = response.read()
          
        with open(file_path, "wb") as out_file:
          out_file.write(data)
        print(f">>>>>>>> Saved to {file}")
    else:
        print(f"File already exists: {file}")




class TocParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Track whether we're inside the target UL
        self.in_target_ul = False
        self.target_ul_depth = 0  # nesting depth from the target <ul>
        self.base_url=""

        # Stack of containers for nested structure
        # When we enter a <ul> under the target, push a list (children of that level)
        # When we enter a <li>, push an item dict
        self.container_stack = []  # mix of list (children) and dict (li item)

        # Track current anchor inside a <li>
        self.current_a = None      # dict with {'href': ..., 'title': ...}
        self.capture_text_for_a = False

        # Result will be top-level children list once we exit target UL
        self.result = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == 'ul':
            class_attr = attrs_dict.get('class', '')
            # Entering the target UL?
            if not self.in_target_ul and 'nav-list' in class_attr.split():
                self.in_target_ul = True
                self.target_ul_depth = 1
                # Top-level children list
                self.container_stack.append(self.result)
            elif self.in_target_ul:
                # Nested UL inside target UL
                self.target_ul_depth += 1
                # Create a new children list and attach it to the current LI (dict)
                children = []
                self.container_stack.append(children)
                # Attach children to the nearest LI dict (search backward)
                for i in range(len(self.container_stack) - 2, -1, -1):
                    if isinstance(self.container_stack[i], dict):
                        self.container_stack[i]['children'] = children
                        break

        elif tag == 'li' and self.in_target_ul:
            # Start a new item under current children list
            item = {"title": None, "href": None, "children": []}
            self.container_stack.append(item)

        elif tag == 'a' and self.in_target_ul:
            # We only care about anchors within LIs
            self.current_a = {
                "href": ("/".join([self.base_url.strip("/"),attrs_dict.get('href').strip("/")])),
                "title": ""
            }
            self.capture_text_for_a = True

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_target_ul and self.current_a:
            # Finalize current anchor
            self.capture_text_for_a = False
            # Assign to nearest LI dict (the last dict in stack)
            for i in range(len(self.container_stack) - 1, -1, -1):
                if isinstance(self.container_stack[i], dict):
                    self.container_stack[i]["href"] = self.current_a.get("href")
                    title_text = self.current_a.get("title", "").strip()
                    self.container_stack[i]["title"] = title_text if title_text else None
                    break
            self.current_a = None

        elif tag == 'li' and self.in_target_ul:
            # Pop the current item and append it to the nearest children list
            # (the most recent list on the stack)
            if self.container_stack and isinstance(self.container_stack[-1], dict):
                item = self.container_stack.pop()
                # Find nearest list (children)
                for i in range(len(self.container_stack) - 1, -1, -1):
                    if isinstance(self.container_stack[i], list):
                        # If item['children'] is empty but was linked to a separate list,
                        # keep as is; else ensure an empty list is present.
                        item.setdefault('children', [])
                        self.container_stack[i].append(item)
                        break

        elif tag == 'ul' and self.in_target_ul:
            # Exit a UL level
            if self.target_ul_depth > 0:
                self.target_ul_depth -= 1
            # Pop the current children list when leaving nested UL
            if self.container_stack and isinstance(self.container_stack[-1], list):
                self.container_stack.pop()

            # If we've fully exited the target UL
            if self.target_ul_depth == 0:
                self.in_target_ul = False

    def handle_data(self, data):
        # Collect text inside <a> tags for titles
        if self.capture_text_for_a and self.current_a is not None:
            self.current_a["title"] += data

    def error(self, message):
        # HTMLParser requires an error method; no-op
        pass


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []
        self.iscookbook = False
        self.seen = {}

    def handle_data(self, data):
        if self.iscookbook:
                self.text.append(data)

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.iscookbook = False
        if tag == "a" and "href" in attrs_dict:
               href = attrs_dict.get("href")
               if "https://veeamcookbook.com/" in href and not href in self.seen:
                self.iscookbook = True
                self.seen[href] = True
                self.links.append({"link":href,"title":"","description":""}) 

    def handle_endtag(self, tag):
        if tag == "a" and self.iscookbook and len(self.links) >0:
               self.links[-1]["title"] = "".join(self.text)
               self.links[-1]["description"] = "".join(self.text)+". This is a collection of recipes to complete one task in the product during PoC or evaluation"
               self.text = []

def main():
  generated = "bp.json"

  generateddata = []


  links = [{
        "title": "Veeam Backup & Replication Best Practices",
        "link": "https://bp.veeam.com/vbr",
        "description": "BP guide for Veeam Backup & Replication created by the Solutions Architects"
      },
      {
        "title": "VCSP Best Practices guide",
        "link": "https://bp.veeam.com/sp",
        "description": "This guide is intended to provide best practices on the different Veeam-powered services for our Cloud & Service Providers."
      },
      {
        "title":"Veeam Security Best Practices",
        "link":"https://bp.veeam.com/security",
        "description":"The Security of an I.T. system is a paramount requirement. No deployment of any hardware or software component can be considered complete without considering its security. Cyber Security is simply something nobody can afford to ignore."
      },
      {
        "title":"Best Practice Guide for Veeam Backup for Microsoft 365",
        "link":"https://bp.veeam.com/vb365",
        "description":"This guide is intended to provide bp for Veeam Backup for Microsoft 365"
      },
      {
        "title":"Veeam Recovery Orchestrator Knowledge Base",
        "link":"https://bp.veeam.com/vro",
        "description":"This guide is intended to provide information and best practices for Veeam Recovery Orchestrator. It is not meant as a full documentation or detailed explanation of the features. Please refer to the Veeam Help Center for these kinds of documents."
      }] 


  cachep = ".bp.$ind$.cache"

  for bp in links:
        lurl = bp["link"] 
        n = lurl.rsplit("/",1)[1]
        cache = cachep.replace("$ind$",n)
        download_if_missing(lurl,cache)
        
        addlinks = []
        with open(cache, "r", encoding="utf-8") as f: 
          parser = TocParser()
          parser.base_url = "https://bp.veeam.com"
          parser.feed(f.read())
          #just want 3 levels deep here
          for gp in parser.result:
            addlinks.append({"text":gp["title"],"href":gp["href"]})
            for p in gp["children"]:
              addlinks.append({"text":p["title"],"href":p["href"]})
              for c in p["children"]:
                addlinks.append({"text":c["title"],"href":c["href"]})
        bp["addlinks"] = addlinks

  url = "https://veeamcookbook.com"
  cache = ".bp.cookbook.cache"
  download_if_missing(url,cache)
  with open(cache, "r", encoding="utf-8") as f: 
    parser = LinkParser()
    parser.feed(f.read())
    for l in parser.links:
        links.append(l)

  links.append({"link":"https://vccbook.io","title":"Veeam Cloud Connect 12 Reference Architecture","description":"Luca Dell’Oca is Principal EMEA Cloud Architect for Veeam Software. At Veeam, Luca works with the biggest service providers and telecommunication companies to help them use at full potential the Veeam technologies developed for Cloud and Service Providers. Luca is the author of this Veeam Cloud Connect book, co-author of the Veeam Service Provider Best Practices, and a multitude of technical resources related to service providers and cloud technologies."})
  links.append({"link":"https://www.google.com/search?q=site%3Abp.veeam.com",
    "title": "Deepquery bp",
    "description": "Search directly google in bp domain by adding q=",
    "deepquery":"https://www.google.com/search?q=site%3Abp.veeam.com+$deepquery$"
  })
  bp = {"catname":"Best Practices","cattags":"BP","catlinks":links}
  generateddata.append(bp)
 
  with open(generated, "w", encoding="utf-8") as f:
    json.dump(generateddata, f, indent=4)
 

if __name__ == "__main__":
    main()

