import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import simplejson
from nlp import nlp_score,review_clean,score_trans,pred_score

def split_score(df):
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
    dd1 = dd1.drop(['_id','优惠券信息','其他信息','详情链接','图片链接','店铺电话','店铺均分','评论总数','推荐菜'],axis=1)
    dd1["口味"] = pd.to_numeric(dd1["口味"],errors='coerce')
    dd1["环境"] = pd.to_numeric(dd1["环境"],errors='coerce')
    dd1["服务"] = pd.to_numeric(dd1["服务"],errors='coerce')
    return dd1

def split_dishes(df):
    x0 = []
    x1 = []
    x2 = []
    for value in df['推荐菜']:
        tmp = simplejson.loads(value)
        x0.append(tmp[0])
        x1.append(tmp[1])
        x2.append(tmp[2])
    test = pd.DataFrame({'推荐菜1':x0,'推荐菜2':x1,'推荐菜3':x2})
    dd2 = pd.concat([df,test],axis=1)
    dd2 = dd2.drop(['推荐菜'],axis=1)
    return dd2

def no_queues(x):
    for i in x:
        if i['描述'] == '不用排队':
            return int(i['个数'])
        else:
            0

def split_review(df):
    df["评论摘要"] = df["评论摘要"].map(lambda x:simplejson.loads(x))
    df["不用排队"] = df["评论摘要"].apply(no_queues)
    df["不用排队"] = df["不用排队"].fillna(value=0)
    df = df.drop(columns=['_id','精选评论','评论摘要','带图评论个数'])
    return df 

def chn_to_eng(df):
    return df.rename(columns={"人均价格": "price_per_person", "店铺id": "restaurant_id", "店铺名":"restaurant"
                  ,"店铺地址":"address","店铺总分":"total_review_score","标签1":"tag1","标签2":"tag2"
                  ,"评论总数":"total_review_number","口味":"taste","环境":"surroundings","服务":"service"
                  ,"推荐菜1":"recommendation_1","推荐菜2":"recommendation_2","推荐菜3":"recommendation_3"
                  ,"中评个数":"medium_review_number","好评个数":"good_review_number","差评个数":"bad_review_number"
                  ,"不用排队":"no_queues"})

def eng_to_chn(df):
    return df.rename(columns={"price_per_person":"人均价格", "restaurant_id":"店铺id", "restaurant":"店铺名"
                  ,"address":"店铺地址","total_review_score":"店铺总分","tag1":"标签1","tag2":"标签2"
                  ,"total_review_number":"评论总数","taste":"口味","surroundings":"环境","service":"服务"
                  ,"recommendation_1":"推荐菜1","recommendation_2":"推荐菜2","recommendation_3":"推荐菜3"
                  ,"medium_review_number":"中评个数","good_review_number":"好评个数","bad_review_number":"差评个数"
                  ,"no_queues":"不用排队"})

def run(path1,path2):
    df_info = pd.read_csv(os.path.join(os.getcwd(),'raw_data',path1))
    df_review = pd.read_csv(os.path.join(os.getcwd(),'raw_data',path2))
    # df = pd.merge(split_dishes(split_score(df_info)),split_review(df_review))
    df = pd.merge(split_score(df_info),split_review(df_review),on="店铺id")
    df = pd.merge(df,nlp_score(df_review),on="店铺id")
    df = df.drop(columns=["推荐菜","用户总分"])
    df = chn_to_eng(df)
    df["no_queues%"] = df["no_queues"]/df["total_review_number"]
    return df



def recommendation(cuisine, district):
    df = pd.read_csv("raw_data/cleaned_data.csv")
    if district == "全部" and cuisine == "全部":
        df = df
    elif district == "全部":
        df = df[(df.tag1==cuisine)]
    elif cuisine == "全部":
        df = df[(df.tag2==district)]
    else:
        df = df[(df.tag1==cuisine)&(df.tag2==district)]
    # df = df[df.nlp_score == df.nlp_score.max()]
    df = df.nlargest(n=3, columns=['nlp_score']).reset_index(drop=True)
    df = df.iloc[:, 1:]
    df["rank"] = df.index + 1
    return df.to_dict("r")