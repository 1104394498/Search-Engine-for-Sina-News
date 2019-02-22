
import tkinter as tk
from Refresh import refresh
import threading, sqlite3, pandas
from Search import search

first_time = 1

'''
import Search
import Refresh
import wordcloud
'''

def showArticle(i):
    if len(allPages[Pages[i][1]]['article']) > 600:
        arit_text = allPages[Pages[i][1]]['article'][0:600]+' ......'
    else:
        arit_text = allPages[Pages[i][1]]['article']
    artibody = tk.Label(news_canvas,text = arit_text,
                        width = 65, height = 35, font = ('SimHei',13),
                        wraplength = 590, justify = 'left', anchor = 'w',
                        bg = 'white',relief=tk.RIDGE, bd = 3)
    artibody.place(x=670, y =20)
  
def display_news():
    news_window = tk.Tk()
    news_window.geometry('3000x650')
    global news_canvas
    news_canvas = tk.Canvas(news_window, bg = 'white',height = 750,width = 3200)
    news_canvas.pack()

    #lb = tk.Listbox(news_canvas,width = 100, height = 33)
    
    #message_menu = tk.LabelFrame(news_window,background = 'white', bd = 3, 
                                 #padx = 250, pady = 50)
    global Pages
    Pages = []
    while not minheap.empty():
        Pages.append(minheap.pop())
    Pages.reverse()
    summary = ['']*6
    for i in range(len(Pages)):
        newsNO = Pages[i][1]
        if i >= 6:
            break
        summary[i] = '文章标题： '+allPages[newsNO]['title']+'\n'+'关键词： '+allPages[newsNO]['keywords']
        
        
        
    message_label = [None]*6
    
    message_label[0] = tk.Button(news_canvas, text = summary[0], 
                     bd=3,background='white', width = 70,height=5,
                     font = ('SimHei',13), relief= tk.RIDGE, command=lambda:showArticle(0))
    message_label[1] = tk.Button(news_canvas, text = summary[1], 
                     bd=3,background='white', width = 70,height=5,
                     font = ('SimHei',13), relief=tk.RIDGE, command=lambda:showArticle(1))
    message_label[2] = tk.Button(news_canvas, text = summary[2], 
                     bd=3,background='white', width = 70,height=5,
                     font = ('SimHei',13), relief=tk.RIDGE, command=lambda:showArticle(2))
    message_label[3] = tk.Button(news_canvas, text = summary[3], 
                     bd=3,background='white', width = 70,height=5,
                     font = ('SimHei',13), relief=tk.RIDGE, command=lambda:showArticle(3))
    message_label[4] = tk.Button(news_canvas, text = summary[4], 
                     bd=3,background='white', width = 70,height=5,
                     font = ('SimHei',13), relief=tk.RIDGE, command=lambda:showArticle(4))
    message_label[5] = tk.Button(news_canvas, text = summary[5], 
                     bd=3,background='white', width = 70,height=5,
                     font = ('SimHei',13), relief=tk.RIDGE, command=lambda:showArticle(5))

    for i in range(min(len(Pages),6)):
        message_label[i].place(x=0,y=20+100*i)
    
    news_window.mainloop()
    print('finish news window')
    

def call_refresh_window():
    global refresh_window
    print('call refresh_window')
    refresh_window = tk.Tk()
    refresh_window.geometry('400x300')
    refresh_canvas = tk.Canvas(refresh_window, bg = 'white',height = 400,width = 500)
    refresh_canvas.create_text(150,150,text = '正在刷新数据库，请稍等',font = ('bold Arial',15))
    refresh_canvas.pack()
   
    refresh_window.mainloop()
    print('finish_main_loop')
    
def call_refresh():
    print('call refresh')
    refresh()
    refresh_window.destroy()

def search_mode():
    global search_entry
    global N, avg_l, allPages, minheap
    sentence = search_entry.get()
    #恢复N, avg_l
    paraF = open('parameter.txt','r')
    para = paraF.readline().split()
    N = int(para[0])
    avg_l = int(para[1])
    paraF.close()
    
    #恢复allPages
    db = sqlite3.connect('news.sqlite')
    df2 = pandas.read_sql_query('SELECT * FROM allPages', con = db)
    allPages_new = df2.to_dict()
    db.close()
    first_time = True
    index = None
    allPages = []
    for x in allPages_new:
        if first_time:
            index = allPages_new[x]
            first_time = False
        else:
            newDict = dict()
            for i in allPages_new[x]:
                newDict[index[i]] = allPages_new[x][i]
            allPages.append(newDict)
    
    #TermDict在search中取出    
    minheap = search(sentence, N, avg_l)
    
    display_news()


def refresh_mode():
    t1 = threading.Thread(target=call_refresh_window)
    t2 = threading.Thread(target=call_refresh)
    threads = []
    threads.append(t1)
    threads.append(t2)
    for t in threads:
        #t.setDaemon(True)
        t.start()
    

if __name__ == '__main__':
    window = tk.Tk()
    window.geometry('3000x650')
    
    canvas = tk.Canvas(window, bg = 'white',height = 750,width = 3200)
    #欢迎图片
    welcome_file = tk.PhotoImage(file = 'welcome.gif')
    welcome_img = canvas.create_image(500,10,anchor = 'nw', image = welcome_file)
    
    #词云
    ciyun_file = tk.PhotoImage(file = "wordcloud.gif")
    ciyun_img = canvas.create_image(450,400,anchor = 'nw', image = ciyun_file)
    
    #广告
    ad_file = tk.PhotoImage(file = "ad.png")
    ciyun_img = canvas.create_image(500,200,anchor = 'nw', image = ad_file)
    
    canvas.pack()
    
    #输入文本框
    search_entry = tk.Entry(window, show = None, width = 50,  bd = 3,font =('Arial',20))
    search_entry.place(x=200,y=300)
    text = tk.Text()
    
    #搜索键
    search_button = tk.Button(window, bg = 'SkyBlue', text = '千度一下'
                              ,font =('bold Arial',16),command = search_mode)
    search_button.place(x=970,y=300)
    
    #刷新
    #refresh_entry = tk.Entry(window, show = None , width = 5, bd = 3,font = ('Arial',20))
    #refresh_entry.place(x = 900, y = 250)
    
    refresh_button = tk.Button(window, bg = 'SkyBlue', text = '刷新'
                              ,font =('bold Arial',16),command = refresh_mode)
    refresh_button.place(x=1100,y=300)
    text.pack()
    
    window.mainloop()

