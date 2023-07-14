from flask import Flask, request
import requests
import cssutils
import platform
import logging
import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os
import pandas as pd
import gc

# Metrics Calculator/Tag Estimator
def metricsCalculator(url):
    # input the site name here
    site = url
    # code for selecting suitable user agent for linux, windows, macOS
    result1 = ""
    useragent = ''
    operating_Sys = platform.system()
    if operating_Sys == 'Windows':
        useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    elif operating_Sys == 'Linux':
        useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    elif operating_Sys == 'Darwin':
        useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    else:
        sys.exit("Error OS undertermined")

    # set appropiate server response time according to your server
    # Usual advice to set it higher due to worst case response times when server is under load
    server_response_time = 120
    session = requests.Session()
    session.headers.update({'User-Agent': useragent})
    response = session.get(site, timeout=server_response_time)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 1) finding no. of image tags
    img_tags = soup.find_all('img')
    result1=result1 + "Total " + str(len(img_tags)) + " Image tags Found!" + "\n"

    # 2) finding total no. of empty tags
    empty_tags = soup.findAll(lambda tag: tag.find(True) is None and (tag.string is None or tag.string.strip()==""))
    result1 = result1 + "Total " + str(len(empty_tags)) + " Empty tags Found!" + "\n"
    # for specificity use (example find empty <p> tags) -> empty_tags = soup.findAll(lambda tag: tag.name == 'p' and tag.find(True) is None and (tag.string is None or tag.string.strip()==""))

    # 3) finding no. of script tags
    script_tags = soup.find_all("script")
    text_inside_script_tag = script_tags[0].string
    result1 = result1 + "Total " + str(len(script_tags)) + " Script tags Found!" + "\n"

    # 4) finding no. of style sheet linked
    style_sheets = []
    link_tags_with_style_sheets = []

    link_tags = soup.find_all("link")
    for link in link_tags:
        if "stylesheet" in link.get("rel", []):
            link_tags_with_style_sheets.append(link)
            style_sheets.append(link["href"])
    result1 = result1 + "Total " + str(len(style_sheets)) + " Linked Style sheets Found!" + "\n"

    # 5) Total tags with empty href
    anchor_tags_no_href = []
    for a in soup.find_all('a', href=True):
        x = a['href']
        # if empty href found
        if x.strip()=="":
           anchor_tags_no_href.append(a)

    result1 = result1 + "Total " + str(len(anchor_tags_no_href))+ " anchor tags Found with empty href!" + "\n"

    # 6) find no. of font family (iterating through CSS files)
    css_files = []
    def collect_css_files(url):
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        css_list = []
        css = soup.find_all('link', rel="stylesheet")
        for each in css:
            href = each['href']
            if "http://" in href or "https://" in href:
                css_list.append(href)
        return css_list

    def iter_css_files(css_files):
        css_files_font_family = []
        for css_file in css_files:
            url = css_file
            server_response_time = 120
            session = requests.Session()
            session.headers.update({'User-Agent': useragent})
            response = session.get(url, timeout=server_response_time)
            content = response.content
            sheet = cssutils.parseString(content)
            results_per_file = []
            for rule in sheet:
                    if rule.type == cssutils.css.CSSFontFaceRule.FONT_FACE_RULE:
                        for prop in rule.style:
                            if prop.name == 'font-family':
                                results_per_file.append(prop.value)
            css_files_font_family.append(results_per_file)

        return css_files_font_family

    cssutils.log.setLevel(logging.CRITICAL)
    css_files = collect_css_files(url=site)
    css_files_font_family = iter_css_files(css_files)

    # Printing CSS files with the font familys included in them
    main_count = 0
    for index,file in enumerate(css_files):
        count = len(css_files_font_family[index])
        main_count = main_count + count
        # print(f'CSS FILE - {file} has {count} Font families')
        # print(f'FONT FAMILIES - {css_files_font_family[index]}')
    result1 = result1 + "Total " + str(main_count) + " Non-universal font-families detected!" + "\n"

    # Page transfer size
    def get_page_transfer_size(url):
        # Send a GET request to the website URL
        response = requests.get(url)
        # Get the content size in bytes
        content_size = sys.getsizeof(response.content)
        content_size = content_size / 1000000
        return content_size

    # print("Total Page transfer size:")
    result2 = get_page_transfer_size(site)
    result1 = result1 + "Total Page transfer size: " + str(result2) + " MB" + "\n" + str(result2)

    return result1

