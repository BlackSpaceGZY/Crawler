import time
import random
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.wait import WebDriverWait


class bilibili():
	def __init__(self, phone, password):
		"""
		初始化
		:param phone: 账号
		:param password: 密码
		"""
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('start-fullscreen')
		self.browser = webdriver.Chrome(options=chrome_options)
		self.wait = WebDriverWait(self.browser, 15)
		self.url = 'https://passport.bilibili.com/login'
		self.phone = phone
		self.password = password


	def open(self):
		"""
		打开网页，输入账号、密码，点击
		"""
		self.browser.get(self.url)
		phone = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
		password = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
		button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-login')))
		phone.send_keys(self.phone)
		password.send_keys(self.password)
		button.click()


	def get_position(self, scale):
		"""
		获取验证码位置
		:return: 验证码位置元组
		"""
		img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_slicebg.geetest_absolute')))
		location = img.location
		size = img.size
		top, bottom, left, right = location['y'] * scale, (location['y'] + size['height']) * scale,\
		 location['x'] * scale, (location['x'] + size['width']) * scale
		return (top, bottom, left, right)


	def get_screenshot(self):
	    """
	    获取网页截图
	    :return: 截图对象
	    """
	    screenshot =  self.browser.get_screenshot_as_png()
	    screenshot = Image.open(BytesIO(screenshot))
	    screenshot = screenshot.convert('RGB')
	    return screenshot


	def get_geetest_image(self):
		"""
		获取验证码图片
		:return: 图片对象
		"""
		screenshot = self.get_screenshot()
		scale = self.get_scale()
		top, bottom, left, right = self.get_position(scale)
		image = screenshot.crop((left, top, right, bottom))
		return image


	def get_scale(self):
		"""
		截取页与浏览器的宽比例
		:return: 比例
		"""
		screenshot = self.get_screenshot()
		size1 = screenshot.size
		size2 = self.browser.get_window_size()
		# 网页与截图比例，主要是宽的影响（不知道为什么）
		scale = size1[0]/size2['width']
		return scale


	def get_two_images(self):
		"""
		获得两张图片
		:return: 两个Image对象
		"""
		time.sleep(2)
		self.browser.execute_script("document.getElementsByClassName('geetest_canvas_slice geetest_absolute')[0].style.display='none'")
		image1 = self.get_geetest_image()
		self.browser.execute_script("document.getElementsByClassName('geetest_canvas_fullbg geetest_fade geetest_absolute')[0].style['display'] = 'block'")
		image2 = self.get_geetest_image()
		return image1, image2


	def is_pixel_equal(self, image1, image2, x, y):
	    """
	    判断两个像素是否相同
	    :param image1: 图片1
	    :param image2: 图片2
	    :param x: 位置x
	    :param y: 位置y
	    :return: 像素是否相同
	    """
	    # 取两个图片的像素点
	    pixel1 = image1.load()[x, y]
	    pixel2 = image2.load()[x, y]
	    threshold = 60
	    if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
	            pixel1[2] - pixel2[2]) < threshold:
	        return True
	    else:
	        return False


	def get_gap(self, image1, image2):
	    """
	    获取移动位置
	    :param image1: 带缺口图片
	    :param image2: 原图
	    :return:
	    """
	    for i in range(0, image1.size[0]):
	        for j in range(image1.size[1]):
	            if not self.is_pixel_equal(image1, image2, i, j):
	                return i
	    return 0


	def get_track(self, distance):
		"""
	    根据偏移量获取移动轨迹
	    :param distance: 偏移量
	    :return: 移动轨迹
	    """
		# 移动轨迹
		track = []
		# 当前位移
		current = 0
		# 减速阈值
		mid = distance * 4 / 5
		# 初速度
		v0 = 5
		while current < distance:
			if current < mid:
				a = 5
			else:
				a = -4
			# 间隔
			t = random.randint(3, 6) / 10
			# 移动距离
			move = v0 * t + 0.5 * t * t
			# 当前速度
			v0 = v0 + a * t
			if current + move >= distance:
				move = distance - current
			current += move
			track.append(move)
		return track


	def get_slider(self):
		"""
		获取滑块
		:return: 滑块对象
		"""
		slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
		return slider


	def move_to_gap(self, slider, track):
	    """
	    拖动滑块到缺口处
	    :param slider: 滑块
	    :param track: 轨迹
	    :return:
	    """
	    ActionChains(self.browser).click_and_hold(slider).perform()
	    time.sleep(0.02)
	    for x in track:
	        ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
	        time.sleep(0.01)
	    time.sleep(0.017)
	    ActionChains(self.browser).move_by_offset(xoffset=-1, yoffset=0).perform()
	    time.sleep(0.028)
	    ActionChains(self.browser).release().perform()


	def start(self):
		"""
		开始
		"""
		# 打开网页
		self.open()
		# 获取残缺图与原图
		image1, image2 = self.get_two_images()
		# 计算需要向右移动的距离
		distance = self.get_gap(image1, image2)
		scale = self.get_scale()
		# 转为浏览器距离
		distance = distance / scale
		# 得到每次移动的距离
		track = self.get_track(distance)
		# 获取滑块
		slider = self.get_slider()
		self.browser.execute_script("document.getElementsByClassName('geetest_canvas_slice geetest_absolute')[0].style.display='block'")
		# 移动滑块
		self.move_to_gap(slider, track)
		time.sleep(3)
		self.browser.close()

b = bilibili(1234567, '*******')
b.start()
