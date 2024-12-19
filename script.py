from dotenv import load_dotenv
from DrissionPage import Chromium
import os
import json
import platform
import subprocess
from pathlib import Path

def find_chrome_path():
    """Find Chrome browser path based on operating system"""
    system = platform.system()
    
    if system == "Linux":
        # Common Linux Chrome paths
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            # Add snap path
            "/snap/bin/chromium",
            "/snap/chromium/current/usr/lib/chromium-browser/chrome",
        ]
        
        # Try to find Chrome using 'which' command
        try:
            chrome_path = subprocess.check_output(["which", "google-chrome"], 
                                               stderr=subprocess.STDOUT).decode().strip()
            chrome_paths.insert(0, chrome_path)
        except subprocess.CalledProcessError:
            pass
            
        # Check each path
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"Found Chrome at: {path}")
                return path
                
    elif system == "Darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
        for path in chrome_paths:
            path = os.path.expanduser(path)
            if os.path.exists(path):
                return path
                
    elif system == "Windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe",
            r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe",
            r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"
        ]
        for path in chrome_paths:
            path = os.path.expandvars(path)
            if os.path.exists(path):
                return path
    
    print("Chrome not found in common locations")
    return None

def setup_chrome():
    """Setup Chrome with appropriate configurations"""
    chrome_path = find_chrome_path()
    if not chrome_path:
        raise Exception("Chrome browser not found. Please install Chrome.")
    
    chrome_options = {
        'binary_location': chrome_path,
        'arguments': [
            '--no-sandbox',
            '--headless',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-software-rasterizer'
        ]
    }
    
    return Chromium(chrome_options)

def get_search_volume():
    try:
        load_dotenv()
        keyword = os.getenv('keyword')
        if not keyword:
            raise ValueError("No keyword provided in environment variables")
        
        # Initialize browser with custom setup
        browser = setup_chrome()
        tab = browser.latest_tab
        
        # Process keywords
        keywords = keyword.split(',') if ',' in keyword else [keyword]
        results = []
        
        for k in keywords:
            try:
                # Format URL with the keyword
                url = f'https://www.spyfu.com/keyword/overview?vwot=aa&query={k.strip()}'
                print(f"Accessing URL: {url}")
                
                tab.get(url)
                tab.change_mode()
                
                # Wait for element and get data
                ele = tab.ele('.montly-volume', timeout=10)
                if ele:
                    search_volume = ele.text
                else:
                    search_volume = "N/A"
                
                # Create data dictionary for current keyword
                data = {
                    "keyword": k.strip(),
                    "sv": search_volume
                }
                results.append(data)
                print(f'Processed: {data}')
                
            except Exception as e:
                print(f"Error processing keyword '{k}': {str(e)}")
                results.append({
                    "keyword": k.strip(),
                    "sv": "Error",
                    "error": str(e)
                })
        
        # Combine all results into a single JSON
        final_result = {
            "keywords_data": results,
            "total_keywords": len(results),
            "successful_queries": len([r for r in results if r.get('sv') != "Error"])
        }
        
        # Convert to JSON string
        json_result = json.dumps(final_result, indent=2)
        return json_result
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "keywords_data": [],
            "total_keywords": 0,
            "successful_queries": 0
        }
        return json.dumps(error_result, indent=2)

if __name__ == "__main__":
    print("System Information:")
    print(f"Operating System: {platform.system()}")
    print(f"OS Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print("\nStarting search volume retrieval...")
    
    result = get_search_volume()
    print("\nFinal JSON Result:")
    print(result)
