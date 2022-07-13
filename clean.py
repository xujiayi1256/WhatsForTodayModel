import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import simplejson

def splitScore(df):
    x0 = []
    x1 = []
    x2 = []
    for idx, row in df.iterrows():
        tmp = simplejson.loads(row['店铺均分'])
        x0.append(tmp['口味'])
        x1.append(tmp['环境'])
        x2.append(tmp['服务'])
    test = pd.DataFrame({'口味':x0,'环境':x1, '服务':x2})
    dd1 = pd.concat([df,test],axis=1)
    dd1 = dd1.drop(['_id','优惠券信息','其他信息','详情链接','图片链接','店铺电话','店铺均分'],axis=1)
    return dd1

def no_queues(x):
    for i in x:
        if i['描述'] == '不用排队':
            return int(i['个数'])
        else:
            0

def split_review1(df):
    df["评论摘要"] = df["评论摘要"].map(lambda x:simplejson.loads(x))
    df["不用排队"] = df["评论摘要"].apply(no_queues)
    df["不用排队"] = df["不用排队"].fillna(value=0)
    df = df.drop(columns=['_id','精选评论','评论摘要','带图评论个数'])
    return df 

df = pd.read_excel('dianping_info(1).xlsx')
df1 = pd.read_excel('dianping_review.xlsx')
print(pd.merge(splitScore(df),split_review1(df1)))