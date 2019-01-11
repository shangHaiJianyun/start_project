# -*- coding:utf-8 -*-

from flask import request, jsonify

from api.common_func.area import AreaM, AreaRateM
from api.modules.map import map_blu


@map_blu.route('/get_rate', methods=['POST'])
def get_rate():
    # 获取指定坐标后根据中心点坐标确定其所属的区域及价格系数
    # lng:经度  lat:纬度
    location = request.json.get('location')
    # 从数据库中提取数据
    for j in AreaM().list_all():
        lng = location['lng']
        lat = location['lat']
        # 获取该区域的区域坐标
        i = j.locations
        # 判断指定坐标属于哪个区域
        if (i['lt']['lng'] <= lng <= i['rt']['lng']) and (i['rd']['lat'] <= lat <= i['rt']['lat']):
            rate = AreaRateM().get(j.rate_id)
            # 根据需求返回该坐标所属的价格系数
            data = {
                'rate_name': rate['name'],
                'rate_level': rate['rate_level']
            }
            return jsonify(data)

    return jsonify({'error': 'please input right axis'})