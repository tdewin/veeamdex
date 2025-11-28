#!/usr/bin/env python3
import urllib.request
import json

url = "https://api.github.com/orgs/veeamhub/repos"
headers = {
    "Accept": "application/vnd.github+json"
}

# Build the request
req = urllib.request.Request(url, headers=headers)

# Send the request and read the response
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())

# Print repository details
print("Number of repos:", len(data))

generateddata = []
links = []
for repo in data:
    if repo["name"] != ".github":
      #print(f"- {repo['description']} {repo['name']} (URL: {repo['html_url']})")
      links.append({"link":repo['html_url'],
        "title": f"{repo['name']}",
        "description": repo['description'] if repo['description'] else "" , 
      })
 


github = {"catname":"Github","catlinks":links}
generateddata.append(github)

generated = "veeamhub.json"
with open(generated, "w", encoding="utf-8") as f:
  json.dump(generateddata, f, indent=4)
