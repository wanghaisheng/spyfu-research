from getbrowser import setup_chrome
from markitdown import MarkItDown
import json
import os
import threading
import requests
from dotenv import load_dotenv
load_dotenv()

# Initialize global variables
markitdown = MarkItDown()
concurrency = 5

# Setup browser
browser = setup_chrome()

def openai_api_call(api_key, prompt, model="gpt-4o-mini"):
    url = "https://heisenberg-duckduckgo-66.deno.dev/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}]}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": str(e)}

def md2json(md, api_key):
    prompt = "extract structure json\n" + md
    response = openai_api_call(api_key, prompt)

    if "error" in response:
        print(f"Error: {response['message']}")
        return None
    else:
        return response["choices"][0]["message"]["content"].strip()

def get_page_count(keyword=None):
    print("browser", browser)
    tab = browser.new_tab()
    domain = "https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=7&dbselect=bidx&kw=CT&start_time=2024%3A06%3A25&end_time=2024%3A12%3A24&timeType=5&displayZone=&zoneId=&pppStatus=0&agentName="

    tab.get(domain)
    print("Loading page count...")
    counts = tab.ele(".pager").eles("tag:a")[-2].text
    print(f"Found {counts} pages")
    
    return int(counts)

def get_urls(counts):
    urls = []

    for page in range(1, counts + 1):
        print(f'Detecting page {page}')
        tab = browser.new_tab()
        domain = f"https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index={page}&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=7&dbselect=bidx&kw=CT&start_time=2024%3A06%3A25&end_time=2024%3A12%3A24&timeType=5&displayZone=&zoneId=&pppStatus=0&agentName="
        tab.get(domain)
        results = tab.eles("@href^https://www.ccgp.gov.cn/cggg/dfgg/")
        for i in results:
            url = i.attr("href")
            urls.append(url)
    return urls

def process_url(url, api_key):
    md = markitdown.convert(url)
    data = md2json(md, api_key)
    if data is None:
        return

    os.makedirs("./result", exist_ok=True)
    filename = url.split("/")[-1].replace(".html", "")
    filepath = os.path.join("result", filename + ".json")
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"Saved JSON file: {filepath}")

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY environment variable.")

    counts = get_page_count()
    if counts is None:
        print('No pages found')
        return

    urls = get_urls(counts)
    tasks = []

    for url in urls:
        task = threading.Thread(target=process_url, args=(url, api_key))
        tasks.append(task)
        task.start()
        if len(tasks) >= concurrency:
            for task in tasks:
                task.join()
            tasks = []

    # Ensure remaining tasks are completed
    for task in tasks:
        task.join()

if __name__ == "__main__":
    main()
