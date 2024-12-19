from DrissionPage import ChromiumOptions, ChromiumPage

def getahrefkd(keyword, browser):
    """Get keyword difficulty from Ahrefs"""
    try:
        url = "https://ahrefs.com/keyword-difficulty/"
        browser.get(url)
        
        # Input keyword
        browser.ele("@placeholder=Enter keyword").input(keyword)
        
        # Click check button
        browser.ele("text=Check keyword").click()
        
        # Get difficulty score and description
        kd = browser.ele(".css-16bvajg-chartValue").text
        kds = browser.ele(".css-1wi5h2-row css-1crciv5 css-6rbp9c").text
        
        return {
            "keyword": keyword,
            "kd": kd,
            "description": kds
        }
    except Exception as e:
        print(f"Error in getahrefkd: {str(e)}")
        return {
            "keyword": keyword,
            "kd": "Error",
            "description": str(e)
        }

def getahrefsv(keyword, browser):
    """Get search volume and related keywords from Ahrefs"""
    try:
        url = "https://ahrefs.com/keyword-generator/"
        browser.get(url)
        
        # Input keyword
        browser.ele("@placeholder=Enter keyword").input(keyword)
        
        # Click check button
        browser.ele("text=Check keyword").click()
        
        # Get table data
        table = browser.ele('t:table')
        rows = table.eles('t:tr')
        
        results = []
        for row in rows:
            cols = row.eles('t:td')
            if len(cols) >= 3:  # Ensure we have all needed columns
                results.append({
                    "keyword": cols[0].text,
                    "kd_level": cols[1].text,
                    "volume": cols[2].text
                })
        
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        print(f"Error in getahrefsv: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "data": []
        }

# Example usage
if __name__ == "__main__":
    try:
        # Initialize browser
        co = ChromiumOptions()
        co.headless()  # Optional: run in headless mode
        browser = ChromiumPage(co)
        
        # Test keyword
        test_keyword = "example"
        
        # Get keyword difficulty
        kd_result = getahrefkd(test_keyword, browser)
        print("\nKeyword Difficulty Result:")
        print(kd_result)
        
        # Get search volume and related keywords
        sv_result = getahrefsv(test_keyword, browser)
        print("\nSearch Volume Results:")
        print(sv_result)
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
    finally:
        if 'browser' in locals():
            browser.quit()
