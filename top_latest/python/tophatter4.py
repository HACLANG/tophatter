# -*- coding: utf-8 -*-
import random
import re
import string

import selenium

__author__ = 'bobby'

from selenium import webdriver
import time
import pymysql
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC

# 连接数据库
connect = pymysql.Connect(host='localhost', port=3306, user='root', passwd='0123456789', db='tophatter',
                          charset='utf8')
# 获取游标
cursor = connect.cursor()


def mysql_get_floor_price(str_product_image):
    # 查询数据
    try:
        sql = "select floor_price from auction_setting where auction_id='" + str_product_image + "'"
        cursor.execute(sql)
        floor_price = cursor.fetchone()
        # print(floor_price)
        floor_price1 = str(floor_price).replace("'", "").replace("(", "").replace(")", "").replace(",", "")
        # print(floor_price1)
    except Exception as e:
        connect.rollback()  # 事务回滚
        # print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        # print('事务处理成功', cursor.rowcount)
    return floor_price1


def mysql_set_email_get_auction(mysql_data):
    # 插入数据
    sql = "INSERT INTO email_get_auction (`auction_id`, `email_account`, `get_price`, `execution_status`) VALUES ('%s','%s','%s','%s')"
    try:
        cursor.execute(sql % mysql_data)
        connect.commit()
        print('成功插入', cursor.rowcount, '条数据')
    except Exception as e:
        connect.rollback()  # 事务回滚
        print('事务处理失败', e)
    else:
        connect.commit()  # 事务提交
        # print('事务处理成功', cursor.rowcount)
    pass


# 一直等待某元素可见，默认超时10秒
def is_visible(locator, timeout=20):
    try:
        ui.WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
        return True
    except TimeoutException:
        return False


def mysql_get_auction_id() -> list:
    # 查询数据
    try:
        sql = "select auction_id from auction_setting"
        cursor.execute(sql)
        amazon_title_list = []
        # 获取所有结果
        results = cursor.fetchall()
        # 去除小括号
        for (r,) in results:
            amazon_title_list.append(r)

        # print(str(amazon_title_list))
        # print('共查找出', cursor.rowcount, '条数据')
    except Exception as e:
        connect.rollback()  # 事务回滚
    else:
        connect.commit()  # 事务提交
    return amazon_title_list


#
# # 设置chromedriver不加载图片
# chrome_opt = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images": 2}
# chrome_opt.add_experimental_option("prefs", prefs)
# browser = webdriver.Chrome(executable_path="C:/amazon_python/chromedriver_win32/chromedriver.exe",
#                            chrome_options=chrome_opt)


mysql_get_auction_id = mysql_get_auction_id()


def index_button(product_image, div_index, floor_price):
    try:
        div_index = str(int(div_index) + 1)
        # try:
        xpath_str = '//*[@id="slot-group"]/div[' + div_index + ']/div/div/div/div[2]/button/div[1]/div/div[1]'
        browser.execute_script("arguments[0].scrollIntoView();", browser.find_element_by_xpath(xpath_str))
        time.sleep(2)
        web_get_price_now = str(browser.find_element_by_xpath(xpath_str).text)
        print("web_get_price_now+++" + web_get_price_now)
        print("product_image+++" + product_image)
        web_get_price_now = browser.find_element_by_xpath(xpath_str).text
        print("原始button：" + str(web_get_price_now))
        web_get_price_now = browser.find_element_by_xpath(xpath_str).text.replace("BID $", "").replace(
            "SOLD", "").replace("NEXT", "")
        print("提取处理后_价格为：" + str(web_get_price_now))

        if web_get_price_now != "" and floor_price != "":
            try:
                while int(floor_price) > int(web_get_price_now):
                    # if browser.find_element_by_class_name("modal-ribbon").is_displayed():
                    #     print("出现遮罩层")
                    #     browser.find_element_by_class_name("modal-ribbon").click()
                    print("小于设定售价，准备点击")
                    time.sleep(5)
                    xpath_button = '//*[@id="slot-group"]/div[' + div_index + ']/div/div/div/div[2]/button'
                    # browser.find_element_by_xpath(xpath_button).click()
                    browser.find_element_by_xpath(xpath_button).send_keys(selenium.webdriver.common.keys.Keys.SPACE)
                    print("完成点击")
                    print("完成点击，任务账号为:" + str(get_email) + "产品拍卖id为：" + str(product_image))
                    time.sleep(3)
                    web_get_title_status = str(browser.find_element_by_xpath(xpath_str).text)
                    print("3秒后的状态：" + web_get_title_status)
                    if "WINNING" in web_get_title_status:
                        print("完成点击，目前状态为：" + str(web_get_title_status) + " ———任务账号为:" + str(
                            get_email) + "产品拍卖id为：" + str(product_image))
                        execution_status = "已点击"
                        mysql_data = (
                            product_image, get_email, web_get_price_now, execution_status
                        )
                        mysql_set_email_get_auction(mysql_data)

                    web_get_title_status = str(browser.find_element_by_xpath(xpath_str).text)
                    while "WINNING" in web_get_title_status:
                        web_get_title_status = str(browser.find_element_by_xpath(xpath_str).text)
                        print("循环等待1秒")
                        time.sleep(1)
                    web_get_title_status = str(browser.find_element_by_xpath(xpath_str).text)
                    if "YOU" in web_get_title_status:
                        print("目前状态为：抢得拍卖!赢了!赢了! ———任务账号为:" + get_email + "成功拍到产品id为：" + product_image)
                        mysql_data = (
                            product_image, get_email, web_get_price_now, "已拍下"
                        )
                        mysql_set_email_get_auction(mysql_data)
                        browser.close()
                        browser.quit()
                        return

                    if "BID" in web_get_title_status:
                        print("目前状态为：被抢拍 ———任务账号为:" + get_email + "产品拍卖id为：" + product_image)
                        mysql_data = (
                            product_image, get_email, web_get_price_now, "已点击被抢拍"
                        )
                        mysql_set_email_get_auction(mysql_data)

                        while "OUT" in web_get_title_status:
                            web_get_title_status = str(browser.find_element_by_xpath(xpath_str).text)
                            print("循环等待1秒")
                            time.sleep(1)

                        web_get_price_now1 = browser.find_element_by_xpath(xpath_str).text
                        print("age:原始button：" + str(web_get_price_now1))
                        web_get_price_now1 = browser.find_element_by_xpath(xpath_str).text.replace(
                            "BID $", "").replace(
                            "SOLD", "").replace("NEXT", "")
                        print("age:提取处理后_价格为：" + str(web_get_price_now1))
                        if web_get_price_now1 != "" and floor_price != "":
                            web_get_price_now = web_get_price_now1

            except Exception as e:
                print("抛出异常1")
                browser.close()
                browser.quit()
                return
    except Exception as e:
        print("抛出异常2")
        browser.close()
        browser.quit()
        return

    print("完成一个id任务")
    # browser.close()
    # browser.quit()
    return