def SiteLocatorComponent(url):
    # Selenium with no sandbox mode on
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    # Navigate to the Site24x7 website
    driver.get("https://www.site24x7.com/tools/find-website-location.html")
    driver.implicitly_wait(10)
    # Find the input field and enter the website URL to search for
    input_field = driver.find_element(By.ID, "hostName")
    input_field.send_keys(url)
    input_field.send_keys(Keys.RETURN)
    # Wait for the result to load
    time.sleep(3)
    driver.implicitly_wait(10)
    # Find the country name of the website location from the result
    # Failing here
    html = driver.page_source
    # Write the HTML source to a file
    with open('page.html', 'w') as f:
        f.write(html)
    with open('page.html', 'r') as f:
        lines = f.readlines()
        locationLine = lines[282]
        pattern = r'<div class=".*?">(.*?)</div>'
        match = re.search(pattern, locationLine)
        location = match.group(1)
        print(location)
    os.remove('page.html')
    # Close the browser session
    driver.quit()
    return location

# Sea Cable Factor
def SeaCableComponent(location):
    CableDistance = -1
    CarbonIntensityFactor = 0
    df = pd.read_csv('subseacabledata.csv')
    match = df.loc[df['COUNTRY'] == location]
    if not match.empty:
        # print(match.iloc[0]['DISTANCE OF CABLE'])
        CableDistance = float(match.iloc[0]['DISTANCE OF CABLE'])
        # print(match.iloc[0]['CARBON INTENSITY FACTOR'])
        CarbonIntensityFactor = float(match.iloc[0]['CARBON INTENSITY FACTOR'])
    del df
    # print(CarbonIntensityFactor)
    return CableDistance, CarbonIntensityFactor

# Formulae component
def formulaeApplicator(PageTransferSize, CableDistance, CarbonIntensityFactor):
    CarbonEmission = (PageTransferSize * CableDistance * CarbonIntensityFactor) * 2
    EnergyConsumptionInkWh = (PageTransferSize * 1.8)/100
    result = "--------------------------------------------------------------------------------------------------------------------\n"
    x = result
    result = result + "SustainWeb's Estimates for your website:\n"
    if CarbonEmission == 0:
        result = result + "\n" + "Location of Datacenter of Website Unknown. Therefore, carbon emission related to Underlying Sea Cable can not be estimated. \n"
    else:
        result1 = "Carbon Emission per page views: " + str(CarbonEmission/1000) + " g" + "\n"
        result2 = "Carbon Emission per 1000 views: " + str(500*CarbonEmission + 5000*CarbonEmission/CableDistance) + " g" + "\n"
        result = result + result1 + result2 
    result = result + x + "Based on Constants provided by ABA:\n"
    result1 = "Energy consumption per page view (kWh): " + str(EnergyConsumptionInkWh) + "\n"
    result2 = "CO2 per page view from standard grid energy (kg): " + str((EnergyConsumptionInkWh*475)/1000) + "\n"
    result = result + result1 + result2
    result1 = "Renewable hosting usage estimates: \n"
    result2 = "CO2 per page view with 100% renewable hosting (kg): " + str(((EnergyConsumptionInkWh*0.407)*33.4)/1000+((EnergyConsumptionInkWh*0.593)*449)/1000)
    result = result + result1 + result2 + "\n" + x
    return result

# Flask App
app = Flask(__name__)
@app.route('/')
def hello_run():
    return "SustainWebAPI - By Anmol Virdi, Nandini Jaryal (NITJ)"
@app.route('/process', methods=['POST'])
def process():
    text = request.form['text']
    # Results from Component1: Tag/Page analyzer
    Content = metricsCalculator(text)

    # Fetching the Page transfer Size
    Content = Content.rsplit('\n', 1)
    PageTransferSize = float(Content[-1]) #PAGE TRANSFER SIZE
    # print(PageTransferSize)
    Content = Content[0]
    # Fetching Cable distance and Carbon Intensity Factor
    location = SiteLocatorComponent(text.split('//')[1])
    # Adding Sea Cable Factor
    CableDistance, CarbonIntensityFactor = SeaCableComponent(location) #CABLE DISTANCE, #CABLE CARBON INTENSITY FACTOR
    # print(CarbonIntensityFactor)
    
    UpdatedContent = Content + "\n\n" + formulaeApplicator(PageTransferSize, CableDistance, CarbonIntensityFactor)
    # release memory
    gc.collect
    return UpdatedContent

app.run(host='0.0.0.0', port=5000, debug=True)