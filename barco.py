# -*- coding: UTF-8 -*-
import os
import os.path
import logging
import logging.config
import sys
import configparser
import time
import shutil
#import openpyxl                      # Для .xlsx
#import xlrd                          # для .xls
from   price_tools import getCellXlsx, getCell, quoted, dump_cell, currencyType, openX, sheetByName
import csv
import requests, lxml.html




def convert_csv2csv( cfg ):
    inFfileName  = cfg.get('basic', 'filename_in')
    outFfileName = cfg.get('basic', 'filename_out')
    inFile  = open( inFfileName,  'r', newline='', encoding='CP1251', errors='replace')
    outFile = open( outFfileName, 'w', newline='')
    outFields = cfg.options('cols_out')
    csvReader = csv.DictReader(inFile, delimiter=',')
    csvWriter = csv.DictWriter(outFile, fieldnames=cfg.options('cols_out'))

    print(csvReader.fieldnames)
    csvWriter.writeheader()
    recOut = {}
    for recIn in csvReader:
        for outColName in outFields :
            shablon = cfg.get('cols_out',outColName)
            for key in csvReader.fieldnames:
                if shablon.find(key) >= 0 :
                    shablon = shablon.replace(key, recIn[key])
            if outColName in('закупка','продажа'):
                if shablon.find('Звоните') >=0 :
                    shablon = '0.1'
            recOut[outColName] = shablon
        csvWriter.writerow(recOut)
    log.info('Обработано '+ str(csvReader.line_num) +'строк.')
    inFile.close()
    outFile.close()




def config_read( cfgFName ):
    cfg = configparser.ConfigParser(inline_comment_prefixes=('#'))
    if  os.path.exists('private.cfg'):     
        cfg.read('private.cfg', encoding='utf-8')
    if  os.path.exists(cfgFName):     
        cfg.read( cfgFName, encoding='utf-8')
    else: 
        log.debug('Нет файла конфигурации '+cfgFName)
    return cfg



def is_file_fresh(fileName, qty_days):
    qty_seconds = qty_days *24*60*60 
    if os.path.exists( fileName):
        price_datetime = os.path.getmtime(fileName)
    else:
        log.error('Не найден файл  '+ fileName)
        return False

    if price_datetime+qty_seconds < time.time() :
        file_age = round((time.time()-price_datetime)/24/60/60)
        log.error('Файл "'+fileName+'" устарел!  Допустимый период '+ str(qty_days)+' дней, а ему ' + str(file_age) )
        return False
    else:
        return True



def make_loger():
    global log
    logging.config.fileConfig('logging.cfg')
    log = logging.getLogger('logFile')



def processing(cfgFName):
    log.info('----------------------- Processing '+cfgFName )
    cfg = config_read(cfgFName)
    filename_out = cfg.get('basic','filename_out')
    filename_in  = cfg.get('basic','filename_in')
    if cfg.has_section('download'): filename_new = cfg.get('download','filename_new')
    
    rc_download = False
    if cfg.has_section('download'):
        rc_download = download(cfg)
    if rc_download==True or is_file_fresh( filename_in, int(cfg.get('basic','срок годности'))):
        convert_csv2csv(cfg)
    folderName = os.path.basename(os.getcwd())
    if os.name == 'nt' :
        if os.path.exists(filename_out)  : shutil.copy2(filename_out , 'c://AV_PROM/prices/' + folderName +'/'+filename_out)
        if os.path.exists('python.log')  : shutil.copy2('python.log',  'c://AV_PROM/prices/' + folderName +'/python.log')
        if os.path.exists('python.log.1'): shutil.copy2('python.log.1','c://AV_PROM/prices/' + folderName +'/python.log.1')
    


def main( dealerName):
    """ Обработка прайсов выполняется согласно файлов конфигурации.
    Для этого в текущей папке должны быть файлы конфигурации, описывающие
    свойства файла и правила обработки. По одному конфигу на каждый 
    прайс или раздел прайса со своими правилами обработки
    """
    make_loger()
    log.info('          '+dealerName )
    for cfgFName in os.listdir("."):
        if cfgFName.startswith("cfg") and cfgFName.endswith(".cfg"):
            processing(cfgFName)


if __name__ == '__main__':
    myName = os.path.basename(os.path.splitext(sys.argv[0])[0])
    mydir    = os.path.dirname (sys.argv[0])
    print(mydir, myName)
    main( myName)
