#Shutil函数实现文件复制操作
import shutil
#os函数
import os

def check_file_path(path):
    if not os.path.exists(path):
        print("找不到文件")
        return 0
    return 1


def Move_func(path):
    path = path.replace('\\','/')
    if check_file_path(path):
        #获取光影文件名
        Shaders_name = path.split("\\")[-1].replace('"', "")
        print(Shaders_name)
        # 定义源文件和目标文件的路径
        src_path = path
        dst_path = "./Temp/"
        # 使用shutil模块复制文件
        print("*复制光影包文件到程序目录")
        shutil.copy(src_path, dst_path)
        print("Hello :", path)
    else:
        pass
