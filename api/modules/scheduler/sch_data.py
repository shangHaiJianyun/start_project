# -*- coding: utf-8 -*-
"""
get data from php backend
save data to python backend
"""
import requests
import datetime as dt
from .sch_lib import *


def get_orders_dispatch(days=2, city="上海市"):
    """
        get paied orders
    input:
        days: 天数
    output：
        order list
    """
    access_key = 'xunjiepf'
    url = "https://banana.xunjiepf.cn/api/extend/getorderlist"
    order_status = 2
    yd = dt.datetime.today() - dt.timedelta(days=2)
    start_service_date = yd.date().isoformat()
    tm = dt.datetime.today() + dt.timedelta(days=days+1)
    end_service_date = tm.date().isoformat()
    data = {
        'access_key': access_key,
        'order_status': order_status,
        'start_service_date': start_service_date,
        'end_service_date': end_service_date
    }
    res = requests.post(
        url,
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(data)
    )
    result = res.json()['data']['data']
    if res.json()['data']['page_count'] > 1:
        page_size = res.json()['data']['total_count']
        data.update(page_size=page_size)
        res = requests.post(
            url,
            headers={
                "Content-Type": "application/json"
            },
            data=json.dumps(data)
        )
        result = res.json()['data']['data']
    return result


def save_workers_from_api(day_str, city="上海市"):
    """
        get available worker and save to database
    """

    access_key = 'xunjiepf'
    date = day_str
    results = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getworkerlist",
        params={
            'access_key': access_key,
            'city': city,
            'date': day_str
        }
    )
    page_size = results.json()['data']['total_count']

    res = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getworkerlist",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({
            'access_key': access_key,
            'page_size': page_size,
            'city': city,
            "date": date
        })
    )
    workers = res.json()['data']['data']
    #: prepare dataframe
    df = pd.DataFrame(workers)
    df = df.loc[(df.auth_state == "3") & (df.is_holiday == "1") & (
        df.service_start_time != "") & (df.service_end_time != "")]
    df = df.loc[:, ('uid', 'service_start_time',
                    'service_end_time', 'worker_type')]
    df.loc[:, 'worker_id'] = df.uid
    df.loc[:, 'w_region'] = '0'
    df.loc[:, 'city'] = city
    df.loc[:, 'w_start'] = pd.to_datetime(
        day_str + ' ' + df.service_start_time, format="%Y-%m-%d %H:%M")
    df.loc[:, 'w_end'] = pd.to_datetime(
        day_str + ' ' + df.service_end_time, format="%Y-%m-%d %H:%M")
    df.loc[:, 'w_hrs'] = (df.w_end - df.w_start)/np.timedelta64(60, 'm')
    df.loc[:, 'w_rank'] = 100
    df.loc[:, 'w_type'] = df.worker_type
    df.loc[:, 'worker_type'] = 1
    df.loc[:, 'mdt'] = 8
    df.loc[:, 'max_star_t'] = 8
    df.loc[:, 'hrs_to_assign'] = 0
    df.loc[:, 'hrs_assigned'] = 0
    df.loc[:, 'adt_hrs'] = 0
    df.loc[:, 'min_hrs'] = np.where(
        df.max_star_t < df.w_hrs, df.max_star_t, df.w_hrs)
    df.loc[:, 'bdt_hrs'] = np.where(
        df.mdt < df.min_hrs, df.mdt, df.min_hrs)
    df = df.loc[:, (u'hrs_assigned', u'hrs_to_assign', u'max_star_t', u'mdt', u'w_end', u'w_hrs',
                    u'w_rank', u'w_region', u'w_start', u'w_type', u'worker_type', u'min_hrs', u'bdt_hrs', 'adt_hrs')]
    Sch_W = SchWorkers(city)
    res = Sch_W.df_insert(df)
    return res


def process_unpaid_orders():
    access_key = 'xunjiepf'
    url = "https://banana.xunjiepf.cn/api/extend/getorderlist"
    data = {
        'access_key': access_key,
        'order_status': 1,
    }
    res = requests.post(
        url,
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(data)
    )
    result = res.json()['data']['data']
    paid_order = []
    for x in result[:2]:
        order_ids = x["order_id"]
        res = set_order_paid(order_ids)
        if res:
            paid_order.append(x)
    stl = SchTestLog()
    stl.create("Auto_Pay", dict(orders=paid_order))
    return paid_order


def set_order_paid(order_ids):
    access_key = 'xunjiepf'
    params = {
        "access_key": access_key,
        "order_ids": order_ids,
        "order_status": 2
    }
    res = requests.post(
        url='https://banana.xunjiepf.cn/api/extend/updateOrderStatus',
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(params)
    )
    if res.json()["errcode"] == 0:
        return order_ids
    else:
        return False
