import pandas as pd
import jieba
from matplotlib import pyplot as plt
import simplejson
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import roc_auc_score, f1_score


def score_trans(score):
    if score > 3:
        return 1
    elif score <= 3:
        return 0
    else:
        return None

def words_split(data):
    words_df = data.apply(lambda x:' '.join(jieba.cut(x)))
    return words_df
     
def review_clean(df):
    
    # to dict
    df['精选评论'] = df['精选评论'].map(lambda x:simplejson.loads(x))
    
    # use explode to give each dict in a list a separate row
    df = pd.DataFrame(df.精选评论.explode().reset_index(drop=True))

    # normalize the column of dicts, join back to the remaining dataframe columns, and drop the unneeded column
    df = pd.json_normalize(df.精选评论)
    df = df[['评论内容','用户总分','店铺id']]

    # words_split
    df['评论内容'] = df['评论内容'].apply(lambda x:' '.join(jieba.cut(x)))
    
    df['用户总分'] = pd.to_numeric(df['用户总分'],errors='coerce')
    
    return df


#Chinese stop words
infile = open("raw_data/cn_stopwords.txt",encoding='utf-8')
stopwords_lst = infile.readlines()
stopwords = [x.strip() for x in stopwords_lst]    

def pred_score(model,tv,strings):
    
    strings_fenci = words_split(pd.Series([strings]))
    return round(float(model.predict_proba(tv.transform(strings_fenci))[:,1]),2)
    
def nlp_score(df): 
    # df = pd.read_csv(path,encoding='utf-8')
    df_nlp = review_clean(df)
    
    df_nlp['target'] = df_nlp['用户总分'].map(lambda x:score_trans(x))  
    df_model = df_nlp.dropna()
    
    x_train, x_test, y_train, y_test = train_test_split(df_model['评论内容'], df_model['target'], random_state=3, test_size=0.25)
    
    # 5 times of negative comments
    index_tmp = y_train==0
    y_tmp = y_train[index_tmp]
    x_tmp = x_train[index_tmp]
    x_train2 = pd.concat([x_train,x_tmp,x_tmp,x_tmp,x_tmp,x_tmp])
    y_train2 = pd.concat([y_train,y_tmp,y_tmp,y_tmp,y_tmp,y_tmp])
    
    tv = TfidfVectorizer(stop_words=stopwords, max_features=3000, ngram_range=(1,2))
    tv.fit(x_train)
    
    classifier = MultinomialNB()
    classifier.fit(tv.transform(x_train2), y_train2)
    
    df_nlp['nlp_score'] = df_nlp['评论内容'].map(lambda x:pred_score(classifier,tv,x))
    
    y_pred = classifier.predict_proba(tv.transform(x_test))[:,1]
    print(roc_auc_score(y_test,y_pred))
    
    df_nlp = df_nlp.groupby(['店铺id'],as_index=False).mean()
    df_nlp = df_nlp.drop(columns = ['target'])
    
    return df_nlp

   
    
    
    
