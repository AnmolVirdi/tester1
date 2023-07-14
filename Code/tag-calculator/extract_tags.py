import requests
import cssutils
import platform
import logging
import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup


# Get number of arguments
num_args = len(sys.argv)
if (num_args<=1):
    print("ERROR : No arguments passed!")
    sys.exit()
elif (num_args!=2):
    print("ERROR : Invalid number of arguments passed!")
    sys.exit()

# input the site name here
# 'https://www.thepythoncode.com/article/extract-web-page-script-and-css-files-in-python'
site = sys.argv[1]

# code for selecting suitable user agent for linux, windows, macOS
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
img_src_urls = [img['src'] for img in img_tags]
print(f"Total {len(img_tags)} Image tags Found!")

# 2) finding total no. of empty tags
empty_tags = soup.findAll(lambda tag: tag.find(True) is None and (tag.string is None or tag.string.strip()=="")) 
print(f"Total {len(empty_tags)} Empty tags Found!")
# for specificity use (example find empty <p> tags) -> empty_tags = soup.findAll(lambda tag: tag.name == 'p' and tag.find(True) is None and (tag.string is None or tag.string.strip()=="")) 

# 3) finding no. of script tags
script_tags = soup.find_all("script")
text_inside_script_tag = script_tags[0].string
print(f"Total {len(script_tags)} Script tags Found!")

# 4) finding no. of style sheet linked
style_sheets = []
link_tags_with_style_sheets = []

link_tags = soup.find_all("link")
for link in link_tags:
    if "stylesheet" in link.get("rel", []):
        link_tags_with_style_sheets.append(link)
        style_sheets.append(link["href"])

print(f"Total {len(style_sheets)} Linked Style sheets Found!")

# 6) Get total size of page in MB
website = urlopen(site)
metadata = website.info()
size = len(website.read())
print('Total File content size : {:.5f} MB'.format(int(size) / float(1 << 20)))

# 7) Total tags with empty href
anchor_tags_no_href = []
for a in soup.find_all('a', href=True):
    x = a['href']
    # if empty href found
    if x.strip()=="":
       anchor_tags_no_href.append(a)

print(f"Total {len(anchor_tags_no_href)} anchor tags Found with empty href!")


# 5) find no. of font family (iterating through CSS files)
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
print('\nPrinting CSS files with fonts used -> \n')

for index,file in enumerate(css_files):
    count = len(css_files_font_family[index])
    print(f'CSS FILE - {file} has {count} Font families')
    print(f'FONT FAMILIES - {css_files_font_family[index]}')

# Page transfer size
def get_page_transfer_size(url):
    # Send a GET request to the website URL
    response = requests.get(url)

    # Get the content size in bytes
    content_size = sys.getsizeof(response.content)
    content_size = content_size / 1000000
    return content_size

print("Total Page transfer size:")
print(str(get_page_transfer_size(site)) + " MB")