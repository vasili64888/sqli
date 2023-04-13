from tkinter import *
from tkinter import messagebox
import requests
import queue
import logging
import sys 
import os 
from itertools import permutations
AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0'
#EXTENSIONS = ['.php', '.bak', '.orig', '.inc']
TARGET = 'http://192.168.217.145/'#URL后要加'/'
THREADS = 10
pwd = os.getcwd()
WORDLIST = pwd+"\\dirb\\all.txt"
LOGFILE=pwd+"\\dirb\\log_url.txt"
DirectoryLevel=2
Newlimit = 50
#limit recursion depth
sys.setrecursionlimit(Newlimit) 
# 配置日志输出级别为INFO，格式为时间+级别+消息，文件名为指定的参数
#logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', filename=LOGFILE)
logging.basicConfig(level=logging.INFO, format='%(message)s', filename=LOGFILE)
# 获取一个名为scanner的Logger对象，或者直接使用logging模块的默认Logger
logger = logging.getLogger('scanner')
# 定义一个Session对象，用于复用连接和提高性能
session = requests.Session()
seen_lines = set() # 创建一个空集合,保存服务器的所有url
class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.text = Label(self, text='Please enter the URL you want to detect:')
        str1 = StringVar()
        self.input01 = Entry(self, width=40, textvariable=str1)
        str1.set(TARGET)
        btn01 = Button(self, text='input', command=self.calc)
        #绑定回车键
        self.input01.bind('<Return>', lambda event: self.calc())
        btnQuit = Button(self, text='Quit', command=self.quit)
        # 带滚动条的文本框
        self.word = Text(self, width=60, height=30, bg='pink')

        self.text.grid(row=0, column=0)
        self.input01.grid(row=0, column=1)
        # 左下角
        btn01.grid(row=0, column=2)  # , sticky=W)
        btnQuit.grid(row=3, column=2)  # , sticky=E)
        #文本框占满整个窗口,columnspan=3
        self.word.grid(row=1, column=0, columnspan=3)
        #self.word.insert(1.0, 'hello world')

    def calc(self):
        #messagebox.showinfo('Message', 'Hello World')
        words = get_words() # 获取根路径下所有单词，并添加到队列中
        urllist=dir_bruter(words,)
        self.word.delete(1.0,END)#清空文本框
        #将url写入文本框，每行一个
        for url in urllist:
            self.word.insert(END, url+'\n')

    def quit(self) -> None:
        return super().quit()
def get_words(resume=None):
    def extend_words(word):
        # 使用os.path.splitext()函数来判断文件名是否有点号，而不是使用字符串切片
        #ext = os.path.splitext(word)
        #if ext[-1]:
        #    words.put(f'{word}')
       # else:
        words.put(f'{word}')
        #for extension in EXTENSIONS:
        #    words.put(f'/{word}{extension}')

    with open(WORDLIST) as f:
        raw_words = f.read()

    found_resume = False
    words = queue.Queue()
    for word in raw_words.split():
        if resume is not None:
            if found_resume:
                extend_words(word)
            elif word == resume:
                found_resume = True
                logger.info(f'Resuming wordlist from : {resume}')
        else:
            logger.debug(word)
            extend_words(word)
    return words


def dir_bruter(words):
    '''
    words:tuple,字典的排列组合
    '''
    urllist=[]
    headers = {'User-Agent': AGENT}
    p = permutations(words.queue,DirectoryLevel)   #2为目录遍历层数 
    p = list(p) # convert p to a list of tuples
    for t in p:
        s = "/".join(t)
        words.put(s) # put each tuple into q
    while not words.empty():
        url = f'{TARGET}{words.get()}'
        if '.php' in url:#过滤重复后缀
            #todo regex 匹配，是得url只有一个。
            url = url.split(".php", 1)[0] + ".php"
        #print("url:",url)
        if url not in seen_lines: # 如果这一行没有出现过
            seen_lines.add(url) # 添加到集合中
            try:
                # 使用Session对象来发送请求，而不是每次都创建新的请求对象
                r = session.get(url, headers=headers)
            except requests.exceptions.ConnectionError:
                logger.error('x')
                continue

            if r.status_code == 200: # 如果状态码为200，则表示找到了一个有效的路径
                #开发时使用的日志方式
                #logger.info(f'\nSuccess found({r.status_code}: {url})')
                #使用时的日志方式
                logger.info(f'\n {url}')
                print(f'\nSuccess found({r.status_code}: {url})')
                urllist.append(url)
                # 如果路径以/结尾，则表示是一个子目录，则继续对其进行扫描

            elif r.status_code == 404: # 如果状态码为404，则表示没有找到该路径
                #logger.debug('.')
                #logger.info(f'\nNot found({r.status_code}: {url})')
                pass
            else: # 其他状态码则记录到日志中供参考
                #logger.warning(f'{r.status_code} => {urls}')
                pass
    return urllist
def center(root):# Center the window
    root.update_idletasks()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    root.geometry("%dx%d+%d+%d" % (size + (x, y)))


app = Application()
app.master.title('web scanner')
center(app.master)
app.mainloop()
