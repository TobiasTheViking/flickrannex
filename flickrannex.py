#!/usr/bin/env python2
import os
import sys
import json
import time
import inspect

conf = False

plugin = "flickrannex"

pwd = os.path.dirname(__file__)
if not pwd:
    pwd = os.getcwd()
sys.path.append(pwd + '/lib')
sys.path.append(pwd + '/lib/pypng/')

if "--dbglevel" in sys.argv:
    dbglevel = int(sys.argv[sys.argv.index("--dbglevel") + 1])
else:
    dbglevel = 0

import CommonFunctions as common
import flickrapi
import png

api_key = 'e431589a186b0a83dcc2df1e30cfa7f7'
api_secret = 'd78fc11e3a8832ef'
flickr = flickrapi.FlickrAPI(api_key, api_secret)
user_id = False
if not os.path.exists(pwd + "/temp"):
    os.mkdir(pwd + "/temp")
import base64
def login(uname, pword):
    common.log(uname)
    (token, frob) = flickr.get_token_part_one(perms='delete')
    if not token: raw_input("Press ENTER after you authorized this program")
    flickr.get_token_part_two((token, frob))
    global user_id
    user_id = flickr.people_findByEmail(find_email=uname)
    user_id = user_id[0].attrib["nsid"]
    common.log("Done: " + repr(token) + " - " + repr(frob) + " - " + repr(user_id))

def postFile(subject, filename, folder):
    common.log("%s to %s - %s" % ( filename, repr(folder), subject))
    def func(progress, done):
        if done:
            print "Done uploading"
        else:
            print "At %s%%" % progress

    width, height, pixels, meta, text = png.Reader(filename=pwd + "/logo_small.png").read()

    f = open(pwd + "/temp/encoded-" + subject, 'wb')
    text = readFile(filename, "rb")
    text = base64.b64encode(text)
    
    w = png.Writer(width, height, text={"data": text})
    w.write(f, pixels)
    f.close()

    res = flickr.upload(filename=pwd + "/temp/encoded-" + subject, is_public=0, title=subject, description=folder, callback=func)
    if res:
        if isinstance(folder, int):
            flickr.photosets_addPhoto(photoset_id=folder, photo_id=res[0].text)
        else:
            flickr.photosets_create(title=folder, primary_photo_id=res[0].text)

    os.unlink(pwd + "/temp/encoded-" + subject)
    if res:
        common.log("Done: " + repr(res))
    else:
        sys.exit(1)

def checkFile(subject, folder):
    common.log(subject + " - " + repr(folder) + " - " + repr(user_id))

    file = False
    photos = flickr.photosets_getPhotos(photoset_id=folder, per_page=500)
    for s in photos.find('photoset').findall('photo'):
        title = s.attrib["title"]
        common.log("Found title: " + repr(title), 3)
        if title == subject:
            file = title
            break

    if file:
        common.log("Found: " + repr(file))
        print(subject)
    else:
        common.log("Failure")

def getFile(subject, filename, folder):
    common.log(subject)

    file = False
    photos = flickr.photosets_getPhotos(photoset_id=folder, per_page=500)
    for s in photos.find('photoset').findall('photo'):
        title = s.attrib["title"]
        common.log("Found title: " + repr(title), 3)
        if title == subject:
            file = s.attrib["id"]
            break

    if file:
        url = flickr.photos_getSizes(photo_id=file)
        url = url.find('sizes').findall('size')
        url = url[len(url) -1]

        common.log("Using: " + repr(url.attrib["label"]) + " - " + repr(url.attrib["source"]), 3)
        
        res = common.fetchPage({"link": url.attrib["source"]})

        r=png.Reader(bytes=res["content"])
        width, height, pixels, meta, text = r.read()
        common.log("BLA: " + repr(text)[0:20])
        text = base64.b64decode(text["data"])
        common.log("BLA: " + repr(text)[0:20])
        saveFile(filename, text, "wb")

        common.log("Done")
    else:
        common.log("Failure")


