import hashlib

import threadpool

import forum_page
import tools


if __name__ == "__main__":
    url = "https://v.huya.com/g/all?set_id=51"
    hu_ya = forum_page.HuYaDownload(url)
    hu_ya.get_video_id_list(first_page=25, count_page=1)
    print("视频id总数为：{}".format(tools.count_lines("{}/video_id_list_{}.txt".format(hu_ya.temp_path, hu_ya.set_id))))
    hu_ya.save_video(hu_ya)
    print("需要下载的视频数量总数为：{}".
          format(tools.count_lines("{}/video_url_list_{}.txt".format(hu_ya.temp_path, hu_ya.set_id))))
    pool = threadpool.ThreadPool(128)
    requests = threadpool.makeRequests(hu_ya.save, [([], {})])
    [pool.putRequest(req) for req in requests]
    pool.wait()
