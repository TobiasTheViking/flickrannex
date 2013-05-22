megaannex
=========

Hook program for gitannex to use flickr as backend

# Requirements:

    python2

Credit for the flickr api interface goes to: http://stuvel.eu/flickrapi
Credit for the png library goes to: https://github.com/drj11/pypng
Credit for the png tEXt patch goes to: https://code.google.com/p/pypng/issues/detail?id=65

## Install
Clone the git repository in your home folder.

    git clone git://github.com/TobiasTheViking/flickrannex.git 

This should make a ~/flickrannex folder

## Setup
Run the program once to make an empty config file

    cd ~/flickrannex; python2 flickrannex.py

Edit the flickrannex.conf file. Add your flickrusername, password and folder(set) name.

## Commands for gitannex:

    git config annex.flickr-hook '/usr/bin/python2 ~/flickrannex/flickrannex.py'
    git annex initremote flickr type=hook hooktype=flickr encryption=shared
    git annex describe flickr "the flickr library"

## Notes
The current version base64 encodes all the data, which results in ~35% larger filesize.

I might look into yyenc instead. I'm not sure if it will work in the tEXt field.
