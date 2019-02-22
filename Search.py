
# coding: utf-8

# In[ ]:

import jieba
from datetime import datetime
import sqlite3
import pandas
from MinHeap import MinHeap
# In[5]:


def build_StopWords():
    global stop_words
    stop_words = []
    stop_filename = 'stop_words2.txt'
    stop_f = open(stop_filename,"r",encoding = 'utf-8')
    for stopWord in stop_f.readlines():
        stopWord = stopWord.strip()
        if len(stopWord) == 0:
            continue
        stop_words.append(stopWord)
    stop_f.close


# In[]
import math
def search(sentence, N, avg_l):
    #global N, avg_l
    #global RelaScore, Pages
    build_StopWords()
    #对输入的词进行相关度评价
    searchTerms1 = jieba.lcut(sentence, cut_all = False)
    #清除停用词
    searchTerms = {}
    for p in searchTerms1:
        p=p.strip()
        if len(p)>0 and p not in stop_words and not p.isdigit():
            if p not in searchTerms:
                searchTerms[p] = 1
            else:
                searchTerms[p] += 1

    db = sqlite3.connect('news.sqlite')
    #从数据库sqlite中读出表
    df2 = pandas.read_sql_query('SELECT * FROM TermDict', con = db)
    #df3 = df2.sort_values(axis =0, by=['0'],ascending=False)
    df3=df2.T
    Dict1 = df3.to_dict()
    Dict = {}
    for i in Dict1:
        Dict[Dict1[i]['index']] = [Dict1[i]['0'], Dict1[i]['1']]

    #print(searchTerms)
    #print(Dict)
    
    #采用基于概率的BM25模型计算相关度
    RelaScore = {}  #相关度分数，和allPages中的index相对应

    #参数
    b = 0.75
    k1 = 1.2

    RelaWeight = 0.7
    TimeWeight = 0.3

    #文档平均长度avg_l, 文档总数N 在前面已经求出
    for word in searchTerms:
        #将qtf近似为1
        #qtf = searchTerms[word]  #查询中的词频(query's term frequency)
        if word in Dict:
            df = Dict[word][0]   #文档频率(document frequency)，即该词在所有新闻中出现的总次数
            docs = Dict[word][1].split('\n')
            IDF = math.log2( (N + 0.5 + df) / (df+0.5))  #将分子上的df去掉了
            for x in docs:  #对每一个新闻处理，加上与这个词的相关度
                doc = x.split('\t')
                doc_id = int(doc[0])
                doc_time = doc[1]   #新闻时间
                tf = int(doc[2])    #文档中的词频(term frequency)
                ld = int(doc[3])    #文档长度(length of document)


                K = k1 * ( 1 - b + b*ld/avg_l )
                #计算w(word, doc)
                RelaW = IDF * (tf*(k1+1)) / (tf+K) 

                #w = qtf*tf/ld

                #计算时间因子
                newsTime = datetime.strptime(doc_time,'%Y-%m-%d %H:%M')
                nowTime = datetime.now()
                timeDis = (nowTime.day-newsTime.day)*24 + nowTime.hour-newsTime.hour +(nowTime.minute-newsTime.minute)/60   #以小时为单位

                w = RelaW * RelaWeight + TimeWeight/timeDis

                #print("%f %f"%(RelaW * RelaWeight,TimeWeight/timeDis ))
                if doc_id in RelaScore:
                    RelaScore[doc_id] += w
                else:
                    RelaScore[doc_id] = w
    
    minheap = MinHeap()
    for i in RelaScore:
        minheap.add((RelaScore[i],i))
                       
    #Pages = [(RelaScore[i], i) for i in RelaScore]
    #Pages.sort(key = lambda x:x[0], reverse = True)
    
    return minheap

# In[]
if __name__ == '__main__':
    search('特朗普', N ,avg_l)