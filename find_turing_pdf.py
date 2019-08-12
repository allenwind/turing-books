import requests
import re
import threading
import queue

URL = re.compile('book/\d{1,}')

url_format = 'http://www.ituring.com.cn/book?tab=book&sort=hot&page={}'
url_book = 'http://www.ituring.com.cn/{}'

state = '样书兑换'

MAX = 58

page = set()

htmls = []
urls = set()

for page in range(MAX):
    url = url_format.format(page)
    htmls.append(requests.get(url).text)
    print(page)

for html in htmls:
    for item in URL.findall(html):
        urls.add(item)


s = threading.Semaphore(15)

def task(url, q, s):
    try:
        r = requests.get(url).text
        t = q.put((url, r))
        print(url, ' is ok')
    except Exception as err:
        print(err)
    finally:
        s.release()

books = queue.Queue()
for url in urls:
    s.acquire()
    url = url_book.format(url)
    t = threading.Thread(target=task, args=(url, books, s))
    t.start()
    

def makedown(html):
    pattern = '[{}]({})\r\n'
    title = re.compile('(?<=<title>).+(?=</title>)')
    
    result = []
    for url, data in html:
        if '样书兑换' in data:
            bookname = title.findall(data)[0]
            bookname, _ = bookname.split('-', 1)
            result.append(pattern.format(bookname, url))
        else:
            continue
    return result