def deleteFile(subject, folder):
    common.log(subject)

    file = False
    photos = flickr.photosets_getPhotos(photoset_id=folder, per_page=500)
    for s in photos.find('photoset').findall('photo'):
        title = s.attrib["title"]
        common.log("Found title: " + repr(title), 3)
        if title == subject:
            file = s.attrib["id"]
            break

    common.log("file: " + repr(file))

    if file:
        res = flickr.photos_delete(photo_id=file)
        common.log("Done: " + repr(res))
    else:
        common.log("Failure")

def readFile(fname, flags="r"):
    common.log(repr(fname) + " - " + repr(flags))

    if not os.path.exists(fname):
        common.log("File doesn't exist")
        return False
    d = ""
    try:
        t = open(fname, flags)
        d = t.read()
        t.close()
    except Exception as e:
        common.log("Exception: " + repr(e), -1)

    common.log("Done")
    return d

def saveFile(fname, content, flags="w"):
    common.log(fname + " - " + str(len(content)) + " - " + repr(flags))
    t = open(fname, flags)
    t.write(content)
    t.close()
    common.log("Done")

def main():
    global conf
    args = sys.argv

    ANNEX_ACTION = os.getenv("ANNEX_ACTION")
    ANNEX_KEY = os.getenv("ANNEX_KEY")
    ANNEX_HASH_1 = os.getenv("ANNEX_HASH_1")
    ANNEX_HASH_2 = os.getenv("ANNEX_HASH_2")
    ANNEX_FILE = os.getenv("ANNEX_FILE")
    envargs = []
    if ANNEX_ACTION:
        envargs += ["ANNEX_ACTION=" + ANNEX_ACTION]
    if ANNEX_KEY:
        envargs += ["ANNEX_KEY=" + ANNEX_KEY]
    if ANNEX_HASH_1:
        envargs += ["ANNEX_HASH_1=" + ANNEX_HASH_1]
    if ANNEX_HASH_2:
        envargs += ["ANNEX_HASH_2=" + ANNEX_HASH_2]
    if ANNEX_FILE:
        envargs += ["ANNEX_FILE=" + ANNEX_FILE]
    common.log("ARGS: " + repr(" ".join(envargs + args)))

    if not os.path.exists(pwd + "/flickrannex.conf"):
        saveFile(pwd + "/flickrannex.conf", json.dumps({"uname": "", "folder": "gitannex", "pword": ""}))
        common.log("no flickrannex.conf file found. Creating empty template")
        sys.exit(1)

    conf = readFile(pwd + "/flickrannex.conf")
    try:
        conf = json.loads(conf)
    except Exception as e:
        common.log("Traceback EXCEPTION: " + repr(e))
        common.log("Couldn't parse conf: " + repr(conf))
        conf = {}

    common.log("Conf: " + repr(conf), 2)

    if "uname" not in conf or "pword" not in conf or ("uname" in conf and conf["uname"] == "") or ("pword" in conf and conf["pword"] == ""):
        common.log("No username or password found in config")
        sys.exit(1)

    login(conf["uname"], conf["pword"])
    ANNEX_FOLDER = conf["folder"]
    sets = flickr.photosets_getList(user_id=user_id, per_page=500)
    # Handle multiple pages sanely
    for s in sets.find('photosets').findall('photoset'):
        if s[0].text.find(conf["folder"]) > -1:
            ANNEX_FOLDER = int(s.attrib["id"])

    if "store" == ANNEX_ACTION:
        postFile(ANNEX_KEY, ANNEX_FILE, ANNEX_FOLDER)
    elif "checkpresent" == ANNEX_ACTION:
        checkFile(ANNEX_KEY, ANNEX_FOLDER)
    elif "retrieve" == ANNEX_ACTION:
        getFile(ANNEX_KEY, ANNEX_FILE, ANNEX_FOLDER)
    elif "remove" == ANNEX_ACTION:
        deleteFile(ANNEX_KEY, ANNEX_FOLDER)
    else:
        common.log("ERROR")
        sys.exit(1)

t = time.time()
common.log("START")
if __name__ == '__main__':
    main()
common.log("STOP: %ss" % int(time.time() - t))
