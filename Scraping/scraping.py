import requests 


web =requests.get("https://www.youtube.com/")
print(web)

print(web.content)