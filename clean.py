import os

import numpy as np
import pandas as pd
import simplejson

from nlp import nlp_score


def split_score(df):
    x0 = []
    x1 = []
    x2 = []
    for idx, row in df.iterrows():
        tmp = simplejson.loads(row['店铺均分'])
        x0.append(tmp['口味'])
        x1.append(tmp['环境'])
        x2.append(tmp['服务'])
    test = pd.DataFrame({'口味': x0, '环境': x1, '服务': x2})
    dd1 = pd.concat([df, test], axis=1)
    dd1 = dd1.drop(['_id', '优惠券信息', '其他信息', '详情链接', '图片链接', '店铺电话', '店铺均分', '评论总数', '推荐菜'], axis=1)
    dd1["口味"] = pd.to_numeric(dd1["口味"], errors='coerce')
    dd1["环境"] = pd.to_numeric(dd1["环境"], errors='coerce')
    dd1["服务"] = pd.to_numeric(dd1["服务"], errors='coerce')
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
    test = pd.DataFrame({'推荐菜1': x0, '推荐菜2': x1, '推荐菜3': x2})
    dd2 = pd.concat([df, test], axis=1)
    dd2 = dd2.drop(['推荐菜'], axis=1)
    return dd2


def no_queues(x):
    for i in x:
        if i['描述'] == '不用排队':
            return int(i['个数'])
        else:
            0


def split_review(df):
    df["评论摘要"] = df["评论摘要"].map(lambda x: simplejson.loads(x))
    df["不用排队"] = df["评论摘要"].apply(no_queues)
    df["不用排队"] = df["不用排队"].fillna(value=0)
    df = df.drop(columns=['_id', '精选评论', '评论摘要', '带图评论个数'])
    return df


def chn_to_eng(df):
    return df.rename(
        columns={"人均价格": "price_per_person", "店铺id": "restaurant_id", "店铺名": "restaurant"
            , "店铺地址": "address", "店铺总分": "total_review_score", "标签1": "tag1", "标签2": "tag2"
            , "评论总数": "total_review_number", "口味": "taste", "环境": "surroundings", "服务": "service"
            , "推荐菜1": "recommendation_1", "推荐菜2": "recommendation_2", "推荐菜3": "recommendation_3"
            , "中评个数": "medium_review_number", "好评个数": "good_review_number",
                 "差评个数": "bad_review_number"
            , "不用排队": "no_queues"})


def eng_to_chn(df):
    return df.rename(
        columns={"price_per_person": "人均价格", "restaurant_id": "店铺id", "restaurant": "店铺名"
            , "address": "店铺地址", "total_review_score": "店铺总分", "tag1": "标签1", "tag2": "标签2"
            , "total_review_number": "评论总数", "taste": "口味", "surroundings": "环境", "service": "服务"
            , "recommendation_1": "推荐菜1", "recommendation_2": "推荐菜2", "recommendation_3": "推荐菜3"
            , "medium_review_number": "中评个数", "good_review_number": "好评个数",
                 "bad_review_number": "差评个数"
            , "no_queues": "不用排队"})


def run(path1, path2):
    df_info = pd.read_csv(os.path.join(os.getcwd(), 'raw_data', path1))
    df_review = pd.read_csv(os.path.join(os.getcwd(), 'raw_data', path2))
    # df = pd.merge(split_dishes(split_score(df_info)),split_review(df_review))
    df = pd.merge(split_score(df_info), split_review(df_review), on="店铺id")
    df = pd.merge(df, nlp_score(df_review), on="店铺id")
    df = df.drop(columns=["推荐菜", "用户总分"])
    df = classify_cuisine(df)
    df = classify_area(df)
    df = chn_to_eng(df)
    df["no_queues%"] = df["no_queues"] / df["total_review_number"]

    return df


