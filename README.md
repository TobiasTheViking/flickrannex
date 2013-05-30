flickrannex
=========

Hook program for gitannex to use flickr as backend

# Requirements:

    python2

Credit for the flickr api interface goes to: http://stuvel.eu/flickrapi
Credit for the png library goes to: https://github.com/drj11/pypng
Credit for the png tEXt patch goes to: https://code.google.com/p/pypng/issues/detail?id=65

# Install
Clone the git repository in your home folder.

    git clone git://github.com/TobiasTheViking/flickrannex.git 

This should make a ~/flickrannex folder

# Setup

Run the program once to set it up. 

    cd ~/flickrannex; python2 flickrannex.py

After the setup has finished, it will print the git-annex configure lines.

# Notes

## Unencrypted mode
The photo name on flickr is currently the GPGHMACSHA1 version.

## Encrypted mode
The current version base64 encodes all the data, which results in ~35% larger filesize.

I might look into yyenc instead. I'm not sure if it will work in the tEXt field.

# Todo
Pagination.
