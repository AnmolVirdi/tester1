from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import re
import os
# Start a new Chrome browser session
driver = webdriver.Chrome()

# Navigate to the Site24x7 website
driver.get("https://www.site24x7.com/tools/find-website-location.html")

driver.implicitly_wait(10)
# Find the input field and enter the website URL to search for
input_field = driver.find_element(By.ID, "hostName")
input_field.send_keys("nitj.ac.in")
input_field.send_keys(Keys.RETURN)

# Wait for the result to load
time.sleep(10)
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
    print(locationLine)
    pattern = r'<div class=".*?">(.*?)</div>'
    match = re.search(pattern, locationLine)
    location = match.group(1)
    print(location)

os.remove('page.html')
# Print the country name
# print("The website is located in", country)

# Close the browser session
driver.quit()
