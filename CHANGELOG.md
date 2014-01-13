# Version 0.2.1
  - Add cache to file/folder lookup to speed up access to known folders, cache is not stored between runs.

# Version 0.2.0
  - Updated to external special remote protocol
  - Because of missing GIT_TOP_LEVEL no tags(directories) are added to pictures. A random filename is still provided.
  - Applied a hack within the flickrapi library(flickr.upload) to make progress actually work.
  - Setting cost to 200 for encrypted remotes. 150 for remotes with encryption=none

# Version 0.1.10
  - Refactor directories as tags
	
# Version 0.1.9
  - Refactor
  - Support --configfile 

# Version 0.1.8
  - Bugfix (set id can be long as well as int)

# Version 0.1.7
  - Allow directories to be used as tags (--directories-as-tags)
    Directories below the top level git directory are added as tags to uploads:
      /home/me/annex-photos/holidays/2013/Greenland/img001.jpg
    would get the following tags:  "holidays" "2013" "Greenland"
  - Fix minor typo

# Version 0.1.6
  - Fix pagination error
  - Print certain error messages even with debug disabled.

# Version 0.1.5
  - Exit on files larger than 30mb

# Version 0.1.4
  - Implement pagination on flickr(handle more than 500 sets/photos)

# Version 0.1.3
  - Fix issue #4

# Version 0.1.2
  - Add "associated" message when asking for flickr login credentials

# Version 0.1.1
  - Fix issue #2 (can't get through configuration, if I choose not to encrypt files)

# Version 0.1.0
  - Fix folder issue by no longer providing user_id
