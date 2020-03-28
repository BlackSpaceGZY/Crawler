import requests
import pandas as pd
import numpy as np
import json

# address list
places_ll = []


def geocoding(address, currentkey):
    """
    address convert lat and lng
    :param address: address
    :param currentkey: AK
    :return: places_ll
    """
    url = 'http://api.map.baidu.com/geocoding/v3/?'
    params = {
        "address": address,
        "city": '北京市',
        "output": 'json',
        "ak": currentkey,
    }
    response = requests.get(url, params=params)
    answer = response.json()
    if answer['status'] == 0:
        tmpList = answer['result']
        coordString = tmpList['location']
        coordList = [coordString['lng'], coordString['lat']]
        places_ll.append([address, float(coordList[0]), float(coordList[1])])
        print([address, float(coordList[0]), float(coordList[1])])
    else:
        return -1


def reverse_geocoding(lng, lat, currentkey):
    """
    lat and lng convert address
    :param lng: longitude
    :param lat: latitude
    :param currentkey: AK
    :return: places_ll
    """
    url = 'http://api.map.baidu.com/reverse_geocoding/v3/?'
    params = {
        "location": str(lat)+','+str(lng),
        "output": 'json',
        "ak": currentkey,
        "coordtype": "wgs84ll",
    }
    response = requests.get(url, params=params)
    answer = response.json()
    if answer['status'] == 0:
        tmpList = answer['result']
        address = tmpList['formatted_address']
        print([lng, lat, address])
        places_ll.append([address, lng, lat])
    else:
        return -1


if __name__ == '__main__':

    # 地点
    l = ['东四',	'天坛', '官园', '万寿公园', '奥体中心',	'农展馆',
        '万柳', '北部新区', '丰台花园',	'云岗',	'石景山古城', '房山', '大兴',
        '亦庄',	'通州',	'顺义',	'昌平',	'门头沟',	 '平谷',	'怀柔',
        '密云',	'延庆',	'定陵',	'八达岭',	 '密云水库',	'东高村',
        '永乐店', '榆垡',	 '琉璃河', '前门', '永定门内', 	'西直门北',
        '南三环', '东四环']
    for i in range(len(l)):
        geocoding(address=l[i], currentkey="******************")
        # reverse_geocoding(116.430431, 39.937572, currentkey="*********************")
        """
        df = pd.DataFrame(places_ll, columns=['地址', '经度', '纬度'])
        df.to_csv('data/monitoring_station.csv', index=None)
        """