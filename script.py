from dotenv import load_dotenv
from DrissionPage import Chromium,ChromiumOptions
import os
import json
co = ChromiumOptions().headless()
browser = Chromium()


load_dotenv()
keyword = os.getenv('keyword')
    
# Initialize browser and create tab object
    
    # Process keywords
keywords = keyword.split(',') if ',' in keyword else [keyword]
def get_search_volume():
    
    results = []
    
    for k in keywords:
        # Format URL with the keyword
        if ' ' in k:
            k=k.replace(' ','%20')
        url = f'https://www.spyfu.com/keyword/overview?vwot=aa&query={k}'
        browser.get(url)
        browser.change_mode()
        
        # Find the monthly volume element
        ele = browser.ele('.montly-volume')
        
        # Create data dictionary for current keyword
        data = {
            "keyword": k,
            "sv": ele.text
        }
        results.append(data)
        print(f'Processing: {data}')
    
    # Combine all results into a single JSON
    final_result = {
        "keywords_data": results
    }
    
    # Convert to JSON string
    json_result = json.dumps(final_result, indent=2)
    return json_result

if __name__ == "__main__":
    result = get_search_volume()
    print("\nFinal JSON Result:")
    print(result)
