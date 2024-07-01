from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import smtplib
import json

# DataAnnotation account info
data_annotation_email = "me@gmail.com"
data_annotation_password = "password"

# GMail account info
gmail = "me@gmail.com"
gmail_password = "vblu zraz lqmk itvn" # to create a Google app password, see https://support.google.com/accounts/answer/185833?hl=en

fpath = 'User/full/path/to/proj/' # crontab needs file path to be explicitly defined

def check_for_new_projects():

    # Setup Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get("https://app.dataannotation.tech/users/sign_in")

    # Login
    email = driver.find_element(By.ID, "user_email")
    password = driver.find_element(By.ID, "user_password")
    email.send_keys(data_annotation_email)
    password.send_keys(data_annotation_password)
    driver.find_element(By.NAME, "commit").click()

    time.sleep(2)
    
    driver.get("https://app.dataannotation.tech/workers/projects")
    
    projects_header = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(), 'Qualifications')]"))
    )
    projects_section = projects_header.find_element(By.XPATH, "following::div[contains(@class, 'tw-bg-white')]")

    table = WebDriverWait(projects_section, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
    )
    project_rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")
    
    prev_projects = load_previous_projects(fpath + 'projects_data.json')
    current_projects = {}
    new_projects = []

    for row in project_rows:
        project_name = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(1) a").text
        pay_rate = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(2)").text
        tasks = int(row.find_element(By.CSS_SELECTOR, "td:nth-of-type(3)").text)
        created_date = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(4)").text
        
        days_since_created = calculate_days_since_created(created_date)
        
        pay_rate_int = int(pay_rate[1:3])

        if tasks == 1:
            continue  # skip projects with only 1 task remaining – historically these are not available
        
        # unique key for each project based on its name and creation date
        project_key = f"{project_name}_{created_date}"
        current_projects[project_key] = {
            "name": project_name,
            "pay": pay_rate,
            "pay_int": pay_rate_int,
            "tasks": tasks,
            "days_since_created": days_since_created
        }
        
        # check if this project is new
        if project_key not in prev_projects:
            new_projects.append(current_projects[project_key])    
        
    # sort all_projects from newest to oldest
    all_projects = list(current_projects.values())
    all_projects.sort(key = lambda x: x['days_since_created'])
    
    # sort new_projects by pay
    new_projects.sort(key = lambda x: x['pay'], reverse=True)

    # send an email if new projects are found
    if new_projects:
        teaser = ', '.join([f"\"{str(p['name'][:6]).strip()}..\" (${p['pay_int']}/h)" for p in new_projects])
        email_body = '\n'.join([f"\"{p['name']}\", {p['pay']}, {p['tasks']} tasks, created {p['days_since_created']} days ago" for p in all_projects])
        send_email(teaser, email_body)

    # update projects file
    save_current_projects(fpath + 'projects_data.json', current_projects)

    driver.quit()
    
def send_email(teaser, body):
    body_with_link = "https://app.dataannotation.tech/workers/projects\n\n" + body
    msg = MIMEText(body_with_link)
    msg['Subject'] = '[DataAnnotation Proj]: ' + teaser
    msg['From'] = gmail
    msg['To'] = gmail

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail, gmail_password)
        server.sendmail(gmail,gmail,msg.as_string())
        server.close()
    except:
        print("failed to send mail")
        
def load_previous_projects(filepath):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_current_projects(filepath, projects):
    with open(filepath, 'w') as file:
        json.dump(projects, file)
        
def calculate_days_since_created(created_date_str):
    created_date = datetime.strptime(created_date_str, "%b %d")
    now = datetime.now()
    created_date = created_date.replace(year=now.year)
    if created_date > now:
        created_date = created_date.replace(year=now.year - 1)
    days_since_created = (now - created_date).days
    return days_since_created

check_for_new_projects()