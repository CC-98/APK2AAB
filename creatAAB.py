from genericpath import exists
import os
import re
import shutil
import zipfile
import getopt
import sys

# 当前目录
P_curposition = os.path.split(os.path.realpath(__file__))[0]
# 替换文件目录
P_TMP_ROOT = P_curposition+"/TMP"
P_TMP_Config = P_TMP_ROOT+"/config.ini"
P_TMP_APPBUILD_GRADLE = P_TMP_ROOT+"/appbuild.gradle"
P_TMP_TARGET_BUILD_GRADLE = P_TMP_ROOT+"/build.gradle"
P_TARGET_BUILD_GRADLE = P_curposition+"/app/build.gradle"
P_aab_path = P_curposition+"/release.zip"
P_apk_path = P_curposition+"/releaseapk.zip"
P_SIGN_CONFIG = P_curposition+"/config.ini"
P_PROJECTROOT = P_curposition+"/app/src/main/java"
P_PROJECT_LIBS = P_curposition+"/app/libs" 
P_PROJECT_RES = P_curposition+"/app/src/main/res" 
P_PROJECT_ASSETS = P_curposition+"/assets/src/main/assets" 
P_PROJECTROOT_MANIFEST = P_curposition+"/app/src/main/AndroidManifest.xml"
P_PACKAGE_NAME = ""
P_PROJECT_INNER = ""
P_Prime_Apk_Path = ""
P_AAB_PATH = P_curposition+"/app/build/outputs/bundle/release/app-release.aab"

# 入口函数
def F_init():

    # 反解apk
    F_powershell_run_d_apk()
    F_remake_config()
    F_cleanProject()
    if F_powershell_run_bundle_aab():
        F_remake_aab()
        F_powershell_run_sign_aab()



# 执行命令创建资源工程aab
def F_powershell_run_bundle_aab():
    if(os.path.isfile(P_AAB_PATH)):
        F_LOGD("cleaning build path")
        F_remove_tmp_file(P_AAB_PATH)
    F_LOGD("run task to build bundlerelease is begining")
    outs = os.system('%s\\./gradlew -p %s bundlerelease'%(P_curposition,P_curposition))
    if(outs == 0):
        return True
    return False


# 执行gradlew命令后执行的函数
def F_callBack():
    print(">>end")


# 执行命令反解apk
def F_powershell_run_d_apk():
    apkname = F_getApkName()
    outs = os.system('java -jar %s/apktool.jar d -f %s -o %s'%(P_curposition,apkname,apkname[:-4]))
    F_LOGD("dpack apk is done!")
    return 

# 获取需要反解的apk名称
def F_getApkName():
    matchFileNameList=[]
    FileList = os.listdir(P_curposition)
    for file in FileList:
        if(os.path.splitext(file)[1]=='.apk'):
            matchFileNameList.append(file)
    return P_curposition+"/"+matchFileNameList[0]

# 整理工程内容与目录
def F_cleanProject():
    # 清除并创建包名目录
    if(os.path.exists(P_PROJECTROOT)):
        shutil.rmtree(P_PROJECTROOT)
    os.mkdir(P_PROJECTROOT)
    path_dpackage  = F_getApkName()[:-4]
    path_dpackage_manifest = path_dpackage+"/AndroidManifest.xml"
    File_dpackage_manifest = open(path_dpackage_manifest,"r",encoding="utf-8")

    for eachline in File_dpackage_manifest:
        if(re.search("package=\"",eachline)):
            begin_position = re.search("package=\"",eachline).span()[1]
            cur_line = eachline[begin_position:]
            end_position = re.search("\"",cur_line).span()[0]
            P_PACKAGE_NAME = cur_line[:end_position]
            break
    package_name_list = P_PACKAGE_NAME.split(".")
    cur_project_root = P_PROJECTROOT
    for dirname in package_name_list:
        cur_project_root = cur_project_root+"/"+dirname
        os.mkdir(cur_project_root)
    P_PROJECT_INNER = cur_project_root
    File_dpackage_manifest.close()

    F_LOGD("recreat project dir is done!")
    # 创建工程目录完成

    # 调用覆写模板方法
    File_readConfig = open(P_TMP_Config,"r",encoding="utf-8")
    File_Build_gradle = open(P_TMP_APPBUILD_GRADLE,"r",encoding="utf-8")
    File_Build_gradle_content = File_Build_gradle.read() 
    File_Target_Build_gradle = open(P_TMP_TARGET_BUILD_GRADLE,"w",encoding="utf-8")
    for eachLine in File_readConfig:
        if(re.search("[-]",eachLine)):
            eachlineList = eachLine.split("[-]")
            File_Build_gradle_content = File_Build_gradle_content.replace(eachlineList[3],eachlineList[4])
    File_Build_gradle_content = File_Build_gradle_content.replace("##PACKNAME##",P_PACKAGE_NAME)
    File_Target_Build_gradle.write(File_Build_gradle_content)
    
    File_readConfig.close()
    File_Build_gradle.close()
    File_Target_Build_gradle.close()
    shutil.copyfile(P_TMP_TARGET_BUILD_GRADLE,P_TARGET_BUILD_GRADLE)

    F_LOGD("recreat tmpfile is done!")
    # 覆写模板结束

    # 替换工程文件
    # 1.替换androidmanifest.xml
    shutil.copyfile(path_dpackage_manifest,P_PROJECTROOT_MANIFEST)
    # 2.替换libs目录
    F_replace_dir(path_dpackage+"/lib",P_PROJECT_LIBS)
    # 3.替换res目录
    F_replace_dir(path_dpackage+"/res",P_PROJECT_RES)
    # 4.替换assets目录
    F_replace_dir(path_dpackage+"/assets",P_PROJECT_ASSETS)
    F_LOGD("replace libs/res/assets is done!")

