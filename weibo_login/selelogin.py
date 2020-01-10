from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
import time,requests,base64,json
from PIL import Image
from json.decoder import JSONDecodeError



class WeiboLogin():

    def __init__(self,weibo_username,weibo_password,ali_appcode,chrome_driver_path):
        ## super().__init__()(self):
        '''
        weibo_username,weibo_password,ali_appcode,chrome_driver_path
        微博用户名,密码,阿里云识别号,chrome_driver路径
        识别号申请地址：https://market.aliyun.com/products/57124001/cmapi027426.html?spm=5176.2020520132.101.2.75ef7218vDrZVw#sku=yuncode2142600000
        '''
        # 配置chrome驱动
        self.chrome_driver = chrome_driver_path
        self.driver = webdriver.Chrome(executable_path=self.chrome_driver)
        
        self.driver.implicitly_wait(5)
        self.verificationErrors = []
        self.accept_next_alert = True


        ##微博用户名密码

        self.username = weibo_username
        self.password = weibo_password

        ##阿里云识别号
        # 识别号申请地址：https://market.aliyun.com/products/57124001/cmapi027426.html?spm=5176.2020520132.101.2.75ef7218vDrZVw#sku=yuncode2142600000
        self.appcode = ali_appcode





    def login(self):
        '''
        登录
        '''
        driver = self.driver
        wait=WebDriverWait(driver,30)
        driver.set_window_size(1489,880)
        driver.get("https://www.weibo.com/")
        time.sleep(2)

        if 'home' in driver.current_url:
            print('该账号已经登录成功')
            cookies = driver.get_cookies()
            
            print('-------------------------------------------------success-------------------------------------------------')
            
            ## 存到cookies中
            cookie = [item["name"] + "=" + item["value"] for item in cookies]
            cookie_str = '; '.join(item for item in cookie)
            driver.quit()
            return cookie_str

        wait.until(EC.presence_of_element_located((By.XPATH,"//*[@id='loginname']")))
        time.sleep(0.5)
        ## 输入用户名密码
        print('正在输入输入用户名密码')
        driver.find_element_by_xpath(u"//*[@id='loginname']").click()
        driver.find_element_by_xpath("//*[@id='loginname']").clear()
        driver.find_element_by_xpath("//*[@id='loginname']").send_keys(self.username)


        driver.find_element_by_xpath(u"//*[@id='pl_login_form']/div/div[3]/div[2]/div/input").click()
        driver.find_element_by_xpath("//*[@id='pl_login_form']/div/div[3]/div[2]/div/input").clear()
        driver.find_element_by_xpath("//*[@id='pl_login_form']/div/div[3]/div[2]/div/input").send_keys(self.password)
        driver.find_element_by_xpath(u"//*[@id='pl_login_form']/div/div[3]/div[6]/a").click()
        time.sleep(1.5)

        ## 验证码识别阶段
        

        while 'home' not in driver.current_url:
            print('检测到有验证码,正在调用人工智能识别')
            # 截取图像
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#pl_login_form > div > div:nth-child(3) > div.info_list.verify.clearfix > a > img')))
            driver.save_screenshot('printscreen.png')
            # 定位截取验证码
            imgelement = driver.find_element_by_css_selector('#pl_login_form > div > div:nth-child(3) > div.info_list.verify.clearfix > a > img')
            location = imgelement.location
            size = imgelement.size
            rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),int(location['y'] + size['height'])) 

            i = Image.open("printscreen.png")  # 打开截图
            frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
            frame4=frame4.convert('RGB')
            frame4.save('save.jpg')

            # 储存验证码图像
            with open('save.jpg','rb') as f:
                imgbytes = f.read()


            ## 调用阿里云API

            # 转换base64编码
            imgbase64 = base64.b64encode(imgbytes)

            # 上传
            url = 'http://api.3023data.com/ocr/captcha'

            headers = {'key':self.appcode}

            content = {
                'image':imgbase64,
                'length':'5',
                'type':'1001'
            }
            rep = requests.post(url, data=content,headers=headers)
            # 返回checkcode
            try:
                checkcode =  str(json.loads(rep.content).get('data').get('captcha'))
            except JSONDecodeError:
                print('请检查余额是否充足或CODE是否正确')
                checkcode = str('401')
            # 填入checkcode
            driver.find_element_by_name("verifycode").send_keys(checkcode) 
            
           

            ## 登录
            driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
            
            time.sleep(4)
        
        ## 登陆成功后拿到cookies
        cookies = driver.get_cookies()
        
        print('-------------------------------------------------success-------------------------------------------------')
        
        ## 存到cookies中
        cookie = [item["name"] + "=" + item["value"] for item in cookies]
        cookie_str = '; '.join(item for item in cookie)
        driver.quit()
        return cookie_str
    
            

def login(weibo_username,weibo_password,ali_appcode='****',chrome_driver_path=r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'):
    print('正在调用一键登录功能，祝您登录愉快！from go north')
    return WeiboLogin(weibo_username,weibo_password,ali_appcode,chrome_driver_path).login()
