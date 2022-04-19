import shutil
import os
import time
from pathlib import Path
from fake_useragent import UserAgent
import requests
from requests.adapters import HTTPAdapter


def mkdir(path, is_delete=False):
    """
    Method to create a new subdirectory
    :param is_delete: Whether or not to delete
    :param path:  The address to create the folder
    :return: Boolean
    """
    # Remove the leading space and then the trailing \ symbol.
    path = path.strip().rstrip("\\")

    # Check whether a path exists。True for existence and False for nonexistence.
    is_exists = os.path.exists(path)

    if not is_exists:
        # If the directory address does not exist, create the directory.
        try:
            os.makedirs(path)
            print("directory:" + path + ' Creating a successful!')
            return True
        except Exception as e:
            print("directory:" + path + ' Create a failure！')
            print(e)
            return False
    else:
        # If the directory exists, it is not created and a message
        # is displayed indicating that the directory already exists.
        try:
            # delete the original directory.
            if is_delete:
                print("directory:" + path + ' the directory already exists, delete the original directory and '
                                            'create a new directory.')
                shutil.rmtree(path)
                print("The original directory has been deleted.")
                # Create the directory again.
                try:
                    os.makedirs(path)
                    print("directory:" + path + ' Succeeded in creating the directory again!')
                    return True
                except Exception as e:
                    print("directory:" + path + ' Failure in creating the directory again！')
                    print(e)
                    return False
        except Exception as e:
            print("Failed to delete the original directory.")
            print(e)


def get_url(url, referer=None):
    """
    Method to get the response page
    :param url: indicates the address of the page to be obtained.
    :param referer: The HTTP Referer is part of the header. When a browser sends a request to a Web server,
            it usually carries the Referer with it to tell the server from which page the web page is linked,
            so that the server can obtain some information for processing.
    :return response the retrieved response content.
    """
    # Random generation User-Agent
    ua = UserAgent()
    headers = {'User-Agent': ua.random, "Referer": referer}
    # stream=True   requests.exceptions.ChunkedEncodingError:
    # ('Connection broken: IncompleteRead(0 bytes read)', IncompleteRead(0 bytes read))
    s = requests.Session()
    # max_retries is the maximum number of retries. The total number of retries is 3 times plus the original request
    s.mount('http://', HTTPAdapter(max_retries=9))
    s.mount('https://', HTTPAdapter(max_retries=9))
    start_time = time.time()
    print("The current request link is：{}  -->  Start request time is：{}"
          .format(url, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))))
    try:
        '''
        If you set a single value as timeout, it looks like this:  
        r = requests.get('https://github.com', timeout=5)
        This timeout value will be used as a timeout for both connect and read.  
        To specify separately, pass in a tuple:  
        r = requests.get('https://github.com', timeout=(5, 25))
        '''
        response = s.get(url, headers=headers, stream=True, timeout=(5, 300))
        end_time = time.time()
        print("The current request link is：{} -->  End request time is：{}"
              .format(url, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))))
        print("The current request link is：{}  -->   The requested total time is：{}秒"
              .format(url, round(end_time - start_time, 4)))
        return response
    except requests.exceptions.RequestException as e:
        print(e)
        print("Request failed!!! The current request link is：{} -->  The request end time is：{}"
              .format(url, time.strftime('%Y-%m-%d %H:%M:%S')))


def update_name(name):
    """
    The method of updating the name
    :param name: The name you want to change.
    :return: Modified name
    """
    string = "~`!@#$%^&*()+-/=|\\[]{};:'\"<,>.?|“‘ "
    # Check if the string contains any of the special symbols listed above and replace them with "_"
    for i in string:
        if i in name:
            name = name.replace(i, "_")     # Replace special characters
    return name


def count_lines(file_path):
    """
    Gets the number of lines of the current file by passing in the file address
    :param file_path:
    :return:
    """
    count = -1
    for count, line in enumerate(open(file_path, 'rU', encoding="utf-8")):
        pass
    count += 1
    return count


def read_file(path, types):
    """

    :param path: fire path
    :param types: "r" or "rb"
    :return: list
    """
    with open(path, types, encoding="utf-8") as r:
        return r.readlines()


def get_all_files(path):
    """
    Get all the addresses
    :param path:    root path
    :return: all file path and name
    """
    all_file = []
    for dir_path, dir_names, filenames in os.walk(path):
        for dir_ in dir_names:
            all_file.append(os.path.join(dir_path, dir_))
        for name in filenames:
            all_file.append(os.path.join(dir_path, name))
    return all_file


def is_or_not_file(path):
    """
    Method to determine if it is a file
    :param path: file or dir path
    :return:  True is File False is dir
    """
    return os.path.isfile(path)


def save_video(video_name=None, video_url=None, video_path=None):
    save_video_flag = False
    start_time = time.time()
    response = get_url(video_url)
    my_file = Path("{}/{}.mp4".format(video_path, video_name))
    if response.status_code == 200:
        print("当前保存的视频名称为：{}， 开始保存视频时间为：{}"
              .format(video_name, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))))
        with open(my_file, "wb") as f:
            f.write(response.content)
        end_time = time.time()
        print("当前保存的视频名称为：{}， 结束保存视频时间为：{}"
              .format(video_name, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))))
        print("当前保存的视频名称为：{}， 视频保存总用时间为：{}秒"
              .format(video_name, round(end_time - start_time, 4)))
        print("视频： {}/{}.mp4 下载成功!".format(video_path, video_name))
        save_video_flag = True
        return video_name, video_url, save_video_flag
    else:
        return video_name, video_url, save_video_flag


def file_to_list(path):
    """
    Types  --> XXX.txt  -->  file name|id or url
    :param path: file path
    :return: video id or url lists
    """
    video_id_or_url_list = []
    videos = read_file(path, "r")
    for video in videos:
        video_name = video.split("|")[0]
        video_url_or_id = video.split("|")[1]
        tmp = (video_name, video_url_or_id)
        video_id_or_url_list.append(tmp)
    return video_id_or_url_list
