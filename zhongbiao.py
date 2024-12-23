from getbrowser import setup_chrome
from markitdown import MarkItDown
import json
import os
import threading
markitdown = MarkItDown()
concurrency=5

import requests

browser = setup_chrome()


def openai_api_call(api_key, prompt, model="gpt-4o-mini"):
    # Set the endpoint URL and headers
    url = "https://heisenberg-duckduckgo-66.deno.dev/v1/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Define the data payload
    # Modified
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}

    # Make the request
    response = requests.post(url, headers=headers, json=data)

    # Check for a successful response
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}


def md2json(md):

    api_key = "123456"
    prompt = "extract structure json\n" + md
    response = openai_api_call(api_key, prompt)

    if "error" in response:
        print(f"Error: {response['message']}")
    else:
        # Modified
        print(response["choices"][0]["message"]["content"].strip())


def getpagecount(keyword=None):
    print("borw", browser)
    tab = browser.new_tab()
    
    domain = "https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=7&dbselect=bidx&kw=CT&start_time=2024%3A06%3A25&end_time=2024%3A12%3A24&timeType=5&displayZone=&zoneId=&pppStatus=0&agentName="

    tab.get(domain)
    print("sssss")
    counts = tab.ele(".pager").eles("tag:a")[-2].text
    print(counts)
    return counts


def geturls(counts):
    urls = []

    for page in range(1, counts):
        tab = browser.new_tab()

        tab.get(url)
        results = tab.ele(".vT-srch-result-list-bid").eles("tag:a")
        for i in results:
            url = i.attr("href")
            urls.append(url)
    return urls


def processurl(url):
    # tab=browser.new_tab()
    # tab.get(url)
    # html=tab.html
    md = markitdown.convert(url)
    data = md2json(md)
    os.makedirs("./result", exist_ok=True)

    filename = url.split("/")[-1].replace(".html", "")
    filepath = os.path.join("result", filename + ".json")
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        print("save tag json file")


counts = getpagecount()
urls = geturls(counts)
tasks = []
getpagecount()
for url in urls:
    task = threading.Thread(target=processurl, args=(url))
    tasks.append(task)
    task.start()
    if len(tasks) >= concurrency:
        for task in tasks:
            task.join()
            tasks = []
