from getbrowser import setup_chrome
from markitdown import MarkItDown
import json
import os,io
import threading
import requests
from dotenv import load_dotenv
from DataRecorder import Recorder

import datetime

date_today = datetime.date.today().strftime("%Y-%m-%d")
os.makedirs("./result", exist_ok=True)

outfile=Recorder(f'./result/{date_today}.csv')

load_dotenv()

# Initialize global variables
markitdown = MarkItDown()
concurrency =1

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

def openai_api_call(api_key, prompt, model="gpt-4o-mini", retries=3, delay=5):
    url = "https://heisenberg-duckduckgo-66.deno.dev/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}]}

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Request failed with status code {response.status_code}: {response.text}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")

        if attempt < retries - 1:
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    
    return {"error": f"Failed after {retries} attempts"}


def md2json(md, api_key):
    prompt = "extract structure json,include project_name,purchasing_unit,administrative_area,announcement_time,review_experts,total_bid_amount,contact_phone,contact_person,purchasing_unit_address,purchasing_unit_contact,brand,pdf attchmentlink ,return as flat json only\n" + md
    prompt = "extract structure csv,include project_name,purchasing_unit,administrative_area,announcement_time,review_experts list,total_bid_amount,采购标的,品目名称,品牌,规格型号,单价,数量,contact_phone,contact_person list,purchasing_unit_address,purchasing_unit_contact,pdf attchmentlink list,return as flat csv only\n" + md
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
        results = tab.eles("@href^http://www.ccgp.gov.cn/cggg/dfgg/")
        for i in results:
            url = i.attr("href")
            urls.append(url)
    return urls

def process_url(url, api_key):
    tab=browser.new_tab()
    tab.get(url)
    html=tab.html
    if html is None:

        return 
    if '中标公告' not in html:
        return 
    md = markitdown.convert_stream(io.StringIO(html)).text_content
    data = md2json(md, api_key)
    if data is None:
        return
    filename = url.split("/")[-1].replace(".htm", ".txt")
    
    outfile1=Recorder(f'./result/{filename}')
    outfile1.add_data(md)
    outfile1.record()

    if '```':
        data=data.replace('\n```','')

        data=data.replace('```csv\n','')
        print('===',data)
        # data = json.loads(data)
        for line in data.split('\n'):
            outfile.add_data(line.strip().split(','))
    # filename = url.split("/")[-1].replace(".htm", "")
    # filepath = os.path.join("result", filename + ".csv")
    # with open(filepath, "w", encoding="utf-8") as file:
        # json.dump(data, file, ensure_ascii=False, indent=2)
        # file.write(data)
        # print(f"Saved JSON file: {filepath}")

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    api_key='123456'
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY environment variable.")

    counts = get_page_count()
    if counts is None:
        print('No pages found')
        return
    counts=1
    urls = get_urls(counts)
    tasks = []
    print(urls)
    for url in urls:
        url=url.replace('http://','https://')
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
    outfile.record()

if __name__ == "__main__":
    main()
