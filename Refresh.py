
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import jieba
import pandas
import sqlite3
from wordcloud import WordCloud

# In[2]:

maxPage = 5  #搜索的页数

# In[]

def buildStopWordFile():
    filename = "stop_words.txt"

    f = open(filename,"r")
    result = list()
    for line in f.readlines():
        line = line.strip()
        if not len(line):
            continue

        result.append(line)
    f.close
    with open("stop_words2.txt","w",encoding='utf-8') as fw:
        for sentence in result:
            sentence.encode('utf-8')
            data=sentence.strip()  
            if len(data)!=0:  
                fw.write(data)
                fw.write("\n") 


# In[3]:


def getUrlInfo(url):
    try:
        res = requests.get(url)
        res.encoding = 'utf-8'
        #print(res.text)
        soup = BeautifulSoup(res.text, 'html.parser')
        article = soup.select('.article p')[:-1]
        article = '\n\t'.join([p.text.strip() for p in article])

        date = soup.select('.date')[0].text
        date = datetime.strptime(date, '%Y年%m月%d日 %H:%M')

        result = {}
        #result['url'] = url
        # result['head'] = head
        result['date'] = date
        result['article'] = article
    
    except:
        return
    
    return result


# In[4]:


def dealPages(maxPage):
    global allPages
    allPages = []
    for page in range(1,maxPage+1):
        url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page=%d'%(page)
        try:
            res = requests.get(url)
        except:
            continue

        pageInfo = []

        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        jd = json.loads(soup.text)
        for info in jd['result']['data']:
            url = info['url']
            title = info['title']
            #subtitle = info['stitle']
            #summary = info['summary']
            #intro = info['intro']
            keywords = info['keywords']

            date_article = getUrlInfo(url)

            if date_article == None:
                continue

            date = date_article['date']
            date = date.strftime('%Y-%m-%d %H:%M')
            article = date_article['article']

            news = {}
            news['url'] = url
            news['title'] = title
            news['keywords'] = keywords
            news['date'] = date
            news['article'] = article

            pageInfo.append(news)

        allPages.extend(pageInfo)


# In[5]:


def build_StopWords():
    global stop_words
    stop_words.clear()
    stop_filename = 'stop_words2.txt'
    stop_f = open(stop_filename,"r",encoding = 'utf-8')
    for stopWord in stop_f.readlines():
        stopWord = stopWord.strip()
        if len(stopWord) == 0:
            continue
        stop_words.append(stopWord)
    stop_f.close


# In[6]:


def build_TermDict():
    global TermDict, N, avg_l
    global allPages
    TermDict.clear()
    avg_l = 0  #文档平均长度,即平均每个新闻中有多少个有效词
    N = len(allPages)
    cloudTerm = []  #用于云图构建
    for doc_id in range(0,N):
        doc = allPages[doc_id]
        #toCut = doc['title']*30 + doc['keywords']*15+doc['article'] #设定不同的权重
        toCut = doc['title']+doc['keywords']
        terms = jieba.cut_for_search(toCut)

        ld = 0  #文档长度，即文章中有效词的个数

        #去除标点和停用词
        Terms = {}
        
        for p in terms:
            p = p.strip()
            if len(p)>0 and p not in stop_words and not p.isdigit():
                if p in Terms:
                    Terms[p] += 1
                else:
                    Terms[p] = 1
                cloudTerm.append(p)
                ld += 1
                avg_l += 1
        #将Terms中元素加入TermDict
        
        for p in Terms:
            if p in TermDict:
                TermDict[p][0] += Terms[p]
            else:
                TermDict[p] = [1,[]]
            TermDict[p][1].append('%d\t%s\t%d\t%d'%(doc_id, doc['date'], Terms[p],ld ))

    avg_l /= N
    
    #生成云图
    cloudText = ','.join(cloudTerm)
    wc = WordCloud(
    background_color="white", #背景颜色
    max_words=200, #显示最大词数
    font_path="simhei.ttf",  #使用字体
    min_font_size=15,
    max_font_size=50, 
    width=400  #图幅宽度
    )
    wc.generate(cloudText)
    wc.to_file("wordcloud.gif")

    #将TermDict中文档信息合并成一个字符串，用\n隔开
    for i in TermDict:
        TermDict[i][1] = '\n'.join(TermDict[i][1])


# In[7]:


def WriteInDataBase():
    #将TermDict写入数据库
    global TermDict
    df = pandas.DataFrame(TermDict).T

    db = sqlite3.connect('news.sqlite')
    df.to_sql('TermDict',con = db,if_exists='replace')  #如果表存在就将表替代
    db.close()
    #将N 和 avg_l写入txt文件中
    paraF = open('parameter.txt','w')
    paraF.write('%d\t%d'%(N,avg_l))
    paraF.close()
    
    #将allPages写入数据库
    df = pandas.DataFrame(allPages)
    db = sqlite3.connect('news.sqlite')
    df.T.to_sql('allPages',con = db,if_exists='replace')  #如果表存在就将表替代
    
    db.close()
    
# In[9]:


def refresh():
    global maxPage
    global allPages, TermDict, stop_words, N, avg_l
    #停用词文档构建
    #buildStopWordFile()
    
    #处理滚动页面
    allPages = []
    
    dealPages(maxPage)
    
    #构建列表stop_words,包含停用词和标点
    stop_words = []
    build_StopWords()
    
    #构建TermDict
    TermDict={}
    N = 0
    avg_l = 0
    build_TermDict()
    
    #将TermDict转化为pandas中的DataFrame，再写入数据库sqlite
    WriteInDataBase()

if __name__ == '__main__':
    refresh()