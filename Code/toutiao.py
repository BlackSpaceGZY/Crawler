"""
Created on Feb 18, 2020

Crawler Toutiao

@author: Gengziyao
"""
import requests
import time
import os
import re
from hashlib import md5
from urllib.parse import urlencode
from multiprocessing.pool import Pool

def get_page(offset):
	"""
	get json of one page
	:param offset: offset between two pages
	:return: json
	"""
	params = {
		'aid': 24,
		'app_name': 'web_search',
		'offset': offset,
		'format': 'json',
		'keyword': '天气之子',
		'autoload': 'true',
		'count': 20,
		'en_qc': 1,
		'cur_tab': 1,
		'from': 'search_tab',
		'pd': 'synthesis',
		'timestamp' : int(time.time_ns() / (10**6))
	}
	headers = {
	# cookie加入重中之重
	'cookie': ('__tasessionId=q6mp1lrxu1583224640956;' 
		'csrftoken=4d4dc07f33b82883b72743f5c81537ab;' 
		's_v_web_id=verify_k7bn2ml4_15YGHeUM_iH2m_4qAg_A8Ec_UlarLgh3Pcej;' 
		'SLARDAR_WEB_ID=4177e739-d79a-44bc-b568-502f52fe45d2;' 
		'tt_scid=7nzno7juT5MPzFuVZIr2zTCJKKlx-nEheWIm47qBeDd7PRKAcGCk-XD5jpZADunmcb54;' 
		'tt_webid=6799872105451128333;' 
		'tt_webid=6799872105451128333;' 
		'ttcid=2204991f51f148848ab9d33a3b1c85a639;' 
		'WEATHER_CITY=%E5%8C%97%E4%BA%AC'),
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537/36'+
	'(KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537/36'
	}
	url = 'https://www.toutiao.com/api/search/content/?' + urlencode(params)
	try:
		res = requests.get(url, headers=headers)
		if res.status_code == 200:
			return res.json()
	except requests.ConnectionError:
		return None

def get_images(json):
	"""
	get images' url
	:param json: page's json
	:retrun: generator of image and title
	"""
	if json.get('data'):
		for item in json.get('data'):
			if item.get('title') and item.get('image_list'):
 				title = item.get('title')
 				images = item.get('image_list')
 				for image in images:
 					if "190x124" in image.get('url'):
 						image_url = re.sub('list/190x124', 'large', image.get('url'))
 					else:
 						image_url = re.sub('list', 'large', image.get('url'))
 					yield{
 					'image': image_url,
 					'title': title
 					}

def save_images(item):
	"""
	save images
	:param item: image and title
	"""
	path = 'data/tianqizhizi/' + item.get('title')
	if not os.path.exists(path):
		os.makedirs(path)
	try:
		res = requests.get(item.get('image'))
		if res.status_code == 200:
			print(item)
			file_path = '{0}/{1}.{2}'.format(path, 
				md5(res.content).hexdigest(), 'png')
			if not os.path.exists(file_path):
				with open(file_path, 'wb') as f:
					f.write(res.content)
			else:
				print('Already Download', file_path)
	except requests.ConnectionError:
		print('Falied to Save Image')


def main(offset):
	"""
	main function
	:param offset: offset between two pages
	"""
	json = get_page(offset)
	for item in get_images(json):
		save_images(item)

if __name__ == '__main__':
	pool = Pool()
	groups = [x * 20 for x in range(0, 9)]
	pool.map(main, groups)
	pool.close()
	pool.join()