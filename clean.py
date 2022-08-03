import os

import pandas as pd

from nlp import nlp_score


def review_tag(str):
    if len(str) == 0:
        result = "NaN"
    else:
        result = dict((a.strip(), int(b.strip()))
                      for a, b in (element.split('(') for element in str.split(')')))

    return result


def info_clean(df_info):
    df_info['评论标签'] = df_info['评论标签'].fillna(value='不用排队 (0)')
    df_info['评论标签'] = df_info['评论标签'].astype(str)
    df_info['评论标签'] = df_info['评论标签'].apply(lambda x: x.strip())
    df_info['评论标签'] = df_info['评论标签'].apply(lambda x: x[:len(x) - 1])

    df_info['评论标签'] = df_info['评论标签'].apply(lambda x: review_tag(x))
    df_info = df_info.drop(['店铺电话', '图片评论数'], axis=1)

    df_info["不用排队"] = df_info["评论标签"].map(lambda x: x.get('不用排队'))
    df_info["不用排队"] = df_info["不用排队"].fillna(value=0)

    return df_info


def recommend_dishes(df_dish):
    df_dish = df_dish.groupby(['店铺ID'], as_index=False).apply(lambda x: ','.join(x['推荐菜']))
    df_dish.columns = ["店铺id", "推荐菜"]
    return df_dish


# def review_clean(df):
#     # df["评论摘要"] = df["评论摘要"].map(lambda x:simplejson.loads(x))
#     df["不用排队"] = df["评论标签"].apply(x:x.get('不用排队'))
#     df["不用排队"] = df["不用排队"].fillna(value=0)
#     df = df.drop(columns=['_id','精选评论','评论摘要','带图评论个数'])
#     return df 

def chn_to_eng(df):
    return df.rename(
        columns={"人均价格": "price_per_person", "店铺id": "restaurant_id", "店铺名": "restaurant"
            , "店铺地址": "address", "店铺总分": "total_review_score", "标签1": "cuisine", "标签2": "district2"
            , "评论总数": "total_review_number", "口味": "taste", "环境": "surroundings", "服务": "service"
            , "推荐菜1": "recommendation_1", "推荐菜2": "recommendation_2", "推荐菜3": "recommendation_3"
            , "中评数": "medium_review_number", "好评数": "good_review_number", "差评数": "bad_review_number"
            , "不用排队": "no_queues", "经度": "longitude", "纬度": "latitude", "区": "district",
                 "类目1": "cuisine2"
            , "评论标签": "top_comments"})


# def eng_to_chn(df):
#     return df.rename(columns={"price_per_person":"人均价格", "restaurant_id":"店铺id", "restaurant":"店铺名"
#                   ,"address":"店铺地址","total_review_score":"店铺总分","tag1":"标签1","tag2":"标签2"
#                   ,"total_review_number":"评论总数","taste":"口味","surroundings":"环境","service":"服务"
#                   ,"recommendation_1":"推荐菜1","recommendation_2":"推荐菜2","recommendation_3":"推荐菜3"
#                   ,"medium_review_number":"中评个数","good_review_number":"好评个数","bad_review_number":"差评个数"
#                   ,"no_queues":"不用排队"})

def run(info_path, review_path, dishes_path):
    df_info = pd.read_csv(os.path.join(os.getcwd(), 'raw_data', info_path))
    df_review = pd.read_csv(os.path.join(os.getcwd(), 'raw_data', review_path))
    df_dish = pd.read_csv(os.path.join(os.getcwd(), 'raw_data', dishes_path))

    df = pd.merge(info_clean(df_info), nlp_score(df_review), on="店铺id")
    df = pd.merge(df, recommend_dishes(df_dish), on="店铺id")

    df = df.drop(columns=["评分"])
    # df = classify_cuisine(df)
    # df = classify_area(df)
    df = chn_to_eng(df)
    df["no_queues%"] = df["no_queues"] / df["total_review_number"]

    return df


def recommendation(cuisine, district):
    df = pd.read_csv("raw_data/cleaned_data.csv")
    if district == "全部" and cuisine == "全部":
        df = df
    elif district == "全部":
        df = df[(df.cuisine == cuisine)]
    elif cuisine == "全部":
        df = df[(df.district == district)]
    else:
        df = df[(df.cuisine == cuisine) & (df.district == district)]
    # df = df[df.nlp_score == df.nlp_score.max()]
    df = df.nlargest(n=3, columns=['nlp_score']).reset_index(drop=True)
    df = df.iloc[:, 1:]
    df["rank"] = df.index + 1
    return df.to_dict(orient='records')
