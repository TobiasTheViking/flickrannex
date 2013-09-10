#!/usr/bin/env python2
import os
import sys
import json
import time
import inspect

conf = False
version = "0.1.7"
plugin = "flickrannex-" + version

pwd = os.path.dirname(__file__)
if not pwd:
    pwd = os.getcwd()
sys.path.append(pwd + '/lib')
sys.path.append(pwd + '/lib/pypng/')

if "--dbglevel" in sys.argv:
    dbglevel = int(sys.argv[sys.argv.index("--dbglevel") + 1])
else:
    dbglevel = 0

if "--directories-as-tags" in sys.argv:
    dirtags = 1
else:
    dirtags = 0

import CommonFunctions as common
import flickrapi
import png

api_key = "2f6b468927a824c00b33c4672b10d24e"
api_secret = "e28467365581abd4"

flickr = flickrapi.FlickrAPI(api_key, api_secret)
user_id = False
if not os.path.exists(pwd + "/temp"):
    os.mkdir(pwd + "/temp")
import base64

def login(uname):
    common.log(uname)
    (token, frob) = flickr.get_token_part_one(perms='delete')
    if not token: 
        try:
            raw_input("Press ENTER after you authorized this program")
        except Exception as e:
            common.log("Sleeping for 60s while waiting for user to authorize program: " + repr(e))
            time.sleep(60)
    flickr.get_token_part_two((token, frob))
    global user_id
    user_id = flickr.people_findByEmail(find_email=uname)
    user_id = user_id[0].attrib["nsid"]
    common.log("Done: " + repr(token) + " - " + repr(frob) + " - " + repr(user_id))

def verifyFileType(filename):
    common.log(filename)
    status = False
    fname, ext = os.path.splitext(os.path.basename(filename))
    # Video gets converted to flv.
    # pdf gets (Horribly badly) converted to jpg
    if ext.lower() in [".jpg", ".jpeg", ".gif", ".png"]:
        common.log("Filetype can be uploaded: " + ext)
        status = True

    common.log("Done: " + repr(status))
    return status

def postFile(subject, filename, folder, git_top_level):
    common.log("%s to %s - %s" % ( filename, repr(folder), subject))

    if git_top_level:
        common.log("git top level directory: %s" % git_top_level)

    def func(progress, done):
        common.log("func: %s - %s" % (repr(progress), repr(done)))
        if len(done):
            print("Done uploading")
        else:
            print("At %s%%" % progress)

    width, height, pixels, meta, text = png.Reader(filename=pwd + "/logo_small.png").read()
    upper_limit = 40234050
    if os.path.getsize(filename) > upper_limit:
        print("%s size: %s more than %s. Skipping" % ( filename, os.path.getsize(filename), upper_limit))
        sys.exit(1)

    if conf["encrypted"]:
        tfile = pwd + "/temp/encoded-" + subject
        f = open(tfile, 'wb')
        text = readFile(filename, "rb")
        text = base64.b64encode(text)
    
        w = png.Writer(width, height, text={"data": text})
        w.write(f, pixels)
        f.close()
    else:
        tfile = filename

    # If we want to use directories as tags...
    tags = []
    if dirtags:
        dirpath = os.path.relpath(os.path.dirname(tfile), git_top_level)

        # Thank you StackOverflow
        #   http://stackoverflow.com/questions/3167154/how-to-split-a-dos-path-into-its-components-in-python
        while 1:
            dirpath,dir = os.path.split(dirpath)

            if dir != "":
                tags.append(dir)
            else:
                break

        # Handle the case of indirect repos
        #  - indirect repos have ".git" as the first subdirectory (never will happen for a direct repo)
        #  - this will mean that don't know what the filename is in that case, so don't use any tags
        if (len(tags) > 0) and (tags[len(tags) - 1] == ".git"):
            tags = []

        common.log("Tags added to photo" + '"' + '" "'.join(tags) + '"')

    common.log("Uploading: " + tfile)

    res = flickr.upload(filename=tfile, is_public=0, title=subject,
                        description=os.path.basename(tfile), tags = '"' + '" "'.join(tags) + '"',
                        callback=func)

    if len(res):
        if isinstance(folder, int):
            flickr.photosets_addPhoto(photoset_id=folder, photo_id=res[0].text)
        else:
            flickr.photosets_create(title=folder, primary_photo_id=res[0].text)

    if conf["encrypted"]:
        os.unlink(pwd + "/temp/encoded-" + subject)

    if len(res):
        common.log("Done: " + repr(res))
    else:
        print("Failed to store: " + repr(res))
        sys.exit(1)