if __name__ == "__main__":
    while 1 == 1:
        try:
            try:
                try:
                    #设置chromedriver不加载图片
                    chrome_opt = webdriver.ChromeOptions()
                    prefs = {"profile.managed_default_content_settings.images": 2}
                    chrome_opt.add_experimental_option("prefs", prefs)
                    browser = webdriver.Chrome(executable_path="C:/amazon_python/chromedriver_win32/chromedriver.exe",chrome_options=chrome_opt)
                    # browser = webdriver.Chrome(executable_path="C:/amazon_python/chromedriver_win32/chromedriver.exe")
                    browser.get("https://tophatter.com/")
                    # lang_funtion()


                    get_email = ''.join(random.sample(string.ascii_letters + string.digits, random.randint(6, 9))) + "@mail.com"
                    # try:
                    is_visible('//*[@id="social-sign-up"]/a[3]')
                    browser.find_element_by_xpath('//*[@id="social-sign-up"]/a[3]').click()
                    is_visible('//*[@id="new_user"]/div[1]/input')
                    browser.find_element_by_xpath('//*[@id="new_user"]/div[1]/input').send_keys(get_email)
                    is_visible('//*[@id="new_user"]/div[2]/button')
                    browser.find_element_by_xpath('//*[@id="new_user"]/div[2]/button').click()
                    print("已登陆，准备爬取图片url")
                    time.sleep(3)
                except:
                    print("异常超时")
                    browser.close()
                    browser.quit()

                for i in range(3):
                    browser.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
                    time.sleep(2)

                store_info = browser.find_elements_by_xpath('//*[starts-with(@class,"slot slot-auction")]')
                product_image_list = []
                threads = []
                try:
                    for a in store_info:
                        product_image = a.find_element_by_tag_name('img').get_attribute("src")
                        product_image = str(product_image.replace("https://images.tophatter.com/", "").replace(
                            "/square.jpg?io=true&format=pjpg&auto=webp", ""))
                        product_image_list.append(product_image)
                        if product_image in mysql_get_auction_id:
                        # try:
                            # t = threading.Thread(target=index_button, args=(product_image,))
                            div_index = product_image_list.index(product_image)
                            print("匹配到图片id:" + product_image + "准备从数据库查询价格")
                            floor_price = str(mysql_get_floor_price(product_image))
                            print("div_index==="+str(div_index)+"， product_image==="+str(product_image)+"， 设定最低价为" + floor_price)
                            index_button(product_image, div_index, floor_price)
                            #并发线程
                            # threads.append(threading.Thread(target=index_button, args=(product_image, div_index, floor_price)))
                        # except:
                        #     print("Error: unable to start thread")
                except:
                    print("当前未匹配到id")
                browser.close()
                browser.quit()
                # for t in threads:
                #     t.setDaemon(False)
                #     t.start()
            except:
                browser.close()
                browser.quit()
                print("运行异常")
        except:
            print("主线程异常退出")

pass
