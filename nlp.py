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
     
def review_clean(df_dirty):
    import simplejson
    # to dict
    df_dirty['精选评论'] = df_dirty['精选评论'].map(lambda x:simplejson.loads(x))
    
    # use explode to give each dict in a list a separate row
    df_dirty = pd.DataFrame(df_dirty.精选评论.explode().reset_index(drop=True))

    # normalize the column of dicts, join back to the remaining dataframe columns, and drop the unneeded column
    df_dirty = pd.json_normalize(df_dirty.精选评论)
    df_dirty = df_dirty[['评论内容','用户总分','店铺id']]

    # words_split
    # df_dirty['评论内容'] = df_dirty['评论内容'].apply(lambda x:' '.join(jieba.cut(x)))
    
    df_dirty['用户总分'] = pd.to_numeric(df_dirty['用户总分'],errors='coerce')
    
    return df_dirty


#Chinese stop words
infile = open("raw_data/cn_stopwords.txt",encoding='utf-8')
stopwords_lst = infile.readlines()
stopwords = [x.strip() for x in stopwords_lst]    

def ceshi(model,strings):
    strings_fenci = fenci(pd.Series([strings]))
    return round(float(model.predict_proba(tv.transform(strings_fenci))[:,1]),2)
    
def nlp_score(path): 
    df = pd.read_csv(path,encoding='utf-8')
    df_review = review_clean(df)
    
    df_review['target'] = df_review['用户总分'].map(lambda x:score_trans(x))  
    df_model = df_review.dropna()
    
    x_train, x_test, y_train, y_test = train_test_split(df_model['评论内容'], df_model['target'], random_state=3, test_size=0.25)
    
    tv = TfidfVectorizer(stop_words=stopwords, max_features=3000, ngram_range=(1,2))
    tv.fit(x_train)
    
    classifier = MultinomialNB()
    classifier.fit(tv.transform(x_train), y_train)
    
    df_review['nlp_score'] = df_review['评论内容'].map(lambda x:round(float(classifier.predict_proba([tv.transform([x])[:,1]]),2)))
    
    return df_review

    
    
    
    
