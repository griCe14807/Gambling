# -*- coding=utf8 =*-
# 1. 朝、このスクリプトを回し、その日のレーススケジュールcronを作成
# 2. レーススケジュールcronに、automated_voterを実行させる


import pandas as pd
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '../crawl/'))

# my module
import boatrace_crawler_conf


def crawle_race_schedule(soup, jcd, hd):
    """
    soupをパースし, 日付、会場、レースナンバー、締め切り時刻のdfを返す
    :param soup:
    :return race_result_list: [日付、レース場、レース、順位、枠番、登録番号、選手名、タイム]のリストを一位から6位までネストしたリスト
    """
    cols = ["日付", "会場", "レースナンバー", "締め切り時刻"]
    closing_time_list = []

    table = soup.find(class_="table1")
    row = table.find("tbody").find("tr")
    closing_times = row.find_all("td")[1:]
    # print(closing_times)

    # 各レースについて、[日付、会場, レース名, 締め切り時刻]のリストを要素にとるリストを作成
    for i, closing_time in enumerate(closing_times, 1):
        race_number = str(i) + "R"
        closing_time_text = closing_time.text
        closing_time_list.append([hd, jcd, race_number, closing_time_text])

    closing_time_df = pd.DataFrame(closing_time_list, columns=cols)

    return closing_time_df


def cron_generater():

    """
    closing_time_dfをインプットにして、その日のcronをgenerateする関数
    generateしたcronはshファイルで書きだして、それを実際に食わせるのはとりあえず手動でOK
    :return:
    """

if __name__ == "__main__":


    # ------- input -----------

    the_hd = "2019/07/27"
    # 指定したrnoより後の物をprint
    the_rno_int = 1
    # --------------------------- #

    the_rno = str(the_rno_int) + "R"
    # 会場のリスト
    the_jcd_dict = boatrace_crawler_conf.make_jcd_dict()
    the_jcd_list = list(the_jcd_dict.keys())

    # main
    the_closing_time_df_list = []
    for the_jcd in the_jcd_list:
        # クロール対象サイトのurl作成
        racelist_url = boatrace_crawler_conf.make_url("racelist", the_rno, the_jcd, the_hd)
        print(racelist_url)

        try:
            # 対象サイトをパースしてcrawl
            soup = boatrace_crawler_conf.html_parser(racelist_url)
            the_closing_time_df_ = crawle_race_schedule(soup, the_jcd, the_hd)
            the_closing_time_df_list.append(the_closing_time_df_)

        except AttributeError:
            pass

    # dfをまとめて一つにする
    the_closing_time_df = pd.concat(the_closing_time_df_list)
    # print(the_closing_time_df)

    # dfからcrontabのスクリプトをgenerate
    for index, rows in the_closing_time_df.iterrows():
        closing_time_min = int(rows["締め切り時刻"][3:5])
        closing_time_hour = int(rows["締め切り時刻"][0:2])
        # 11じ1分など、3分前だと時間まで変わるやつらの対応
        if closing_time_min < 5:
            conduction_time_min = str(60 + closing_time_min - 5)
            conduction_time_hour = str(closing_time_hour - 1)
        else:
            conduction_time_min = str(closing_time_min - 5)
            conduction_time_hour = str(closing_time_hour)
        conduction_time = conduction_time_min + " " + conduction_time_hour + " * * * "
        command = "cd /Users/grice/mywork/boatrace/src/automated_voting/; bash -l -c " +\
                  "'python3 /Users/grice/mywork/boatrace/src/automated_voting/automated_voter.py -rno " +\
                  rows["レースナンバー"] + " -jcd " + rows["会場"] + " -hd " + rows["日付"] + "';"
        cron = conduction_time + command

        if int(rows["レースナンバー"][:-1]) >= the_rno_int:
            print(cron)

    # crontabスクリプトを書きだし