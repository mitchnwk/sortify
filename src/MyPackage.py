#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright (C) 2020 Michel Nowak <mitch@mitchnwk.com
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


import os, os.path
import exifread
import datetime
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import shutil 

# Supported files
listExt = ['.jpg', '.png', '.gif', '.bmp', '.JPG', '.BMP', '.GIF','.PNG']

def CreateLogger():
    # create logger object used to write logs
    logger = logging.getLogger()
    # set severity to debug
    logger.setLevel(logging.DEBUG)

    # create a formatter to associate time
    # and severity to each message to be written in the log
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    # create handler to redirect log to a file in 'append' mode 
    # with a backup and a maximal length to 1Mo
    if not os.path.exists('../log/activity.log'):
        os.makedirs('../log')
    
    file_handler = RotatingFileHandler('../log/activity.log', 'a', 1000000, 1)
    # add this handler to logger
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # create a second handler to redirect each log to the console
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.DEBUG)
    logger.addHandler(steam_handler)
    return logger

#Detect duplicate by computing a Hashkey
def DetectDuplicatedPics(path4pics,path2trash,mylogger):  

    dicoDupli = {}
    movedItems = 0    
    for root, dirs, files in os.walk(path4pics):
        for file in files:
            if os.path .splitext(file)[1] in listExt:
                try:
                    fileStream = open(root+os.sep+file,'rb')
                    mylogger.info('open :%s', root+os.sep+file)
                    stat = os.stat(root+os.sep+file)
                    #create a key based on file length and 100 first bytes of the file
                    #could be repplacerd by a hash computation (quite slow) : hashKey = hash(fileStream .read())
                    hashKey = str(stat.st_size) + str(fileStream.read(100))
                    mylogger.info('hashKey for %s = %s',file,hashKey)
                    fileStream.close()
                except:
                    mylogger.info('fail to open :%s', root+os.sep+file)
            
                if hashKey in dicoDupli:
                    # file already find in the dictionnary, add it to the dictionnary
                    dicoDupli[hashKey].append(root+os.sep+file)
                    mylogger.info('hash already find :%s', dicoDupli)
                    mylogger.info('%s moving to trash', file)
                    try:
                        shutil.move(root+os.sep+file,path2trash)                    
                    except:
                        mylogger.info('%s already in trash', file)
                        os.remove(root+os.sep+file)
                    movedItems+=1
                else:
                    # new file found. Add it in the dictionnary
                    dicoDupli[hashKey] = [root+os.sep+file]
                    mylogger.info('new Hash added:%s', dicoDupli)
            else:
                mylogger.info('no file found to analysis')
    return movedItems

def GetFileDateInfo(filename):

    # Read File
    open_file = open(filename, 'rb')
    print 'get date'
    tags = exifread.process_file(open_file,stop_tag='Image DateTime',details=False,debug=False)
    print 'bob'
    try:
        date_string = tags['Image DateTime']
        print 'bob2'
        date_object = datetime.datetime.strptime(date_string.values, '%Y:%m:%d %H:%M:%S')
        #date
        day = str(date_object.day).zfill(2)
        month = str(date_object.month).zfill(2)
        year = str(date_object.year)
        #time
        second = str(date_object.second).zfill(2)
        minute = str(date_object.minute).zfill(2)
        hour = str(date_object.hour).zfill(2)
        #New fileName
        output = [day,month,year,year + month + day + '_' + hour + minute + second]
        return output
    except:
        return None

def RenamePictures(path4pics,mylogger):
    #rename all remaining single files using their exif date
    NbRenamedFiles = 0
    number = [0,1,2,3,4,5,6,7,8,9]
    for root, dirs, files in os.walk(path4pics):
        for file in files:
            if os.path .splitext(file)[1] in listExt:
                extension = os.path .splitext(file)[1]
                fileName = root + os.sep + file
                # check if filename starts with a date
                #[date,sep,part2] = file.partition('_')
                #if date.isdigit():
                #    mylogger.info('fileName already has a date')
                #else:
                mylogger.info('get EXIF info for: %s', fileName)
                dateFile = GetFileDateInfo(fileName)                   
                if dateFile <> None:                        
                    NewFileName = root + os.sep + dateFile[3] + extension                                               
                    os.rename(fileName,NewFileName)
                    mylogger.info('%s renamed in :%s', fileName, NewFileName)
                    NbRenamedFiles+=1                   
                else:
                    mylogger.info('unable to retrieve EXIF info for: %s', fileName)
    return NbRenamedFiles

def MovePictures(path4pics,dest4pics,mylogger):

#Move renamed pictures  using their exif date
    NbMovedFiles = 0
    for root, dirs, files in os.walk(path4pics):
        for file in files:
            if os.path .splitext(file)[1] in listExt:
                extension = os.path .splitext(file)[1] 
                fileName = root + os.sep + file
                try:
                    #get date info 
                    dateFile = GetFileDateInfo(fileName)      
                    # compute new destination path based on Year
                    outFilePath = dest4pics + os.sep + dateFile[2]
                    newFileName = outFilePath + os.sep + file              
                    # check if destination path is existing create if not
                    if not os.path.exists(outFilePath):
                        os.makedirs(outFilePath)
                    # check if file already exists
                    if not os.path.exists(newFileName):     
                        print 'new file , ready to copy : ' + file       
                        # copy the picture to the organised structure
                        shutil.copy2(fileName,newFileName)  
                        # verify if file is the same and display output
                        print 'moved done'
                        if hash_file(fileName) == hash_file(newFileName):
                            print 'File copied with success to ' + outFilePath
                            os.remove(fileName)
                            mylogger.info('%s moved to :%s', file, outFilePath)
                            NbMovedFiles+=1                   
                        else:
                            print 'File failed to copy :( ' + file
                            mylogger.info('%s failed to be moved to :%s', fileName, outFilePath)
                    else:
                        mylogger.info('%s already exists in %s. Skipped...', fileName, outFilePath)
                except:
                    print 'File has no exif data skipped ' + file
    return NbMovedFiles

def hash_file(filename):

   # make a hash object
   h = hashlib.sha1()

   # open file for reading in binary mode
   with open(filename,'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()