def checkFile(subject, folder):
    common.log(subject + " - " + repr(folder) + " - " + repr(user_id))

    if not isinstance(folder, int):
        common.log("No set exists, thus no files exists: " + repr(type(folder)))
        #return False

    org_sub = subject

    file = False
    page=1
    while not file:
        photos = flickr.photosets_getPhotos(photoset_id=folder, per_page=500, page=page)
        photos = photos.find("photoset")
        for s in photos.findall('photo'):
            title = s.attrib["title"]
            common.log("Found title: " + repr(title), 3)
            if title == subject:
                file = title
                break
        if int(photos.attrib["pages"]) > page:
            page +=1
            common.log("Trying page: " + repr(page))
        else:
            common.log("Error, found nothing:" + repr(photos))
            common.log("Error, found nothing:" + repr(photos.attrib))
            break

    if file:
        common.log("Found: " + repr(file))
        print(org_sub)
        return True
    else:
        common.log("Failure")
        return False

def getFile(subject, filename, folder):
    common.log(subject)

    file = False
    page=1
    while not file:
        photos = flickr.photosets_getPhotos(photoset_id=folder, per_page=500, page=page)
        photos = photos.find("photoset")
        for s in photos.findall('photo'):
            title = s.attrib["title"]
            common.log("Found title: " + repr(title), 2)
            if title == subject:
                common.log("Found title2: " + repr(title), 0)
                file = s.attrib["id"]
                break
        if int(photos.attrib["total"]) > page:
            page +=1
            common.log("Trying page: " + repr(page) + " - " + repr(photos.attrib))
        else:
            common.log("Error. found nothing:" + repr(photos))
            common.log("Error. found nothing:" + repr(photos.attrib))
            break

    if file:
        url = flickr.photos_getSizes(photo_id=file)
        url = url.find('sizes').findall('size')
        url = url[len(url) -1]

        common.log("Using: " + repr(url.attrib["label"]) + " - " + repr(url.attrib["source"]), 3)
        
        res = common.fetchPage({"link": url.attrib["source"]})

        if "encrypted" in conf and conf["encrypted"]:
            r=png.Reader(bytes=res["content"])
            width, height, pixels, meta, text = r.read()
            text = base64.b64decode(text["data"])
            saveFile(filename, text, "wb")
        else:
            saveFile(filename, res["content"], "wb")

        common.log("Done")
    else:
        common.log("Failure")


