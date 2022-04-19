import forum_page
import tools
import time


if __name__ == "__main__":
    start_time = time.time()
    url = "https://v.huya.com/g/all?set_id=51"        # 舞蹈
    # url = "https://v.huya.com/g/all?set_id=65"      # 音乐
    hu_ya = forum_page.HuYaDownload(url)
    hu_ya.get_video_page_list(first_page=1, count_page=50)

    print("视频id总数为：{}".format(tools.count_lines("{}/video_id_list_{}.txt".format(hu_ya.temp_path, hu_ya.set_id))))
    hu_ya.get_all_video_url()
    print("需要下载的视频数量总数为：{}".
          format(tools.count_lines("{}/video_url_list_{}.txt".format(hu_ya.temp_path, hu_ya.set_id))))

    hu_ya.read_and_save()

    end_time = time.time()
    print("总用时为：{}".format(end_time - start_time))
