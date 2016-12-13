# -*- coding:utf-8 -*-

import argparse
import jubatus
from jubatus.common import Datum
import json
import os

def make_datum(title = None, text = None, picture = None):
    d = Datum()
    if title:
        d.add_string("title", title)
    if text:
        d.add_string("text", text)
    if picture:
        with open(picture, "rb") as f:
            d.add_binary("img", f.read())
    return d
            
def make_client(address="localhost", port=9199, name="irasutoya", timeout=0):
    return jubatus.Recommender(address, port, name, timeout)

def parse_json(filename):
    with open(filename) as f:
        j = json.load(f)
        title = j["title"]
        text = j["text"]
        img_src = j["img"]
        img_name = img_src.split("/")[-1]
        return title, text, img_src, img_name

def train_jubatus(year, month, args):
    '''
    特定のyear, monthディレクトリ内の全てのデータを学習させる
    '''
    cl = make_client()
    data_dir = os.path.join("article", str(year), str(month))
    print("training {}".format(data_dir))
    img_dir = os.path.join("imgs", str(year), str(month))
    try:
        files = os.listdir(data_dir)
    except FileNotFoundError:
        print("{} can't be found".format(data_dir) )
        return
    for f in files:
        title, text, img_src, img_name = parse_json(os.path.join(data_dir, f))
        row_id = "{}_{}_{}".format(year, month, f.split(".")[0]) # year_month_blog-post_* というid
        if not args.title:
            title = None
        if not args.body:
            text = None
        if args.img:
            img_file = os.path.join(img_dir, img_name)
        else:
            img_file = None
        d = make_datum(title, text, img_file)
        cl.update_row(row_id, d)
        print("updated {}".format(row_id))
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--img", action="store_true", default= False, help="use img for train")
    parser.add_argument("-t", "--title", action="store_true", default= False, help="use title for train")
    parser.add_argument("-b", "--body", action="store_true", default= False, help="use body text for train")
    return parser.parse_args()
    
    
if __name__ == "__main__":
    args = parse_args()
    year=["2013"]

    #year = ["2012", "2013", "2014", "2015", "2016"]

    month = ["01", "02", "03", "04", "05", "06",
             "07", "08", "09", "10", "11", "12"]
    for y in year:
        for m in month:
            train_jubatus(y, m, args)
    
    cl = make_client()
    cl.save("irasutoya")