def deleteFile(subject, folder):
    common.log(subject + " - " + repr(folder))

    file = False
    page=1
    while not file:
        photos = flickr.photosets_getPhotos(photoset_id=folder, per_page=500)
        photos = photos.find('photoset')
        for s in photos.findall('photo'):
            title = s.attrib["title"]
            common.log("Found title: " + repr(title), 0)
            if title == subject:
                file = s.attrib["id"]
                break
        if int(photos.attrib["pages"]) > page:
            page +=1
            common.log("Trying page: " + repr(page))
        else:
            common.log("Error. found nothing:" + repr(photos))
            common.log("Error. found nothing:" + repr(photos.attrib))
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
    GIT_TOP_LEVEL = os.getenv("GIT_TOP_LEVEL")

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
    if GIT_TOP_LEVEL:
        envargs += ["GIT_TOP_LEVEL=" + GIT_TOP_LEVEL]
    common.log("ARGS: " + repr(" ".join(envargs + args)))


    conf = readFile(pwd + "/flickrannex.conf")
    try:
        conf = json.loads(conf)
    except Exception as e:
        common.log("Traceback EXCEPTION: " + repr(e))
        common.log("Couldn't parse conf: " + repr(conf))
        conf = {"folder": "gitannex"}

    common.log("Conf: " + repr(conf), 2)
    changed = False
    if "uname" not in conf:
        print("Please make sure your email address has been associated flickr.")
        conf["uname"] = raw_input("Please enter your flickr email address: ")
        common.log("e-mail set to: " + conf["uname"])
        changed = True

    if "encrypted" not in conf:
        conf["encrypted"] = "?"
        while (conf["encrypted"].lower().find("y") == -1 and conf["encrypted"].lower().find("n") == -1 ):
            conf["encrypted"] = raw_input("Should uploaded files be encrypted [yes/no]: ")
        conf["encrypted"] = conf["encrypted"].lower().find("y") > -1
        common.log("encryption set to: " + repr(conf["encrypted"]))
        changed = True

    login(conf["uname"])
    ANNEX_FOLDER = conf["folder"]
    page=1
    while ANNEX_FOLDER == conf["folder"]:
        common.log("Photoset %s searching for %s" % (repr(ANNEX_FOLDER), repr(conf["folder"])))
        sets = flickr.photosets_getList(per_page=500)
        sets = sets.find('photosets')
        for s in sets.findall('photoset'):
            common.log("Photoset %s found: %s" % (s[0].text, repr(s)))
            if s[0].text == conf["folder"]:
                common.log("Photoset %s found: %s Setting" % (s[0].text, repr(s[0].text), repr(s.attrib["id"])))
                ANNEX_FOLDER = int(s.attrib["id"])
                break
        if int(sets.attrib["pages"]) > page:
            page +=1
            common.log("Trying page: " + repr(page))
        else:
            common.log("Error. found nothing:" + repr(sets.attrib))
            break
        
    if not conf["encrypted"] and ANNEX_KEY and not verifyFileType(ANNEX_KEY):
        print("Unencrypted flickr can only accept picture and video files")
        sys.exit(1)

    if ANNEX_FILE and os.path.exists(ANNEX_FILE) and os.path.getsize(ANNEX_FILE) > 31457280:
        print("flickr won't accept files larger than ~30mb")
        sys.exit(1)

    if "store" == ANNEX_ACTION:
        postFile(ANNEX_KEY, ANNEX_FILE, ANNEX_FOLDER, GIT_TOP_LEVEL)
    elif "checkpresent" == ANNEX_ACTION:
        checkFile(ANNEX_KEY, ANNEX_FOLDER)
    elif "retrieve" == ANNEX_ACTION:
        getFile(ANNEX_KEY, ANNEX_FILE, ANNEX_FOLDER)
    elif "remove" == ANNEX_ACTION:
        deleteFile(ANNEX_KEY, ANNEX_FOLDER)
    elif changed or True:
        if user_id:
            print("Program sucessfully setup")
            if conf["encrypted"]:
                encryption = "shared"
            else:
                encryption = "none"
            setup = '''
Please run the following commands in your annex directory:

git config annex.flickr-hook '/usr/bin/python2 %s/flickrannex.py'

# If you have a direct mode repository and want to use your directores as tags, use this hook instead
git config annex.flickr-hook 'GIT_TOP_LEVEL=`git rev-parse --show-toplevel` /usr/bin/python2 %s/flickrannex.py --directories-as-tags'

git annex initremote flickr type=hook hooktype=flickr encryption=%s
git annex describe flickr "the flickr library"
git annex content flickr exclude=largerthan=30mb
''' % (os.getcwd(), os.getcwd(), encryption)
            print setup
            common.log("Saving flickrannex.conf", 0)
            saveFile(pwd + "/flickrannex.conf", json.dumps(conf))
        else:
            print("Error during setup. Please try again")
    else:
        print("ERROR")
        sys.exit(1)

t = time.time()
common.log("START")
if __name__ == '__main__':
    main()
common.log("STOP: %ss" % int(time.time() - t))
