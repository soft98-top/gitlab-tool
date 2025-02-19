from genericpath import isdir
import requests
import json
import os
import argparse

gitlab_address = ""
gitlab_token = ""
## 需要输入绝对路径
download_path = ""
gitlab_headers = {
    "Private-Token":gitlab_token
}

def get_group_info(group_id):
    url = "/".join([gitlab_address,"api/v4/groups",str(int(group_id))])
    resp = requests.get(url,headers=gitlab_headers)
    if resp.status_code == 200:
        return json.loads(resp.text)
    else:
        return None

def get_subgroups(group_id):
    url = "/".join([gitlab_address,"api/v4/groups",str(int(group_id)),"subgroups"])
    resp = requests.get(url,headers=gitlab_headers)
    if resp.status_code == 200:
        return json.loads(resp.text)
    else:
        return []

def get_projects(group_id):
    url = "/".join([gitlab_address,"api/v4/groups",str(int(group_id)),"projects"])
    resp = requests.get(url,headers=gitlab_headers)
    if resp.status_code == 200:
        return json.loads(resp.text)
    else:
        return []

def down_groups(dir_path,group_id):
    if os.path.isdir(dir_path):
        projects = get_projects(group_id)
        if len(projects) != 0:
            for project in projects:
                repo = project["ssh_url_to_repo"]
                path = project["path"]
                cmd = " ".join(["git clone",repo,dir_path + "/" + path])
                print(cmd)
                os.system(cmd)
        sub_groups = get_subgroups(group_id)
        if len(sub_groups) != 0:
            for sub_group in sub_groups:
                path = sub_group["path"]
                sub_group_id = sub_group["id"]
                sub_dir_path = "/".join([dir_path,path])
                os.mkdir(sub_dir_path)
                down_groups(sub_dir_path,sub_group_id)

def start(group_id):
    group_info = get_group_info(group_id)
    if group_info == None:
        print("group_id错误")
    else:
        path = group_info["path"]
        dir_path = "/".join([download_path,path])
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
            down_groups(dir_path,group_id)
        else:
            print("目标文件夹已存在：",dir_path)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gitlab groups download')
    parser.add_argument("-g",'--group_id', type=int, help="需要被下载组的id",required=True)
    parser.add_argument("-d",'--dir', type=str, default= None, help="存储目录绝对地址")
    args = parser.parse_args()
    group_id = args.group_id
    dir_path = args.dir
    if dir_path != None :
        if os.path.isdir(dir_path):
            download_path = dir_path
        else:
            print("请输入正确的存储目录绝对地址")
            os._exit(0)
    start(group_id)