def cuisine_list():
    detail = []
    cuisine = []
    s1 = '牛羊肉火锅|重庆火锅|潮汕牛肉火锅|四川火锅|羊蝎子火锅|串串香|鱼火锅|小火锅|老北京火锅|打边炉/港式火锅|自助火锅|猪肚鸡火锅|\
    海鲜火锅|本地鸡窝火锅|汤锅|焖锅|炭火锅|云南火锅|日韩火锅|腊排骨火锅|澳门豆捞|泰式火锅|菌菇火锅|芋儿鸡|虾蟹火锅|韩式火锅|黑山羊火锅|火锅'
    c1 = '火锅'
    s2 = '融合烤肉|韩式烤肉|拉美烤肉|炙子烤肉|烤肉'
    c2 = '烤肉'
    s3 = '日本料理|日式烧烤/烤肉|寿司|日式面条|日式铁板烧|日式自助|日式火锅'
    c3 = '日本菜'
    s4 = '比萨|轻食沙拉|意大利菜|牛排|法国菜|西班牙菜|西餐自助|西餐'
    c4 = '西餐'
    s5 = '韩国料理'
    c5 = '韩国料理'
    s6 = '粤菜馆|茶餐厅|烧腊|潮汕菜|粤式茶点|燕翅鲍|广州菜|顺德菜|客家菜'
    c6 = '粤菜'
    s7 = '上海本帮菜|苏浙菜|浙菜|淮扬菜|衢州菜|苏帮菜|南京菜|无锡菜|温州菜'
    c7 = '本帮江浙菜'
    s8 = '烤鱼|川菜馆|干锅/香锅|酸菜鱼/水煮鱼'
    c8 = '川菜'
    s9 = '泰国菜|越南菜|新加坡菜|印度菜|南洋中菜'
    c9 = '东南亚菜'
    s10 = '快餐简餐|小吃|包子|炸鸡炸串|馄饨|抄手|扁食|熟食熏酱|麻辣烫|卤味鸭脖|饺子|西式快餐|米粉|黄焖鸡|粥店|生煎|日式简餐/快餐|锅贴|小笼|桂林米粉|韩式小吃|花甲|烧鸡|美食城'
    c10 = '小吃快餐'
    cuisine.append(c1)
    cuisine.append(c2)
    cuisine.append(c3)
    cuisine.append(c4)
    cuisine.append(c5)
    cuisine.append(c6)
    cuisine.append(c7)
    cuisine.append(c8)
    cuisine.append(c9)
    cuisine.append(c10)
    detail.append(s1)
    detail.append(s2)
    detail.append(s3)
    detail.append(s4)
    detail.append(s5)
    detail.append(s6)
    detail.append(s7)
    detail.append(s8)
    detail.append(s9)
    detail.append(s10)
    return detail, cuisine


def classify_cuisine(df):
    detail, cuisine = cuisine_list()
    cp_df = pd.DataFrame({"种类": cuisine, "具体": detail})
    df['cuisine'] = np.where(df['标签1'].str.contains(cp_df["具体"][0]), cp_df["种类"][0],
                             np.where(df['标签1'].str.contains(cp_df["具体"][1]), cp_df["种类"][1],
                                      np.where(df['标签1'].str.contains(cp_df["具体"][2]),
                                               cp_df["种类"][2],
                                               np.where(df['标签1'].str.contains(cp_df["具体"][3]),
                                                        cp_df["种类"][3],
                                                        np.where(
                                                            df['标签1'].str.contains(cp_df["具体"][4]),
                                                            cp_df["种类"][4],
                                                            np.where(df['标签1'].str.contains(
                                                                cp_df["具体"][5]), cp_df["种类"][5],
                                                                     np.where(
                                                                         df['标签1'].str.contains(
                                                                             cp_df["具体"][6]),
                                                                         cp_df["种类"][6],
                                                                         np.where(
                                                                             df['标签1'].str.contains(
                                                                                 cp_df["具体"][7]),
                                                                             cp_df["种类"][7],
                                                                             np.where(df[
                                                                                          '标签1'].str.contains(
                                                                                 cp_df["具体"][8]),
                                                                                      cp_df["种类"][
                                                                                          8],
                                                                                      np.where(df[
                                                                                                   '标签1'].str.contains(
                                                                                          cp_df[
                                                                                              "具体"][
                                                                                              9]),
                                                                                               cp_df[
                                                                                                   "种类"][
                                                                                                   9],
                                                                                               0))))))))))
    return df


