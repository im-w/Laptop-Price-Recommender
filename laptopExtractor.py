# .__                 __                  ___________         __                        __                
# |  | _____  _______/  |_  ____ ______   \_   _____/__  ____/  |_____________    _____/  |_  ___________ 
# |  | \__  \ \____ \   __\/  _ \\____ \   |    __)_\  \/  /\   __\_  __ \__  \ _/ ___\   __\/  _ \_  __ \
# |  |__/ __ \|  |_> >  | (  <_> )  |_> >  |        \>    <  |  |  |  | \// __ \\  \___|  | (  <_> )  | \/
# |____(____  /   __/|__|  \____/|   __/  /_______  /__/\_ \ |__|  |__|  (____  /\___  >__|  \____/|__|   
#           \/|__|               |__|             \/      \/                  \/     \/                   

#This program works on digikala and extract information of laptops you can see on their website


# Libraries #

from requests import get
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from time import sleep
import datetime

# Functions #

def create_main_page_url(page_num):
    return 'https://www.digikala.com/search/notebook-netbook-ultrabook/product-list/?sort=7&page=' + str(page_num)

def get_laptop_urls(url, laptop_urls_list, delay_seconds):
    # find all product links in the main page url -search page-
    
    driver = webdriver.Edge()
    #driver.minimize_window()
    driver.get(url)
    sleep(delay_seconds)

    elements = driver.find_elements(By.TAG_NAME, 'a')


    for element in elements:
        laptop_url = element.get_attribute('href')
        if re.search(r'(https://www.digikala.com/product/.+?/.+?/)',laptop_url):
            laptop_urls_list.append(laptop_url)
    driver.close()

def value_corrector(values_list):
    # make a better database for ML purpose
    
    # memory -> values_list[2][1]
    if values_list[2][1]=='چهار گیگابایت':
        values_list[2][1] = 4
    elif values_list[2][1]=='هشت گیگابایت':
        values_list[2][1] = 8
    else:
        matches = re.findall(r'(\d+)', values_list[2][1])
        values_list[2][1] = int(matches[0])
    
    # storage -> values_list[3][1]
    storage = 0
    try:
        matches = re.findall(r'(\d+)', values_list[3][1])
        storage += int(matches[0])
    except:
        pass
    if 'یک ترابایت' in values_list[3][1]:
        storage += 1024
    if 'دو ترابایت' in values_list[3][1]:
        storage += 2048
    values_list[3][1] = storage
    
    
    # display -> values_list[5][1]
    matches = re.findall(r'(\d+).+?(\d+)', values_list[5][1])
    if int(matches[0][0]) >= int(matches[0][1]):
        values_list[5][1] = matches[0][0] + 'x' + matches[0][1]
    else:
        values_list[5][1] = matches[0][1] + 'x' + matches[0][0]
        
    # price -> values_list[-1]
    for letter in values_list[-1]:
        if letter == '۰':
            letter = '0'
        elif letter == '۱':
            letter = '1'
        elif letter == '۲':
            letter = '2'
        elif letter == '۳':
            letter = '3'
        elif letter == '۴':
            letter = '4'
        elif letter == '۵':
            letter = '5'
        elif letter == '۶':
            letter = '6'
        elif letter == '۷':
            letter = '7'
        elif letter == '۸':
            letter = '8'
        elif letter == '۹':
            letter = '9'
    values_list[-1] = int(values_list[-1])
    
    

def get_laptop_info(url , output_file_name , delay_seconds):
    # find info in url and write info in database if url wasn't laptop page cant find what information needs and print error message 
    
    driver = webdriver.Edge()
    #driver.minimize_window()
    driver.get(url)
    sleep(delay_seconds)
    values_list = list()

    elements = driver.find_elements(By.TAG_NAME, 'h1')
    values_list.append(elements[0].text)

    elements = driver.find_elements(By.TAG_NAME, 'li')


    for element in elements:
        element_text = element.text.strip()
        if element_text != '':
            element_text = element_text.replace('\u200c' , ' ').split('\n')
            values_list.append(element_text)
    values_list.append(url)
    
    element = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="price-no-discount"]')
    values_list.append(element.text.replace(',' , ''))
    
    value_corrector(values_list)

    try:
        with open(output_file_name, 'a', encoding='utf-8') as file:
            file.write(f'{values_list[0]},{values_list[1][1]},{values_list[2][1]},{values_list[3][1]},{values_list[4][1]},{values_list[5][1]},{values_list[-2]},{values_list[-1]}\n')
        print('\n>>> One row added!\n')
    except:
        print(f'\n>>> The url is not correct!\n>>> url : {url}\n')
        
    driver.close()
    
def get_page_num_start_end():
    page_num_start = int(input(">>> You want to start extraction from page : "))
    page_num_end = int(input(">>> and stop extraction in end of page : "))
    return (page_num_start , page_num_end)
    
def write_log(log_text):
    current_time = datetime.datetime.now()
    result_log_text = log_text + ' ' + current_time.strftime(r'<%Y-%m-%d %H:%M>')
    print(result_log_text)
    with open('logs.txt', 'a') as f:
        f.write(result_log_text + '\n')

# Main Function #

def main():
    # Defines
    laptop_urls_list = list()
    output_file_name = 'laptopInfoDB.csv'
    delay = 5
    (page_num_start , page_num_end) = get_page_num_start_end()

    # processes
    for page_num in range(page_num_start , page_num_end+1):
        write_log(">>> Program running on page: %s Start!" %page_num)
        laptop_urls_list = list()
        try:
            get_laptop_urls(create_main_page_url(3), laptop_urls_list, delay)
            for url in laptop_urls_list:
                try:
                    get_laptop_info(url , output_file_name , delay)
                except:
                    write_log(">>> Problem in running function 'get_laptop_info'")
                    write_log(">>> url: %s" %url)


                    continue
        except:
            write_log(">>> Problem in running function 'get_laptop_urls'")
            write_log(">>> page_num: %s" %page_num)
            continue
        write_log(">>> Program running on page: %s End!" %page_num)
main()