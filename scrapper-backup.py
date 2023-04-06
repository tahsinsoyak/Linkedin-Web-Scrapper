from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import json

path = "venv/chromedriver.exe"
driver = webdriver.Chrome(path)

def login():
    login = open('login.txt') #fake account
    line = login.readlines()

    email = line[0]#ilk kısım mail
    password = line[1]#ikinci kısım şifre

    #giş ve ve yazma arasında bekletiyoruz
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
    #giriş yapıldı 

# Return all profiles urls of M&A employees of a certain company
def getProfileURLs(companyName):
    time.sleep(1)
    driver.get("https://www.linkedin.com/company/" + companyName + "/people/?keywords=M%26A%2CMergers%2CAcquisitions")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    source = BeautifulSoup(driver.page_source)
    time.sleep(3)

    visibleEmployeesList = []
    visibleEmployees = source.find_all('a', class_='app-aware-link')
    for profile in visibleEmployees:
        if profile.get('href').split('/')[3] ==  'in':
            visibleEmployeesList.append(profile.get('href'))

    invisibleEmployeeList = []
    invisibleEmployees = source.find_all('div', class_='artdeco-entity-lockup artdeco-entity-lockup--stacked-center artdeco-entity-lockup--size-7 ember-view')
    for invisibleguy in invisibleEmployees:
        time.sleep(3)
        title = invisibleguy.findNext('div', class_='lt-line-clamp lt-line-clamp--multi-line ember-view').strip('\n').strip('  ')
        invisibleEmployeeList.append(title)
        time.sleep(3)
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
    return (visibleEmployeesList[5:], invisibleEmployeeList)

# Testing spreadsheet of urls
# profilesToSearch = pd.DataFrame(columns=["ProfileID", "Title", "ProfilePicLink"])
# company = 'apple'
# searchable = getProfileURLs(company)
#
# for profileId in searchable[0]:
#     profilesToSearch.loc[len(profilesToSearch.index)] = [profileId, "", ""]
# for i in range(0, len(searchable[1]), 2):
#     profilesToSearch.loc[len(profilesToSearch.index)] = ["", searchable[1][i], searchable[1][i+1]]

# parses a type 2 job row

def returnProfileInfo(employeeLink, companyName):
    url = employeeLink
    driver.get(url)
    time.sleep(2)
    source = BeautifulSoup(driver.page_source, "html.parser")
    time.sleep(2)
    profile = []
    profile.append(companyName)
    info = source.find('div', class_='mt2 relative')
    time.sleep(2)
    #Kullanıcının İsmi
    name = info.find('h1', class_='text-heading-xlarge inline t-24 v-align-middle break-words').get_text().strip()
    #Kullanıcının Title - Job
    title = info.find('div', class_='text-body-medium break-words').get_text().lstrip().strip()
    
    profile.append(name)
    profile.append(title)
    time.sleep(1)
    experiences = source.find_all('li', class_='artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column')
    print(name)
    print(title)
    for x in experiences[1:]:
        alltext = x.getText().split('\n')
        print(alltext)
        profile.append(alltext)          

    return profile


#main fonksiyonu için
if __name__ == "__main__":
    companies = ['amazon'] #, 'microsoft', 'amazon', 'tesla-motors', 'google', 'nvidia', 'berkshire-hathaway', 'meta', 'unitedhealth-group'
    login()
    employees = {}
    for company in companies:
        searchable = getProfileURLs(company)
        for employee in searchable[0]:
            employees[employee] = returnProfileInfo(employee, company)
    with open('m&a.json', 'w') as f:
        json.dump(employees, f)
    time.sleep(10)
    driver.quit()