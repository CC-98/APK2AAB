from genericpath import exists
import os
import shutil


# 当前目录
P_curposition = os.path.split(os.path.realpath(__file__))[0]

P_bundlerelease = P_curposition+"/app/build/outputs/bundle/release/app-release.aab"
P_tmp_releaseapk = P_curposition+"/releaseapk.zip"
P_tmp_releaseaab = P_curposition+"/release.zip"

P_assets = P_curposition+"/assets/src/main/assets"
P_libs = P_curposition+"/app/libs"
P_res = P_curposition+"/app/src/main/res"


def F_remove_dir(dirpath):
    if(os.path.exists(dirpath)):
        F_delete_log(dirpath)
        shutil.rmtree(dirpath)

def F_remove_file(filedir):
    if(os.path.isfile(filedir)):
        F_delete_log(filedir)
        os.remove(filedir)
# 获取要删除的aab文件
def F_removeaab_apk():
    FileList = os.listdir(P_curposition)
    for file in FileList:
        if(os.path.splitext(file)[1]=='.aab'):
            F_remove_file(P_curposition+"/"+file)
        if(os.path.splitext(file)[1]=='.apk'):
            F_remove_file(P_curposition+"/"+file)

def F_delete_log(pathname):
    print(pathname+" is delete!")

def F_clean_build():
    os.system('%s\\./gradlew -p %s clean'%(P_curposition,P_curposition))

F_removeaab_apk()
F_clean_build()
F_remove_file(P_bundlerelease)
F_remove_file(P_tmp_releaseapk)
F_remove_file(P_tmp_releaseaab)


F_remove_dir(P_assets)
F_remove_dir(P_libs)
F_remove_dir(P_res)
