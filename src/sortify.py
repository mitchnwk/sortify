#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright (C) 2019 Michel Nowak <mitch@mitchnwk.com
## This file is part of Sortify
 

## Sortify is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.

## Sortify is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA



import MyPackage
import sys, getopt, os

__version__ = '0.1.0'
def Usage():
    print 'Usage: sortify.py -p <path4pics> -t <path2trash>'
    return
def main(argv):
    path2trash=""
    path4pics=""
    Mylogger=MyPackage.CreateLogger()
    ShortOptions = "hp:t:"
    LongOptions = ["help","path","trash"]
    try:
        opts,args = getopt.getopt(argv,ShortOptions,LongOptions)
    except getopt.error as err:
        Usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h","--help"):
            Usage()
            sys.exit()
        elif opt in ("-p","--path"):
            path4pics = arg
        elif opt in ("-t","--trash"):
            path2trash = arg
        
    #path4pics = '/home/dargo/MyDev/pics'
    #path2trash = '/home/dargo/MyDev/trash2'
    if path4pics == "" or path2trash == "":
        print "missing args"
        Usage()
        exit()
    elif path4pics == path2trash:
        print "pics path and trash path must different"
        Usage()
        exit()    
    # check if trash path is not existing; create it otherwise
    if not os.path.exists(path2trash):
        os.makedirs(path2trash)
    # check if input path is existing; break otherwise
    if not os.path.exists(path4pics):
        print "Picture directory does not exist. Please check"
        exit()
        
    NbMovedFiles = MyPackage.DetectDuplicatedPics(path4pics,path2trash,Mylogger)
    if NbMovedFiles <>0: 
        Mylogger.info('Numbed of files trashed :%s',NbMovedFiles)
    else:
        Mylogger.info('No duplicated pictures found!')
    Mylogger.info('renaming remaining file...')
    NbRenamedFiles = MyPackage.RenamePictures(path4pics,Mylogger)
    if NbRenamedFiles <>0: 
        Mylogger.info('Numbed of files renamed :%s',NbRenamedFiles)
    else:
        Mylogger.info('No file renamed!')
    return 

if __name__ == "__main__":
    main(sys.argv[1:])
