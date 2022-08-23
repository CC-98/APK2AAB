from genericpath import exists
import os
import re
from powershell import *


# 当前目录
P_curposition = os.getcwd()
P_SIGN_CONFIG = P_curposition+"/config.ini"
# 执行命令创建apks
def F_powershell_run_bundle_aab():
    File_readConfig = open(P_SIGN_CONFIG,"r",encoding="utf-8")
    for eachline in File_readConfig:
        if(re.search("keystore",eachline)):
            keystorepath = eachline.split("=")[1][:-1]
        if(re.match("alias=",eachline)):
            aliasName = eachline.split("=")[1][:-1]
        if(re.match("pswd",eachline)):
            pswd = eachline.split("=")[1][:-1]
        if(re.search("aliaspswd",eachline)):
            aliaspswd = eachline.split("=")[1][:-1]
    with PowerShell('GBK') as ps:
        outs, errs = ps.run('java -jar bundletool-all-1.7.0.jar build-apks --local-testing --bundle='+F_getaabName()+' --output='+F_getaabName()[:-4]+'.apks --ks='+keystorepath+' --ks-pass=pass:'+pswd+' --ks-key-alias='+aliasName+' --key-pass=pass:'+aliaspswd+' --overwrite')
    print('error:', os.linesep, errs)
    print('output:', os.linesep, outs)
    F_install_apks()


# 需要安装的aab名称
def F_getaabName():
    matchFileNameList=[]
    FileList = os.listdir(P_curposition)
    for file in FileList:
        if(os.path.splitext(file)[1]=='.aab'):
            matchFileNameList.append(file)
    return P_curposition+"/"+matchFileNameList[0]


# 安装apks
def F_install_apks():
        with PowerShell('GBK') as ps:
            outs, errs = ps.run('java -jar bundletool-all-1.7.0.jar install-apks --apks='+F_getaabName()[:-4]+'.apks')
        print('error:', os.linesep, errs)
        print('output:', os.linesep, outs)


F_powershell_run_bundle_aab()
# F_install_apks()