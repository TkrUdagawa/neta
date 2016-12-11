from bs4 import BeautifulSoup
import urllib.request
import os
import json

def scrape(contents):
    soup = BeautifulSoup(contents.read())
    title = get_title(soup)
    img_source, text = get_content(soup)
    return title, text, img_source

def get_content(soup):
    e = soup.find("div", class_="entry")
    l = e.find_all("div", class_="separator")
    texts = []
    for s in l:
        if not s.a is None :
            if not s.a.img is None:
                img_source = s.a.img["src"].strip()
        else:
            text = s.text.strip()
            texts.append(text)
    return img_source, "".join(texts)

def get_title(soup):
    return soup.find("div", class_="title").text.strip()


def get_urls(urls,  req, w):
    c = urllib.request.urlopen(req)
    print(c)
    if c is None:
        print("partialy returning urls")
        return urls
    s = BeautifulSoup(c.read())
    imgs = s.find_all("div", class_="boxim")
    for img in imgs:
        urls.append(img.a["href"])
        w.write("{}\n".format(img.a["href"]))
    p = s.find("a", class_="blog-pager-newer-link")
    next_url = p["href"]
    print ("next_url", next_url)
    if not "2016-12-11" in next_url:
        get_urls(urls, next_url, w)
    return urls

def write_data(title, text, img_source, year, month, name):
    with open(os.path.join("article",
                           str(year), 
                           str(m), 
                           "{}.json".format(name)), "w") as f:
                f.write(json.dumps({"title": title, 
                                    "text": text,
                                    "img": img_source}))
    i = urllib.request.urlopen(img_source)
    i_name = img_source.split("/")[-1]
    with open(os.path.join("imgs",
                           str(year),
                           str(m),
                           i_name), "wb") as f:
        f.write(i.read())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", action="store_false",
                        default=True,
                        help="ダウンロード対象のURLを取得しない場合、このオプションを指定する")
    parser.add_argument("-f", "--input", action="store",
                        default = "urls.txt",
                        help="入力urls")
    args = parser.parse_args()
    if args.url:
        print("getting urls from website")
        urls = []
        request = "http://www.irasutoya.com/2012/02"
        with open("urls.txt", "w") as w:
            get_urls(urls, request, w)
    else:
        print("getting urls from local file")
        with open(args.input) as f:
            urls = f.readlines()
    with open("ng_urls.txt", "w") as f:
        for url in urls:
        
            if not "blog-post_" in url:
                print("skip: {}".format(url))
                continue
            print("request: {}".format(url))
            try:
                content = urllib.request.urlopen(url)
            except ConnectionResetError:
                f.write("{}\n".format(url))
                print("skip: {}".format(url))
                continue
            print("scrape: {}".format(url))
            title, text, img_source = scrape(content)
            t = url.split("/")
            y = t[3]
            m = t[4]
            u = t[5].split(".")[0]
            print(title, text, img_source)
            try:
                os.makedirs("article/{}/{}".format(y, m))
            except FileExistsError:
                pass
            try:
                os.makedirs("imgs/{}/{}".format(y, m))
            except FileExistsError:
                pass
            write_data(title, text, img_source, y, m, u)
        print("complete!")
                