# 替换目录方法
def F_replace_dir(PrimeFile,TargetFile):
    if(os.path.exists(TargetFile)):
        shutil.rmtree(TargetFile)
    if(os.path.exists(PrimeFile)):
        shutil.move(PrimeFile,TargetFile)
# 替换文件方法
def F_replace_File(PrimeFile,TargetFile):
    if(os.path.isfile(TargetFile)):
        os.remove(TargetFile)
    if(os.path.exists(PrimeFile)):
        shutil.copy(PrimeFile,TargetFile)

# 构建完整的aab
def F_remake_aab():
    F_LOGD("make complete aab is begining")
    F_replace_File(P_AAB_PATH,P_aab_path)
    F_replace_File(F_getApkName(),P_apk_path)
    F_D_zip_file(P_aab_path)
    F_D_zip_file(P_apk_path)
    F_putin_dex()
    F_putin_root()
    F_remove_tmp_files()
    F_writeAllFileToZip(P_aab_path[:-4],zipfile.ZipFile(P_aab_path,"w",zipfile.ZIP_DEFLATED))
    shutil.rmtree(P_aab_path[:-4])
    shutil.move(P_aab_path,F_getApkName()[:-4]+".aab")
    F_LOGD("make complete aab is done")

# 解压缩zip
def F_D_zip_file(file_path):
    F_LOGD("dpacking "+file_path)
    if(os.path.exists(file_path[:-4])):
        shutil.rmtree(file_path[:-4])
    with zipfile.ZipFile(file_path) as zf:
        zf.extractall(file_path[:-4])


# 放入dex
def F_putin_dex():
    apkInnerFileList = os.listdir(P_apk_path[:-4])
    for innerFile in apkInnerFileList:
        if(re.search(".dex",innerFile)):
            F_LOGD("putin dex file:"+innerFile)
            F_replace_File(P_apk_path[:-4]+"/"+innerFile,P_aab_path[:-4]+"/base/dex/"+innerFile)

# 放入root
def F_putin_root():
    F_LOGD("putin root file")
    dpack_File_path = F_getApkName()[:-4]
    apkdpackInnerFileList = os.listdir(dpack_File_path)
    for innerFile in apkdpackInnerFileList:
        if(re.search("unknown",innerFile)):
            shutil.move(dpack_File_path+"/"+innerFile,P_aab_path[:-4]+"/base/root")

# 清除临时文件夹
def F_remove_tmp_dir(dir_path):
    if(os.path.exists(dir_path)):
        F_LOGD("removing "+dir_path)
        shutil.rmtree(dir_path)

# 清除临时文件
def F_remove_tmp_file(file_path):
    if(os.path.isfile(file_path)):
        F_LOGD("removing "+file_path)
        os.remove(file_path)


# 清除临时文件
def F_remove_tmp_files():
    F_remove_tmp_dir(F_getApkName()[:-4])
    F_remove_tmp_dir(P_apk_path[:-4])
    F_remove_tmp_file(P_apk_path)
    F_remove_tmp_file(P_aab_path)

