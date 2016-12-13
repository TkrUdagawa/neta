# -*- coding:utf-8 -*-

import argparse
import jubatus
from jubatus.common import Datum

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

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--img", action="store", default= None, help="path to img file")
    parser.add_argument("-t", "--title", action="store", default= None, help="title string")
    parser.add_argument("-b", "--body", action="store", default= None, help="body string")
    parser.add_argument("-d", "--id", action="store", default=None, help="id of blog-post")
    parser.add_argument("-m", "--method", action="store", required=True, choices=["id", "datum"], help="")
    return parser.parse_args()

def make_client(address="localhost", port=9199, name="irasutoya", timeout=0):
    return jubatus.Recommender(address, port, name, timeout)

def similar_row(args):
    cl = make_client()
    if args.method == "id":
        return cl.similar_row_from_id(args.id, 10)
    elif args.method == "datum":
        d = make_datum(args.title, args.body, args.img)
        return cl.similar_row_from_datum(d, 10)

if __name__ == "__main__":
    args = parse_args()
    print(similar_row(args))
