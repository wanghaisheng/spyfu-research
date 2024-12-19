from DrissionPage import ChromiumOptions, ChromiumPage
# co = ChromiumOptions().headless()
# browser = Chromium(co)

def getahrefkd(k,browser):

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



def getahrefsv(k,browser):

    url = "https://ahrefs.com/keyword-generator/"
    browser.get(url)
    # keyword = "remini.ai"
    browser.ele("@placeholder=Enter keyword").input(keyword)

    # 点击登录按钮
    browser.ele("text=Check keyword").click()
    svs=browser.ele('t:table').eles('t:tr')
    results=[]
    for line in eles:
       cols= line.eles('t:td'):
       k=cols[0].text
       kd=cols[1].text
       volume=cols[2].text
       results.append({

           "keyowrd":k,
           "kdlevel":kd,
           volume:volume
       }) 

    return {"data":results }