#定义一个函数，递归读取absDir文件夹中所有文件，并塞进zipFile文件中。参数absDir表示文件夹的绝对路径。
def F_writeAllFileToZip(absDir,zipFile):
    for f in os.listdir(absDir):
        absFile=os.path.join(absDir,f) #子文件的绝对路径
        if os.path.isdir(absFile): #判断是文件夹，继续深度读取。
            relFile=absFile[len(P_curposition)+1:] #改成相对路径，否则解压zip是/User/xxx开头的文件。
            zipFile.write(P_curposition+"/"+relFile,absFile[len(P_aab_path[:-4])+1:]) #在zip文件中创建文件夹
            F_writeAllFileToZip(absFile,zipFile) #递归操作
        else: #判断是普通文件，直接写到zip文件中。
            relFile=absFile[len(P_curposition)+1:] #改成相对路径
            zipFile.write(P_curposition+"/"+relFile,absFile[len(P_aab_path[:-4])+1:])
    return


# 执行命令签名aab
def F_powershell_run_sign_aab():
    F_LOGD("signing aab")
    # 获取签名参数
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
    apkname = F_getApkName()[:-4]+".aab"
    F_LOGD('java -jar .\ApkSigner.jar -keystore '+keystorepath+' -alias '+aliasName+' -pswd '+pswd+' -aliaspswd '+aliaspswd+' '+apkname)
    outs = os.system('java -jar %s\ApkSigner.jar -keystore %s -alias %s -pswd %s -aliaspswd %s %s'%(P_curposition,keystorepath,aliasName,pswd,aliaspswd,apkname))

    F_LOGD("end with build success")
    return 

# 反解apk后用apk的参数填写编译config
def F_remake_config():
    f = open(F_getApkName()[:-4]+"/apktool.yml","r",encoding="utf-8")
    for eachline in f:
        if(re.search("versionCode:",eachline)):
            versionCode = eachline.split(":")[1].strip()[1:-1].strip()
        if(re.search("versionName:",eachline)):
            versionName = eachline.split(":")[1].strip()
        if(re.search("minSdkVersion:",eachline)):
            minSdkVersion = eachline.split(":")[1].strip()[1:-1].strip()
        if(re.search("targetSdkVersion:",eachline)):
            targetSdkVersion = eachline.split(":")[1].strip()[1:-1].strip()
    f.close()
    File_readConfig = open(P_TMP_Config,"r",encoding="utf-8")
    newContent = ""
    eachline = File_readConfig.readline()
    while eachline:
        if(re.search("minSdkVersion",eachline)):
            newContent+='最低支持安卓api版本[-]minSdkVersion[-]appbuild.gradle[-]##MINSDKVERSION##[-]'+minSdkVersion+'\n'
        elif(re.search("targetSdkVersion",eachline)):
            newContent+='目标支持安卓api版本[-]targetSdkVersion[-]appbuild.gradle[-]##MAXSDKVERSION##[-]'+targetSdkVersion+'\n'
        elif(re.search("versionCode",eachline)):
            newContent+='版本号[-]versionCode[-]appbuild.gradle[-]##PROJECTVERSION##[-]'+versionCode+'\n'
        elif(re.search("versionName",eachline)):
            newContent+='版本名称[-]versionName[-]appbuild.gradle[-]##PROJECTVERSIONNAME##[-]'+versionName
        else:
            newContent+=eachline
        eachline = File_readConfig.readline()
    File_readConfig.close()
    File_rewriteConfig = open(P_TMP_Config,"w",encoding="utf-8")
    File_rewriteConfig.write(newContent)
    File_rewriteConfig.close()

# 打印日志
def F_LOGD(MSG):
    print("=>"+MSG)


if __name__ == "__main__":
    opts,args = getopt.gnu_getopt(sys.argv[1:],'',['apkfile='])
    for opt,arg in opts:
        if opt in ("--apkfile"):
            P_Prime_Apk_Path = arg
    # 获取需要反解的apk名称
    FileList = os.listdir(P_curposition)
    for file in FileList:
        if(os.path.splitext(file)[1]=='.apk'):
            os.remove(P_curposition+"/"+file)
        if(os.path.splitext(file)[1]=='.aab'):
            os.remove(P_curposition+"/"+file)
    if(os.path.exists(P_Prime_Apk_Path)):
        shutil.copy(P_Prime_Apk_Path,P_curposition+"/tmptocreataab.apk")
    F_init()
    if(os.path.exists(P_curposition+"/tmptocreataab.aab")):
        shutil.move(P_curposition+"/tmptocreataab.aab",P_Prime_Apk_Path[:-4]+".aab")
        print(P_Prime_Apk_Path[:-4]+".aab")
    os.system("python %s/cleanRoot.py"%P_curposition)