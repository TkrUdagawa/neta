from bs4 import BeautifulSoup
import urllib.request
import os
import json

def scrape(contents):
    soup = BeautifulSoup(contents.read())
    title = get_title(soup)
    try:
        img_source, text = get_content(soup)
        return title, text, img_source
    except UnboundLocalError:
        raise


def get_content(soup):
    try:
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
    except UnboundLocalError:
        raise
        

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
    parser.add_argument("-f", "--input", action="store",
                        default = None,
                        help="入力urls")
    parser.add_argument("-o", "--oks", action="store",
                        default=None,
                        help="skipするURLのファイルを与える")
    args = parser.parse_args()
    if args.input:
        print("getting urls from local file")
        with open(args.input) as f:
            urls = f.readlines()
    else:
        print("getting urls from website")
        urls = []
        request = "http://www.irasutoya.com/2012/02"
        with open("urls.txt", "a") as w:
            get_urls(urls, request, w)

    oks_r = set()
    if args.oks:
        with open(args.oks) as oks:
            for line in oks:
                oks_r.add(line.strip())

    with open("ng_urls.txt", "a") as ng, open("ok_urls.txt", "a") as ok_w:
        for url in urls:
            url = url.strip()
            if not "blog-post_" in url:
                print("skip: {}".format(url))
                continue
            try:
                if not url in oks_r:
                    print("request: {}".format(url))
                    content = urllib.request.urlopen(url)

                else:
                    print("url({}) is in ok_url".format(url))
                    continue

            except ConnectionResetError:
                ng.write("{}\n".format(url))
                print("skip: {}".format(url))
                continue
            print("scrape: {}".format(url))

            try:
                title, text, img_source = scrape(content)
            except UnboundLocalError:
                print("ng scraping {}".format(url))
                ng.write("{}\n".format(url))
                continue

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
            ok_w.write("{}\n".format(url))
        print("complete!")
                