def classify_area(df):
    xzq_ls = []
    df_xzq = pd.read_excel(os.path.join(os.getcwd(), 'raw_data', '上海热门商区.xlsx'))
    xzq_l = list(df_xzq['行政区'].unique())
    for i in xzq_l:
        test = df_xzq[df_xzq["行政区"] == i]
        xzq_ls.append("|".join(test["热门商区"]))
    xzq_df = pd.DataFrame({"行政区": xzq_l, "热门商区": xzq_ls})
    df['district'] = np.where(df['标签2'].str.contains(xzq_df["热门商区"][0]), xzq_df["行政区"][0],
                              np.where(df['标签2'].str.contains(xzq_df["热门商区"][1]), xzq_df["行政区"][1],
                                       np.where(df['标签2'].str.contains(xzq_df["热门商区"][2]),
                                                xzq_df["行政区"][2],
                                                np.where(df['标签2'].str.contains(xzq_df["热门商区"][3]),
                                                         xzq_df["行政区"][3],
                                                         np.where(df['标签2'].str.contains(
                                                             xzq_df["热门商区"][4]), xzq_df["行政区"][4],
                                                                  np.where(df['标签2'].str.contains(
                                                                      xzq_df["热门商区"][5]),
                                                                           xzq_df["行政区"][5],
                                                                           np.where(df[
                                                                                        '标签2'].str.contains(
                                                                               xzq_df["热门商区"][6]),
                                                                                    xzq_df["行政区"][
                                                                                        6],
                                                                                    np.where(df[
                                                                                                 '标签2'].str.contains(
                                                                                        xzq_df[
                                                                                            "热门商区"][
                                                                                            7]),
                                                                                             xzq_df[
                                                                                                 "行政区"][
                                                                                                 7],
                                                                                             np.where(
                                                                                                 df[
                                                                                                     '标签2'].str.contains(
                                                                                                     xzq_df[
                                                                                                         "热门商区"][
                                                                                                         8]),
                                                                                                 xzq_df[
                                                                                                     "行政区"][
                                                                                                     8],
                                                                                                 np.where(
                                                                                                     df[
                                                                                                         '标签2'].str.contains(
                                                                                                         xzq_df[
                                                                                                             "热门商区"][
                                                                                                             9]),
                                                                                                     xzq_df[
                                                                                                         "行政区"][
                                                                                                         9],
                                                                                                     np.where(
                                                                                                         df[
                                                                                                             '标签2'].str.contains(
                                                                                                             xzq_df[
                                                                                                                 "热门商区"][
                                                                                                                 10]),
                                                                                                         xzq_df[
                                                                                                             "行政区"][
                                                                                                             10],
                                                                                                         np.where(
                                                                                                             df[
                                                                                                                 '标签2'].str.contains(
                                                                                                                 xzq_df[
                                                                                                                     "热门商区"][
                                                                                                                     11]),
                                                                                                             xzq_df[
                                                                                                                 "行政区"][
                                                                                                                 11],
                                                                                                             np.where(
                                                                                                                 df[
                                                                                                                     '标签2'].str.contains(
                                                                                                                     xzq_df[
                                                                                                                         "热门商区"][
                                                                                                                         12]),
                                                                                                                 xzq_df[
                                                                                                                     "行政区"][
                                                                                                                     12],
                                                                                                                 np.where(
                                                                                                                     df[
                                                                                                                         '标签2'].str.contains(
                                                                                                                         xzq_df[
                                                                                                                             "热门商区"][
                                                                                                                             13]),
                                                                                                                     xzq_df[
                                                                                                                         "行政区"][
                                                                                                                         13],
                                                                                                                     np.where(
                                                                                                                         df[
                                                                                                                             '标签2'].str.contains(
                                                                                                                             xzq_df[
                                                                                                                                 "热门商区"][
                                                                                                                                 14]),
                                                                                                                         xzq_df[
                                                                                                                             "行政区"][
                                                                                                                             14],
                                                                                                                         np.where(
                                                                                                                             df[
                                                                                                                                 '标签2'].str.contains(
                                                                                                                                 xzq_df[
                                                                                                                                     "热门商区"][
                                                                                                                                     15]),
                                                                                                                             xzq_df[
                                                                                                                                 "行政区"][
                                                                                                                                 15],
                                                                                                                             0))))))))))))))))
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
