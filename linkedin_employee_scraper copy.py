from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import json

path = "pathtoyourchromedriver\chromedriver.exe"
# download the chromedriver.exe from https://chromedriver.storage.googleapis.com/index.html?path=106.0.5249.21/

driver = webdriver.Chrome(path)

# Login
def login():
    login = open('login.txt') # this is your linkedin account login, store in a seperate text file. I recommend creating a fake account so your real one dosen't get flagged or banned
    line = login.readlines()

    email = line[0]
    password = line[1]

    driver.get("https://www.linkedin.com/login")
    time.sleep(1)

    eml = driver.find_element(by=By.ID, value="username")
    eml.send_keys(email)
    time.sleep(1)
    passwd = driver.find_element(by=By.ID, value="password")
    passwd.send_keys(password)
    time.sleep(1)
    loginbutton = driver.find_element(by=By.XPATH, value="//*[@id=\"organic-div\"]/form/div[3]/button")
    loginbutton.click()
    time.sleep(3)


# Return all profiles urls of M&A employees of a certain company
def getProfileURLs(companyName):
    time.sleep(1)
    driver.get("https://www.linkedin.com/search/results/people/?geoUrn=%5B%22102424322%22%5D&keywords=nima&origin=FACETED_SEARCH&sid=-DF")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    source = BeautifulSoup(driver.page_source)

    visibleEmployeesList = []
    visibleEmployees = source.find_all('a', class_='app-aware-link')
    for profile in visibleEmployees:
        if profile.get('href').split('/')[3] ==  'in':
            visibleEmployeesList.append(profile.get('href'))

    invisibleEmployeeList = []
    invisibleEmployees = source.find_all('div', class_='artdeco-entity-lockup artdeco-entity-lockup--stacked-center artdeco-entity-lockup--size-7 ember-view')
    for invisibleguy in invisibleEmployees:
        title_element = invisibleguy.findNext('div', class_='lt-line-clamp lt-line-clamp--multi-line ember-view')
        if title_element is not None:
            title = title_element.contents[0].strip('\n').strip('  ')
        else:
            title = ''

        invisibleEmployeeList.append(title)

        # A profile can either be visible or invisible
        profilepiclink = ""
        visibleProfilepiclink = invisibleguy.find('img', class_='lazy-image ember-view')
        invisibleProfilepicLink = invisibleguy.find('img', class_='lazy-image ghost-person ember-view')
        if visibleProfilepiclink == None:
            profilepiclink = invisibleProfilepicLink.get('src')
        else:
            profilepiclink = visibleProfilepiclink.get('src')

        if profilepiclink not in invisibleEmployees:
            invisibleEmployeeList.append(profilepiclink)
    return (visibleEmployeesList[1:], invisibleEmployeeList)


# returns linkedin profile information
def returnProfileInfo(employeeLink):
    url = employeeLink
    driver.get(url)
    time.sleep(3)
    source = BeautifulSoup(driver.page_source, "html.parser")
    time.sleep(1)
    # info = source.find('div', class_='mt2 relative')
    # name = info.find('h1', class_='text-heading-xlarge inline t-24 v-align-middle break-words').get_text().strip()
    # title = info.find('div', class_='text-body-medium break-words').get_text().lstrip().strip()
    # print(name)
    # print(title)
    fileq = str(source)
    with open('source.html', 'w') as f:
        f.write(fileq)
    '''
    experiences = source.find_all('li', class_='artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column')
    for x in experiences[1:]:
        alltext = x.getText().split('\n')
        startIdentifier = 0
        for e in alltext:
            if e == '' or e == ' ':
                startIdentifier+=1
            else:
                break
    '''
    print('#######################################')
    print('#######################################')
    return profile

if __name__ == "__main__":
    companies = ['microsoft'] #'apple',  'amazon', 'tesla-motors', 'google', 'nvidia', 'berkshire-hathaway', 'meta', 'unitedhealth-group']
    login()
    employees = {}
    profile = []
    for company in companies:
        searchable = getProfileURLs(company)
        for employee in searchable[0]:
            employees[employee] = returnProfileInfo(employee)
    with open('m&a5.json', 'w') as f:
        json.dump(employees, f)
    time.sleep(10)
    driver.quit()
