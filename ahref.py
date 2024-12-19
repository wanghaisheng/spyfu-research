from DrissionPage import ChromiumOptions, ChromiumPage
co = ChromiumOptions().headless()

def getahrefkd(k):
    browser = Chromium(co)

    url = "https://ahrefs.com/keyword-difficulty/"
    browser.get(url)
    # keyword = "remini.ai"
    browser.ele("@placeholder=Enter keyword").input(keyword)

    # 点击登录按钮
    browser.ele("text=Check keyword").click()
    kd = browser.ele(".css-16bvajg-chartValue").text

    kds = browser.ele(".css-1wi5h2-row css-1crciv5 css-6rbp9c").text
    #     print(kd)
    #     print(kds)

    return {"keyword": keyword, "kd": kd, "des": kds}



def getahrefsv(k):
    browser = Chromium(co)

    url = "https://ahrefs.com/keyword-difficulty/"
    browser.get(url)
    # keyword = "remini.ai"
    browser.ele("@placeholder=Enter keyword").input(keyword)

    # 点击登录按钮
    browser.ele("text=Check keyword").click()
    kd = browser.ele(".css-16bvajg-chartValue").text

    kds = browser.ele(".css-1wi5h2-row css-1crciv5 css-6rbp9c").text
    #     print(kd)
    #     print(kds)

    return {"keyword": keyword, "kd": kd, "des": kds}

