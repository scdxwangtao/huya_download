import json
import tempfile
import time

import requests
import threadpool
from lxml import etree
import tools
from tools import get_url


class HuYaDownload:
    def __init__(self, url):
        self.url = url
        self.json_url = "https://v-api-player-ssl.huya.com/?r=vhuyaplay%2Fvideo&vid={}&format=mp4%2Cm3u8"
        self.video_path = "../Download/Video"
        self.temp_path = "../Download/Temp"
        self.set_id = url.split("=")[-1]
        tools.mkdir(self.video_path, True)
        tools.mkdir(self.temp_path, True)

    def get_video_id_list(self, first_page=1, count_page=500):
        if first_page + count_page > 501:
            count_page = 501 - first_page
        if first_page < 1 or first_page > 500:
            first_page = 1
        if count_page > 500 or count_page < 1:
            count_page = 500
        # 打印网页源码
        html = etree.HTML(get_url(self.url).text)
        # result = etree.tostring(html, encoding="utf-8", pretty_print=True, method="html").decode("utf-8")
        # print(result)
        for i in range(count_page):
            status_code = False  # 是否获取成功
            while not status_code:
                html = get_url("https://v.huya.com/g/all?set_id={}&order=hot&page={}"
                               .format(self.set_id, i + first_page))
                if html.status_code == 200:
                    status_code = True
                else:
                    status_code = False
            page = etree.HTML(html.text)

            # # 当前页面没有获取到数据，再获取一次
            # # print(len(page.xpath("//ul[@class='vhy-video-list clearfix ']/li")))        # lins
            # if len(page.xpath("//ul[@class='vhy-video-list clearfix ']/li")) == 0:
            #     status_code = False  # 是否获取成功
            #     while not status_code:
            #         html = get_url("https://v.huya.com/g/all?set_id={}&order=hot&page={}"
            #                        .format(self.set_id, i + first_page))
            #         if html.status_code == 200:
            #             status_code = True
            #         else:
            #             status_code = False
            #     page = etree.HTML(html.text)

            print("开始抓取第 {} 页数据。".format(i + 1))
            for j in range(len(page.xpath("//ul[@class='vhy-video-list clearfix ']/li"))):
                pass
                title = page.xpath("//ul[@class='vhy-video-list clearfix ']/li[{}]/a/@title".format(j + 1))[0]
                if title == "" or title == " ":
                    title = tempfile.NamedTemporaryFile().name.split("\\")[-1]
                title = tools.update_name(title).replace('\r\n', '').replace('\n', '').replace('\r', '')
                url = page.xpath("//ul[@class='vhy-video-list clearfix ']/li[{}]/a/@href".format(j + 1))[0].replace(
                    '//', '')
                # video_id = url.replace('.html', '').replace('//v.huya.com/play/', '')
                video_id = url.split('/')[-1].replace('.html', '')
                with open("{}/video_id_list_{}.txt".format(self.temp_path, self.set_id), "a", encoding="utf-8") as f:
                    f.write(title + "|" + video_id + "\n")
                # print(title)
                # print(url)
                # print(video_id)
            print("已经抓取了 {} 页。".format(i + 1))
            # time.sleep(random.randint(1, 3))

    def get_all_video_url_list(self, video_name, video_id):
        data = get_url(
            self.json_url.format(video_id))
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
            video_rul = json_dict['result']['items'][1]['transcode']['urls'][0]         # 1920*1080
        except IndexError as e:
            print("视频： {} 没有1920*1280高清视频。".format(video_name))
            video_rul = json_dict['result']['items'][0]['transcode']['urls'][0]       # 1280*720
        # video_rul = video_rul.split("?")[0]
        # print("video_name: {} \n video_url: {}".
        # format(video_name, json_dict['result']['items'][1]['transcode']['urls'][0]))
        return video_name, video_rul

    def save_video_callback(self, request, result):
        # 第1个参数是request，可以访问request.requestID
        # 第2个参数是request执行完的结果
        print(request.requestID, result)
        with open('{}/video_url_list_{}.txt'.format(self.temp_path, self.set_id), 'a', encoding="utf-8") as f:
            f.write(result[0] + "|" + result[1] + "\n")

    def save(self):
        download_video_count = 0
        videos = tools.read_file('{}/video_url_list_{}.txt'.format(self.temp_path, self.set_id), "r")
        for video in videos:
            video_name = video.split("|")[0]
            video_url = video.split("|")[1]
            # print(video_name, video_url)
            response = tools.get_url(video_url)
            if response.status_code == 200:
                start_time = time.time()
                print("当前保存的视频名称为：{}， 开始保存视频时间为：{}"
                      .format(video_name, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))))
                with open("{}/{}.mp4".format(self.video_path, video_name), "wb") as f:
                    f.write(response.content)
                end_time = time.time()
                print("当前保存的视频名称为：{}， 结束保存视频时间为：{}"
                      .format(video_name, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))))
                print("当前保存的视频名称为：{}， 视频保存总用时间为：{}秒"
                      .format(video_name, round(end_time - start_time, 4)))
                print("视频： {}/{}.mp4 下载成功!".format(self.video_path, video_name))
                download_video_count += 1
                print("已成功下载 {} 个视频！".format(download_video_count))

    def save_video(self, hu_ya):
        ids = tools.read_file("{}/video_id_list_{}.txt".format(self.temp_path, self.set_id), "r")
        pool = threadpool.ThreadPool(128)
        for name_id in ids:
            video_name = name_id.split("|")[0]
            video_id = name_id.split("|")[1]
            req = threadpool.makeRequests(hu_ya.get_all_video_url_list,
                                          [([], {"video_name": video_name, "video_id": video_id})],
                                          hu_ya.save_video_callback)
            [pool.putRequest(req) for req in req]
        pool.wait()
