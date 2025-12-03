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
      base_url = urllib.parse.urlunparse((p.scheme, p.netloc,new_path,"","",""))
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
        self.tocclass = 'page-toc__search-links' 
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
            if not self.in_target_ul and self.tocclass in class_attr.split():
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
                "href": ("/".join([self.base_url,attrs_dict.get('href').lstrip("/")])),
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




def main():
  generated = "helpcenter.json"

  generateddata = []


  cache = ".helpcenter.cache"
  url = "https://helpcenter.veeam.com/services/component/technical_documentation_table/select?productId=&version=&resourceType=&localeCode=en&isInitial=&initialLocaleCode=en&queryPrdCode=&offset=0&limit=10"

  download_if_missing(url,cache)
 
  links = [] 
  saw = {}



  cachep = ".helpcenter.$ind$.cache"

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
            #print("found dt",title,doctitle)
            for n,v in doclinks.items():
                if not v in saw:
                  new_link = {"link":v,"title":f"{doctitle}","description":f"Helpcenter link to {doctitle} for product {title} in format {n} of type {dt}"}
                  addlinks = []
                  p = urllib.parse.urlparse(v)
                  new_path = p.path
                  if new_path.endswith(".html") or new_path.endswith(".html") :
                    new_path = new_path.rsplit("/", 1)[0]
                  p._replace(path=new_path)
                  base_url = urllib.parse.urlunparse((p.scheme, p.netloc,new_path,"","","")).strip("/")

                  titlesp= new_path.split("/")
                  
                  if len(titlesp) > 2 and titlesp[1] == "docs":
                    #if titlesp[2] in ["vbr"]:
                      try:
                        cachetitle= "-".join(titlesp[2:]).strip("-")
                        cache = cachep.replace("$ind$",cachetitle)
                        download_if_missing(v,cache)
                        
                        with Path(cache).open("r", encoding="utf-8") as f:
                          parser = TocParser()
                          parser.base_url = base_url
                          parser.feed(f.read())
                          #just want 3 levels deep here
                          for gp in parser.result:
                            addlinks.append({"text":gp["title"],"href":gp["href"]})
                            for p in gp["children"]:
                              addlinks.append({"text":p["title"],"href":p["href"]})
                              for c in p["children"]:
                                addlinks.append({"text":c["title"],"href":c["href"]})
                      except Exception as e:
                        print("!!!!!!!!",v,e)
                        #traceback.print_exc()
                    #else:
                    #  print("no deep processing list",titlesp)
                  else:
                    print("no deep processing possible",titlesp)
                  new_link["addlinks"] = addlinks
                  links.append(new_link)
                else:
                        print("duplicate",v)
                saw[v] = True

  cachep = ".kasten.latest.$ind$.cache"
  kastenstart = "https://docs.kasten.io/latest/"
  url = kastenstart
  cache = cachep.replace("$ind$","_start")
  download_if_missing(url,cache)

  addlinks = []
  seen = {"kastenstart":True}
  with Path(cache).open("r", encoding="utf-8") as f:  
    parser = TocParser()
    parser.tocclass = "theme-doc-sidebar-menu"
    parser.base_url = "https://docs.kasten.io"
    parser.feed(f.read())
    for kat in parser.result:
      t=kat["title"]
      h=kat["href"].rstrip("/")
      addlinks.append({"text":t,"href":h})
      seen[kat["href"]] = True
      n=h.rsplit("/",1)[1]
      cache = cachep.replace("$ind$",n)
      download_if_missing(kat["href"],cache)
      with Path(cache).open("r", encoding="utf-8") as d:
        subparser = TocParser()  
        subparser.tocclass = "theme-doc-sidebar-menu"
        subparser.base_url = "https://docs.kasten.io"
        subparser.feed(d.read())
        for s in subparser.result:
          if len(s["children"]) > 0:
           for cld in s["children"]:
            if not cld["href"] in seen:
              t=cld["title"]
              h=cld["href"].rstrip("/")
              addlinks.append({"text":t,"href":h})
              seen[cld["href"]] = True
              n=h.rsplit("/",1)[1]


  links.append({"link":kastenstart,"title":"Kasten Helpcenter","description":"Kasten documentation for Kubernetes / Openshift backup and DR",
        "addlinks":addlinks})

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

