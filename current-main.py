from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import json

path = "venv/chromedriver.exe"
driver = webdriver.Chrome(path)
# Login
def login():
    login = open('login.txt') #fake account
    line = login.readlines()

    email = line[0]#ilk kısım mail
    password = line[1]#ikinci kısım şifre

    #giş ve ve yazma arasında bekletiyoruz
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    eml = driver.find_element(by=By.ID, value="username")
    eml.send_keys(email)
    time.sleep(2)
    passwd = driver.find_element(by=By.ID, value="password")
    passwd.send_keys(password)
    time.sleep(2)
    loginbutton = driver.find_element(by=By.XPATH, value="//*[@id=\"organic-div\"]/form/div[3]/button")
    loginbutton.click()
    time.sleep(3)
    #giriş yapıldı 

# Return all profiles urls of M&A employees of a certain company
def getProfileURLs(name, city, job, language, skill):
    page_num = 1
    name = name.replace(" ", "%20")
    city = city.replace(" ", "%20")
    job = job.replace(" ", "%20")
    language = language.replace(" ", "%20")
    skill = skill.replace(" ", "%20")
    driver.get(f"https://www.linkedin.com/search/results/people/?keywords={name}%20{job}%20{city}%20{language}%20{skill}&origin=CLUSTER_EXPANSION&sid=jQt&page={page_num}")
    time.sleep(3)
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
    return (visibleEmployeesList, invisibleEmployeeList)
# returns linkedin profile information
def returnProfileInfo(employeeLink, companyName):
    time.sleep(1)
    url = employeeLink
    
    driver.get(url)
    time.sleep(7)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    source = BeautifulSoup(driver.page_source, "html.parser")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    profile = []
    profile.append(companyName)
    info = source.find('div', class_='mt2 relative')
    print(info)  # Debugging statement
    if info is None:
        print('Info is None')  # Debugging statement
        return None
    time.sleep(2)
    name = info.find('h1', class_='text-heading-xlarge inline t-24 v-align-middle break-words').get_text().strip()
    title = info.find('div', class_='text-body-medium break-words').get_text().lstrip().strip()
    profile.append(name)
    profile.append(title)
    time.sleep(2)
    experiences = source.find_all('li', class_='artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column')
    time.sleep(2)
    morebtn = driver.find_element(by=By.XPATH, value="//body/div[5]/div[3]/div[1]/div[1]/div[2]/div[1]/div[1]/main[1]/section[1]/div[2]/div[3]/div[1]/div[1]/button[1]/span[1]")
    morebtn.click()
    savepdf = driver.find_element(by=By.XPATH,value="//body/div[5]/div[3]/div[1]/div[1]/div[2]/div[1]/div[1]/main[1]/section[1]/div[2]/div[3]/div[1]/div[1]/button[1]/span[1]")
    time.sleep(2)
    savepdf.click()
    time.sleep(2)
    for x in experiences[1:]:
        alltext = x.getText().split('\n')
        profile.append(alltext)
    return profile

if __name__ == "__main__":
    companies = ['apple'] #, 'microsoft', 'amazon', 'tesla-motors', 'google', 'nvidia', 'berkshire-hathaway', 'meta', 'unitedhealth-group'
    login()
    time.sleep(1)
    employees = {}
    em1 = ""
    for company in companies:
        time.sleep(1)
        searchable = getProfileURLs('Selçuk Akarın','','','','')
        
        for employee in searchable[0]:
            if em1 == employee:
                continue
            em1 = employee
            employees[employee] = returnProfileInfo(employee, company)
            
            time.sleep(1)
    with open('latest.json', 'w') as f:
        json.dump(employees, f)
    time.sleep(10)
    driver.quit()