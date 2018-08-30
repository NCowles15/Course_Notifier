from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time 
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def time_check():
    today_str = str(datetime.datetime.today())
    today_date, today_time = today_str.split()
    today_hour, today_minute, today_second = today_time.split(':')
    weekday = datetime.datetime.today().weekday()
    if weekday == 5:
        if (int(today_hour)<8):
            return False
        else:
            return True
    elif weekday == 6:
        if (20<int(today_hour)):
            return False
        else:
            return True
    else:
        if (8<=int(today_hour)<20):
            return True
        else:
            return False
def current_time():
    today_str = str(datetime.datetime.today())
    today_date, today_time = today_str.split()
    today_hour, today_minute, today_second = today_time.split(':')
    mil_time = "{}:{} - {}".format(today_hour, today_minute, today_date)
    return mil_time
def sleep_calc():
    today_str = str(datetime.datetime.today())
    today_date, today_time = today_str.split()
    today_hour, today_minute, today_second = today_time.split(':')
    if (20<=int(today_hour)<24):
        elapsed_hr = int(today_hour)-20
        elapsed_min = int(today_minute)
        elapsed_sec = float(today_second)
        elapsed_total_sec=(elapsed_hr*60*60)+(elapsed_min*60)+elapsed_sec
        sleep_time = sleep_time = (14400-elapsed_total_sec)+28800
        return sleep_time
    elif (0<=int(today_hour)<8):
        elapsed_hr = int(today_hour)
        elapsed_min = int(today_minute)
        elapsed_sec = float(today_second)
        elapsed_total_sec=(elapsed_hr*60*60)+(elapsed_min*60)+elapsed_sec
        sleep_time = (28800-elapsed_total_sec)
        return sleep_time
def Class_Search(name,number,code,section):
    driver = webdriver.PhantomJS()
    driver.get("https://schedule.msu.edu/")
    
    TermFieldID = "MainContent_ddlTerm"
    SubjectFieldID = "MainContent_ddlSubject"
    CourseFieldID = 'MainContent_txtCourseNumber'
    SearchButtonXpath = "//input[@value='Find Courses']"
   
    TermNumber = code
    SubjectCode = name
    CourseNumber = number
    SectionStr = str(int(section)-1)
    
    TermFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(TermFieldID))
    SubjectFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(SubjectFieldID))
    CourseFieldElement =  WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(CourseFieldID))
    SearchButtonElement =  WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(SearchButtonXpath))


    for term_option in TermFieldElement.find_elements_by_tag_name('option'):
        if term_option.text.lower() == TermNumber.lower():
            term_option.click()
            break

    for subject_option in SubjectFieldElement.find_elements_by_tag_name('option'):
        if subject_option.text.split(':')[0].lower() == SubjectCode.lower():
            subject_option.click()
            break
        
    CourseFieldElement.clear()
    CourseFieldElement.send_keys(CourseNumber)
    SearchButtonElement.click()
    time.sleep(2)
    
    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')
    found_enrolled = soup.find(attrs={"data-title": "Enrolled"})
    found_limit = soup.find(attrs={"data-title": "Enrollment Limit"})
    found_enrolled_text = found_enrolled.text
    found_limit_text = found_limit.text
    
    driver.quit()
    
    return found_enrolled_text, found_limit_text
        
def Class_Finder(name,number,code,section,mail):    
    driver = webdriver.PhantomJS()
    driver.get("https://schedule.msu.edu/")
    while time_check() == True:
        TermFieldXpath = "//select[@id='MainContent_ddlTerm']"
        SubjectFieldID = "MainContent_ddlSubject"
        CourseFieldID = 'MainContent_txtCourseNumber'
        SearchButtonXpath = "//input[@value='Find Courses']"
       
        TermNumber = code
        SubjectCode = name
        CourseNumber = number
        SectionStr = str(int(section)-1)
        
        TermFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(TermFieldXpath))
        SubjectFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(SubjectFieldID))
        CourseFieldElement =  WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(CourseFieldID))
        SearchButtonElement =  WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(SearchButtonXpath))


        for term_option in TermFieldElement.find_elements_by_tag_name('option'):
            if term_option.text.lower() == TermNumber.lower():
                term_option.click()
                break

        for subject_option in SubjectFieldElement.find_elements_by_tag_name('option'):
            if subject_option.text.split(':')[0].lower() == SubjectCode.lower():
                subject_option.click()
                break
            
        CourseFieldElement.clear()
        CourseFieldElement.send_keys(CourseNumber)
        SearchButtonElement.click()
        
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser') 
        found_enrolled = soup.find(attrs={"data-title": "Enrolled"})
        found_limit = soup.find(attrs={"data-title": "Enrollment Limit"})
        found_enrolled_text = found_enrolled.text
        found_limit_text = found_limit.text
        
        free = class_checker(found_enrolled_text,found_limit_text)
        if free == True:
            found_time = current_time()
            print("Class opening found at",found_time)
            for i in range(5):
                notifier(found_enrolled_text,found_limit_text,name,number,code,mail)
                time.sleep(15)
            driver.quit()
            break
        else:
            print("{} {} is currently at {}/{} as of {}, waiting...".format(SubjectCode, CourseNumber, found_enrolled_text, found_limit_text, current_time()))
            time.sleep(300)
            print("Refreshing Class Info")
            driver.refresh()
            continue
    driver.quit()
            
def class_checker(current,maxim):
    if int(current)<int(maxim):
        return True
    else:
        return False
def notifier(entered,total,name,number,code,to_mail):
        fromaddr= "example@gmail.com"
        toaddr = to_mail
        msg = MIMEMultipart()
        msg['Subject'] = name+" "+number+" Notification"
        msg['From'] = fromaddr
        msg['To'] = toaddr
        body = "There are currently "+entered+" out of "+total+" enrolled in "+name+" "+number+"."
        msg.attach(MIMEText(body,'plain'))
        
        server = smtplib.SMTP("smtp.gmail.com", "587")
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("example@gmail.com", "password")
        
        server.sendmail(fromaddr,toaddr,msg.as_string())
        server.quit()


def main():
    start_time = current_time()
    print("Program Started at",start_time)
    course_name = input("Input Course Code (CSE): ")
    course_number = input("Input Course Number (232): ")
    course_section = input("Input Course Section (1): ")
    session_code = input("Input Session Code ('spring 2018'): ")
    enrolled, limit = Class_Search(course_name,course_number,session_code,course_section)
    print("There are currently "+enrolled+" out of "+limit+" enrolled in "+course_name+" "+course_number+".")
    cont = input("Would you like notifications when available? (y/n): ")
    if cont.lower() == 'y':
        email = input("Input email address for notifications ('example@gmail.com'): ")
        try:
            while True:
                if time_check() == True:
                    print("Scanning Classes")
                    Class_Finder(course_name,course_number,session_code,course_section,email)
                elif time_check() != True:
                    print("Sleeping")
                    timer = sleep_calc()
                    time.sleep(timer)
        except KeyboardInterrupt:
            print("Successfully Interrupted")
    else:
        print("Invalid Input")
if __name__ == "__main__":
    main()
                
