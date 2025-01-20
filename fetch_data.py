from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import mysql.connector
import re

# 配置数据库连接
db_config = {
    'user': 'root',
    'password': 'firefly@666',
    'host': 'localhost',
    'database': 'lottery_db',
    'charset': 'utf8mb4'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def fetch_recent_lottery_data():
    # 设置Selenium WebDriver
    service = Service('D:\PIC\chromedriver-win64\chromedriver.exe')  # 替换为你的ChromeDriver路径
    driver = webdriver.Chrome(service=service)
    driver.get('https://www.zhcw.com/kjxx/ssq/')

    # 等待页面加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[3]/div[3]/div/table/tbody/tr[1]/td[1]'))
    )

    # 获取页面内容
    page_source = driver.page_source
    tree = etree.HTML(page_source)

    data = []
    for i in range(1, 11):  # 获取近10期的数据
        draw_number_xpath = f'/html/body/div[2]/div[3]/div[3]/div/table/tbody/tr[{i}]/td[1]'
        draw_date_xpath = f'/html/body/div[2]/div[3]/div[3]/div/table/tbody/tr[{i}]/td[2]'
        red_balls_xpath = [f'/html/body/div[2]/div[3]/div[3]/div/table/tbody/tr[{i}]/td[3]/span[{j}]' for j in range(1, 7)]
        
        draw_number = tree.xpath(draw_number_xpath)[0].text.strip()
        draw_date = tree.xpath(draw_date_xpath)[0].text.strip()
        # 清理日期字符串，去掉中文字符
        draw_date = re.sub(r'[^\d-]', '', draw_date)
        red_balls = ' '.join([tree.xpath(xpath)[0].text.strip() for xpath in red_balls_xpath])
        # red_balls = ','.join([tree.xpath(xpath)[0].text.strip() for xpath in red_balls_xpath])
        
        # 假设蓝球在第4个td中
        blue_ball_xpath = f'/html/body/div[2]/div[3]/div[3]/div/table/tbody/tr[{i}]/td[4]/span[1]'
        blue_ball = tree.xpath(blue_ball_xpath)[0].text.strip()
        numbers = f"{red_balls} {blue_ball}"
        # numbers = f"红球: {red_balls} 蓝球: {blue_ball}"
        data.append((draw_number, draw_date, numbers))
    
    # 关闭浏览器
    driver.quit()
    
    return data

def store_data_in_db(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    for draw_number, draw_date, numbers in data:
        cursor.execute(
            "INSERT INTO history (draw_number, draw_date, numbers) VALUES (%s, %s, %s)",
            (draw_number, draw_date, numbers)
        )
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    recent_data = fetch_recent_lottery_data()
    store_data_in_db(recent_data)
    print("数据已成功存储到数据库。") 