import json
import tempfile
import time
import threading
import requests
import threadpool
from lxml import etree
import tools
from tools import get_url


class HuYaDownload:
    def __init__(self, url):
        self.url = url
        self.page = None
        self.lock = threading.RLock()
        self.json_url = "https://v-api-player-ssl.huya.com/?r=vhuyaplay%2Fvideo&vid={}&format=mp4%2Cm3u8"
        # self.video_path = "../Download/Video"         # 相对路径
        self.video_path = "G:/Downloads/huya_video"  # 绝对路径
        self.temp_path = "../Download/Temp"
        self.pool = threadpool.ThreadPool(32)  # 线程池
        self.download_video_count = 0  # 下载视频个数
        self.forum_page_list = []  # forum_page
        self.failure_list = []  # 视频下载失败后列表
        self.set_id = url.split("=")[-1]
        tools.mkdir(self.video_path, False)     # False为不清空文件夹
        tools.mkdir(self.temp_path, True)       # True为清空文件夹

    def get_video_page_list(self, first_page=1, count_page=500):
        if first_page + count_page > 501:
            count_page = 501 - first_page
        if first_page < 1 or first_page > 500:
            first_page = 1
        if count_page > 500 or count_page < 1:
            count_page = 500
        # 打印网页源码
        # html = etree.HTML(get_url(self.url).text)
        # result = etree.tostring(html, encoding="utf-8", pretty_print=True, method="html").decode("utf-8")
        # print(result)
        for i in range(count_page):
            forum_page_url = "https://v.huya.com/g/all?set_id={}&order=hot&page={}".format(self.set_id, i + first_page)
            req = threadpool.makeRequests(self.save_video_id,
                                          [([], {"forum_page_url": forum_page_url,
                                                 "first_page": i + first_page})])
            [self.pool.putRequest(req) for req in req]
        self.pool.wait()

    def save_video_id(self, forum_page_url, first_page):
        # 加锁   使用线程锁，保证数据安全
        self.lock.acquire()
        try:
            status_code = False  # 是否获取成功
            while not status_code:
                html = get_url(forum_page_url)
                if html.status_code == 200:
                    self.page = etree.HTML(html.text)
                    if len(self.page.xpath("//ul[@class='vhy-video-list clearfix ']/li")) != 0:
                        status_code = True
                    else:
                        status_code = False
                else:
                    status_code = False

                print("开始抓取第 {} 页数据。".format(first_page))
                for j in range(len(self.page.xpath("//ul[@class='vhy-video-list clearfix ']/li"))):
                    title = self.page.xpath("//ul[@class='vhy-video-list clearfix ']/li[{}]/a/@title".format(j + 1))[0]
                    tmp_title = tempfile.NamedTemporaryFile().name.split("\\")[-1]
                    title = title + "_" + tmp_title
                    title = tools.update_name(title).replace('\r\n', '').replace('\n', '').replace('\r', '')
                    url = self.page.xpath("//ul[@class='vhy-video-list clearfix ']/li[{}]/a/@href"
                                          .format(j + 1))[0].replace('//', '')
                    video_id = url.split('/')[-1].replace('.html', '')
                    with open("{}/video_id_list_{}.txt".format(self.temp_path, self.set_id), "a", encoding="utf-8") as f:
                        f.write(title + "|" + video_id + "\n")
                    # print(title)
                    # print(url)
                    # print(video_id)
                print("已经抓取了 {} 页。".format(first_page))
                # time.sleep(random.randint(1, 3))
        finally:
            # 修改完成，释放锁
            self.lock.release()

    def get_all_video_url(self, video_id_list=None):
        if video_id_list is None:
            ids = tools.file_to_list('{}/video_id_list_{}.txt'.format(self.temp_path, self.set_id))
        else:
            ids = video_id_list
        for name_id in ids:
            video_name = name_id[0]
            video_id = name_id[1]
            req = threadpool.makeRequests(self.get_all_video_url_list,
                                          [([], {"video_name": video_name,
                                                 "video_id": video_id})],
                                          self.get_all_video_url_callback)
            [self.pool.putRequest(req) for req in req]
        self.pool.wait()

    def get_all_video_url_list(self, video_name, video_id):
        data = get_url(self.json_url.format(video_id.rstrip("\n")))
        # print(data.text)
        json_dict = json.loads(data.text)
        # print(json_dict
        # print("type(json_dict) = >", type(json_dict))
        # print(json.dumps(json_dict, indent=4))
        # print(json.dumps(json_dict['result']['items'], indent=4))
        # with open("t.txt", "a") as f:
        #     f.write(json.dumps(json_dict['result']['items'], indent=4))
        # print(json_dict['result']['cover'])
        try:
            video_rul = json_dict['result']['items'][1]['transcode']['urls'][0]  # 1920*1080
        except IndexError as e:
            print(e)
            print("视频： {} 没有1920*1280高清视频。".format(video_name))
            video_rul = json_dict['result']['items'][0]['transcode']['urls'][0]  # 1280*720
            print("video_name: {} \n video_url: {}".format(video_name, video_rul))
        return video_name, video_rul

    def get_all_video_url_callback(self, request, result):
        # 第1个参数是request，可以访问request.requestID
        # 第2个参数是request执行完的结果
        # print(request.requestID, result)
        # 加锁   使用线程锁，保证数据安全
        self.lock.acquire()
        try:
            with open('{}/video_url_list_{}.txt'.format(self.temp_path, self.set_id), 'a', encoding="utf-8") as f:
                f.write(result[0] + "|" + result[1] + "\n")
        finally:
            # 修改完成，释放锁
            self.lock.release()

    def read_and_save(self, video_url_list=None):
        """
        :param video_url_list: video_url_list
        :return:
        """
        if video_url_list is None:
            videos = tools.file_to_list('{}/video_url_list_{}.txt'.format(self.temp_path, self.set_id))
        else:
            videos = video_url_list
        for video in videos:
            video_name = video[0]
            video_url = video[1]
            req = threadpool.makeRequests(tools.save_video,
                                          [([], {"video_name": video_name,
                                                 "video_url": video_url,
                                                 "video_path": self.video_path})],
                                          self.read_and_save_callback)
            [self.pool.putRequest(req) for req in req]
        self.pool.wait()

    def read_and_save_callback(self, request, result):
        """
        :param request: 这个参数可以访问request.requestID
        :param result: 这个参数是request执行完的结果
        :return:
        print(request.requestID, result)
        """

        if result[2]:
            self.download_video_count += 1
            print("已成功下载{}个视频！".format(self.download_video_count))
        else:
            print("{}    下载失败！".format(result[0]))
            self.failure_list.append(result)  # Add the name and link of the failed download to the failed list
            self.read_and_save(self.failure_list)
