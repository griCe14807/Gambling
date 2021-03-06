"""How to use this script
(1) Download race result files by RaceResults.download()
(2) Manually extract text files from lzh files
(3) Move the text files to ./data directory
(4) RaceResults.load() will parse the text files
"""

import pandas as pd
import glob
import re
from datetime import datetime
import os


def load_race_results(race_results_file_path=
                      os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '../../data/results_race/K1*.TXT')):
    """

    :param race_results_file_path: ダウンロードファイルのパス（glob.globで回す）
    :return:

    """
    # loadした結果を格納するための辞書を作成（最後はpandas.DataFrameにします）
    race_result_dict = {"date": [],
                        "venue": [],
                        "raceNumber": [],
                        "weather": [],
                        "windDir": [],
                        "windPow": [],
                        "waveHight": [],
                        "ruler": [],
                        "win": [],
                        "winOdds": [],
                        "place_1": [],
                        "placeOdds_1": [],
                        "place_2": [],
                        "placeOdds_2": [],
                        "exacta": [],
                        "exactaOdds": [],
                        "quinella": [],
                        "quinellaOdds": [],
                        "wide_1": [],
                        "wideOdds_1": [],
                        "wide_2": [],
                        "wideOdds_2": [],
                        "wide_3": [],
                        "wideOdds_3": [],
                        "trifecta": [],
                        "trifectaOdds": [],
                        "trio": [],
                        "trioOdds": []
                        }
    for i in range(1, 7):
        race_result_dict["rank_{0}".format(i)] = []
        race_result_dict["racerId_{0}".format(i)] = []
        race_result_dict["racerName_{0}".format(i)] = []
        race_result_dict["motor_{0}".format(i)] = []
        race_result_dict["boat_{0}".format(i)] = []
        race_result_dict["exhibitionTime_{0}".format(i)] = []
        race_result_dict["cource_{0}".format(i)] = []
        race_result_dict["startTime_{0}".format(i)] = []
        race_result_dict["raceTime_{0}".format(i)] = []

    # レース結果のテキストファイルを読み込み、辞書に格納していく
    for filename in glob.glob(race_results_file_path):
        # print(filename)
        with open(filename, "r", encoding="shift_jis") as f:
            result_ = f.read()

            # 会場ごとの塊に分割
            result_ = re.split(r"[0-9][0-9]KBGN\n", result_)
            # ファイル全体のhead（start）を削除
            result_ = result_[1:]

            # 第一要素がヘッダ、それ以降は各レースの結果を格納したリストへと分割
            for result_element in result_:
                result_element_list = result_element.split("\n\n\n")

                # 中身一つ一つを改行で分割
                result_element_list = [result__.splitlines() for result__ in result_element_list]

                # ヘッダ部分（会場名や払戻金のまとめなど）
                jcd_head = result_element_list[0]
                # レース結果（最後の改行に伴う空白も削除）
                jcd_body = result_element_list[1:-1]

                # 会場ごとに取得
                jcd = jcd_head[0][0:3]  # 会場名
                hd = datetime.strptime(jcd_head[6][17:27].replace(" ", "0"), '%Y/%m/%d') # 日付 datetime型に

                for race_body in jcd_body:
                    # 同着ありのレースやFLなどによって書式がかわる系のレースは弾く
                    try:
                        if race_body[0] == "":
                            race_body = race_body[1:]

                        # レースごとに取得その1: レースごとのヘッダ部分から取得
                        race_head = race_body[0]
                        race = int(race_head[2:4].replace(" ", ""))  # レース番号
                        ruler = race_body[1][50:53].replace(" ", "") # 決まり手

                        # 進入固定の場合位置が変わる
                        if race_head[20:24] == "進入固定":
                            weather = race_head[39]  # 天候
                            wind_dir = race_head[46:48]  # 風向
                            wind_power = int(race_head[50])  # 風速 (m)
                            wave = int(race_head[58])  # 波高 (cm)

                        else:
                            weather = race_head[43] # 天候
                            wind_dir = race_head[50:52] # 風向
                            wind_power = int(race_head[54])   # 風速
                            wave = int(race_head[62]) # 波高

                        # 払い戻し結果を取得
                        payoff_result = race_body[10:19]
                        win_number = payoff_result[0][15]  # 単勝勝ち艇
                        win_payoff = int(payoff_result[0][25:29])  # 単勝払い戻し
                        place_number_1 = payoff_result[1][15]
                        place_payoff_1 = int(payoff_result[1][25:29])
                        place_number_2 = payoff_result[1][31]
                        place_payoff_2 = int(payoff_result[1][41:45])

                        exacta_number = payoff_result[2][14:17]
                        exacta_payoff = int(payoff_result[2][24:28])
                        quinella_number = payoff_result[3][14:17]
                        quinella_payoff = int(payoff_result[3][23:28])
                        wide_1_number = payoff_result[4][14:17]
                        wide_1_payoff = int(payoff_result[4][24:28])
                        wide_2_number = payoff_result[5][17:20]
                        wide_2_payoff = int(payoff_result[5][27:31])
                        wide_3_number = payoff_result[6][17:20]
                        wide_3_payoff = int(payoff_result[6][27:31])
                        trifecta_number = payoff_result[7][14:19]  # 3連単
                        trifecta_payoff = int(payoff_result[7][22:28])
                        trio_number = payoff_result[8][14:19]  # ３連複
                        trio_payoff = int(payoff_result[8][23:28])

                        # print(hd, jcd, race, weather, wind_dir, wind_power, wave, ruler)

                        """
                        print(win_number, win_payoff, place_number_1, place_payoff_1, place_number_2, place_payoff_2,
                              exacta_number, exacta_payoff, quinella_number, quinella_payoff,
                              wide_1_number, wide_1_payoff, wide_2_number, wide_2_payoff, wide_3_number, wide_3_payoff,
                              trifecta_number, trifecta_payoff, trio_number, trio_payoff
                              )
                        """

                        # 選手情報を取得
                        racers_result = race_body[3:9]
                        for racer_result in racers_result:

                            # スタートタイム。flying, lateがあった場合はnoneを格納. これで多分転覆もexcept側に入ってる
                            # TODO 本当はそもそも解析用のdfに加えないようにしたい
                            try:
                                start_time = float(racer_result[43: 47])
                                rank = int(racer_result[2:4])  # 順位

                            except ValueError:
                                start_time = None
                                rank = 0

                            frame = racer_result[6] # 枠番
                            racer_id = racer_result[8:12]   # 選手登録番号
                            racer_name = racer_result[13:21]    # 名前
                            motor = racer_result[22:24] # モーター番号
                            boat = racer_result[27:29]  # ボート番号
                            # 展示タイムがない場合
                            if racer_result[31:35] == ' .  ':
                                exhibition_time = None
                            else:
                                exhibition_time = float(racer_result[31:35])   # 展示タイム
                            # 進入コースがない場合
                            if racer_result[38] == " ":
                                cource = None
                            else:
                                cource = int(racer_result[38])  # 進入コース

                            # レースタイム
                            race_time = racer_result[52: 58].split(".")
                            if race_time[0] == " ": # 5着5着のタイムはない
                                race_time = None
                            else:
                                race_time = int(race_time[0]) * 60 + int(race_time[1]) + int(race_time[2]) / 100

                        # print(rank, frame, racer_id, racer_name, motor, boat, exhibition_time, cource, start_time, race_time)

                            # 辞書に格納
                            race_result_dict["rank_{0}".format(frame)].append(rank)
                            race_result_dict["racerId_{0}".format(frame)].append(racer_id)
                            race_result_dict["racerName_{0}".format(frame)].append(racer_name)
                            race_result_dict["motor_{0}".format(frame)].append(motor)
                            race_result_dict["boat_{0}".format(frame)].append(boat)
                            race_result_dict["exhibitionTime_{0}".format(frame)].append(exhibition_time)
                            race_result_dict["cource_{0}".format(frame)].append(cource)
                            race_result_dict["startTime_{0}".format(frame)].append(start_time)
                            race_result_dict["raceTime_{0}".format(frame)].append(race_time)

                        # 辞書に格納
                        race_result_dict["date"].append(hd)
                        race_result_dict["venue"].append(jcd)
                        race_result_dict["raceNumber"].append(race)
                        race_result_dict["weather"].append(weather)
                        race_result_dict["windDir"].append(wind_dir)
                        race_result_dict["windPow"].append(wind_power)
                        race_result_dict["waveHight"].append(wave)
                        race_result_dict["ruler"].append(ruler)
                        race_result_dict["win"].append(win_number)
                        race_result_dict["winOdds"].append(win_payoff)
                        race_result_dict["place_1"].append(place_number_1)
                        race_result_dict["placeOdds_1"].append(place_payoff_1)
                        race_result_dict["place_2"].append(place_number_2)
                        race_result_dict["placeOdds_2"].append(place_payoff_2)
                        race_result_dict["exacta"].append(exacta_number)
                        race_result_dict["exactaOdds"].append(exacta_payoff)
                        race_result_dict["quinella"].append(quinella_number)
                        race_result_dict["quinellaOdds"].append(quinella_payoff)
                        race_result_dict["wide_1"].append(wide_1_number)
                        race_result_dict["wideOdds_1"].append(wide_1_payoff)
                        race_result_dict["wide_2"].append(wide_2_number)
                        race_result_dict["wideOdds_2"].append(wide_2_payoff)
                        race_result_dict["wide_3"].append(wide_3_number)
                        race_result_dict["wideOdds_3"].append(wide_3_payoff)
                        race_result_dict["trifecta"].append(trifecta_number)
                        race_result_dict["trifectaOdds"].append(trifecta_payoff)
                        race_result_dict["trio"].append(trio_number)
                        race_result_dict["trioOdds"].append(trio_payoff)

                    except:
                        pass

    race_result_df = pd.DataFrame(race_result_dict)

    return race_result_df



def load_racer_data(racer_filename =
                    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "../../data/racer/fan1904.txt")):
    racer_dict = {"racerId": [],
                  "racerName_ch": [],
                  "racername_ja": [],
                  "branch": [],
                  "class": [],
                  "era": [],
                  "birth": [],
                  "sex": [],
                  "age": [],
                  "hight": [],
                  "weight": [],
                  "bloodType": [],
                  "winRate": [],
                  "placeRate": [],
                  "numWin": [],
                  "numSecond": [],
                  "numRace": [],
                  "numParticipate": [],
                  "numVictory": [],
                  "aveST": [],
                  "pre_class": [],
                  "pre_pre_class": [],
                  "pre_pre_pre_class": [],
                  "pre_abilityValue": [],
                  "abilityValue": [],
                  "year": [],
                  "period": [],
                  "dateFrom": [],
                  "dateTo": [],
                  "schoolYear": [],
                  "numL0": [],
                  "numL1": [],
                  "numK0": [],
                  "numK1": [],
                  "homeTown": []
                  }

    for i in range(1, 7):
        racer_dict["numFrame{0}".format(i)] = []
        racer_dict["placeRate_frame{0}".format(i)] = []
        racer_dict["aveST_frame{0}".format(i)] = []
        racer_dict["aveSR_frame{0}".format(i)] = []
        for j in range(1, 7):
            racer_dict["num_rank_{0}_frame_{1}".format(j, i)] = []
        racer_dict["numF_{0}".format(i)] = []
        racer_dict["numL0_{0}".format(i)] = []
        racer_dict["numL1_{0}".format(i)] = []
        racer_dict["numK0_{0}".format(i)] = []
        racer_dict["numK1_{0}".format(i)] = []
        racer_dict["numS0_{0}".format(i)] = []
        racer_dict["numS1_{0}".format(i)] = []
        racer_dict["numS2_{0}".format(i)] = []


    with open(racer_filename, "r", encoding="shift_jis") as f:
        results = f.read().splitlines()[:-1]
        for line in results:
            racer_dict["racerId"].append(line[0:4])
            racer_dict["racerName_ch"].append(line[4:12])
            racer_dict["racername_ja"].append(line[12:27])
            racer_dict["branch"].append(line[27:29])
            racer_dict["class"].append(line[29:31])
            racer_dict["era"].append(line[31])
            racer_dict["birth"].append(line[32:38])
            racer_dict["sex"].append(line[38])
            racer_dict["age"].append(line[39:41])
            racer_dict["hight"].append(line[41:44])
            racer_dict["weight"].append(line[44:46])
            racer_dict["bloodType"].append(line[46:48])
            racer_dict["winRate"].append(line[48:52])
            racer_dict["placeRate"].append(line[52:56])
            racer_dict["numWin"].append(line[56:59])
            racer_dict["numSecond"].append(line[59:62])
            racer_dict["numRace"].append(line[62:65])
            racer_dict["numParticipate"].append(line[65:67])
            racer_dict["numVictory"].append(line[67:69])
            racer_dict["aveST"].append(line[69:72])

            racer_dict["pre_class"].append(line[150:152])
            racer_dict["pre_pre_class"].append(line[152:154])
            racer_dict["pre_pre_pre_class"].append(line[154:156])
            racer_dict["pre_abilityValue"].append(line[156:160])
            racer_dict["abilityValue"].append(line[160:164])
            racer_dict["year"].append(line[164:168])
            racer_dict["period"].append(line[168])
            racer_dict["dateFrom"].append(line[169: 177])
            racer_dict["dateTo"].append(line[177: 185])
            racer_dict["schoolYear"].append(line[185: 188])

            racer_dict["numL0"].append(line[392: 394])
            racer_dict["numL1"].append(line[394: 396])
            racer_dict["numK0"].append(line[396: 398])
            racer_dict["numK1"].append(line[398: 400])
            racer_dict["homeTown"].append(line[400: 403])

            # error見つけ用
            # print(racer_dict["racerName_ch"])

            for i in range(1, 7):
                racer_dict["numFrame{0}".format(i)].append(line[59+13*i:62+13*i])   # i = 1の時は72:75 2だと85:
                racer_dict["placeRate_frame{0}".format(i)].append(int(line[62+13*i:66+13*i]))   # i = 1の時は75:79
                racer_dict["aveST_frame{0}".format(i)].append(int(line[66+13*i:69+13*i]))
                racer_dict["aveSR_frame{0}".format(i)].append(int(line[69+13*i: 72+13*i]))
                for j in range(1, 7):
                    racer_dict["num_rank_{0}_frame_{1}".format(j, i)].append((line[151+34*i+3*j: 154+34*i+3*j]))
                racer_dict["numF_{0}".format(i)].append(line[172+34*i: 174+34*1])
                racer_dict["numL0_{0}".format(i)].append(line[174+34*i: 176+34*1])
                racer_dict["numL1_{0}".format(i)].append(line[176+34*i: 178+34*1])
                racer_dict["numK0_{0}".format(i)].append(line[178+34*i: 180+34*1])
                racer_dict["numK1_{0}".format(i)].append(line[180+34*i: 182+34*1])
                racer_dict["numS0_{0}".format(i)].append(line[182+34*i: 184+34*1])
                racer_dict["numS1_{0}".format(i)].append(line[184+34*i: 186+34*1])
                racer_dict["numS2_{0}".format(i)].append(line[186+34*i: 188+34*1])

    racer_df = pd.DataFrame(racer_dict)
    racer_df = racer_df.set_index("racerId")

    return racer_df

def load_race_results_supplementary_data(race_results_supplementary_path):
    race_results_supplementary_df_list = []
    for filename in glob.glob(race_results_supplementary_path):
        race_results_supplementary_df_ = pd.read_csv(filename)
        race_results_supplementary_df_list.append(race_results_supplementary_df_)

    race_results_supplementary_df = pd.concat(race_results_supplementary_df_list)
    race_results_supplementary_df["date"] = pd.to_datetime(race_results_supplementary_df["date"])

    return race_results_supplementary_df


def make_race_result_df(race_results_file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../data/results_race/K1*.TXT'),
                        racelist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/racelist/1*.csv"),
                        beforeinfo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/beforeinfo/1*.csv")
                        ):

    """
    ダウンロードファイルのデータに、公式サイトクロールで得られるデータをmergeしたdfを作成

    :return: merged_df 開催日時、開催場所、レースナンバーをindexにして表現できるレース情報をまとめたdf

    """

    # それぞれのdfをロード
    merged_df = load_race_results(race_results_file_path)
    racelist_df = load_race_results_supplementary_data(racelist_path)
    beforeinfo_df = load_race_results_supplementary_data(beforeinfo_path)

    # マージ用のindexを用意 (レースナンバー、開催地、開催日)
    column_list_index = ["raceNumber", "venue", "date"]

    # merged_df (ダウンロードデータ）からdropするカラム名のリストを作成
    race_result_drop_list = ["win", "winOdds", "place_1", "placeOdds_1", "place_2",
                             "placeOdds_2", "exacta", "exactaOdds", "quinella", "quinellaOdds",
                             "wide_1", "wideOdds_1", "wide_2", "wideOdds_2", "wide_3", "wideOdds_3",
                             "trifecta", "trifectaOdds", "trio", "trioOdds"
                             ]
    # drop
    merged_df.drop(columns=race_result_drop_list, inplace=True)

    # racelist_dfからdropするカラム名のリストを作成
    racelist_drop_list = []
    for i in range(1, 7):
        racelist_drop_list.append("boatNo_{0}".format(i))   # 被った情報
        racelist_drop_list.append("motorNo_{0}".format(i))  # 被った情報
        racelist_drop_list.append("racer_{0}".format(i))  # 被った情報
        racelist_drop_list.append("racer_id_{0}".format(i))  # 被った情報

        # 最近のレース結果はとりあえず使わないしカラム多い
        for j in range(1, 12):
            racelist_drop_list.append("CS_frame_{0}_{1}".format(i, j))
            racelist_drop_list.append("CS_rank_{0}_{1}".format(i, j))
    # drop
    racelist_df.drop(columns=racelist_drop_list, inplace=True)

    # racelistをマージ
    merged_df = pd.merge(merged_df, racelist_df,
                         how="left", on=column_list_index
                         )

    # beforeinfo_dfからdropするカラム名のリストを作成
    beforeinfo_drop_list = ["temperature", "weather", "wind_speed", "wave_height"]
    for i in range(1, 7):
        beforeinfo_drop_list.append("exhibitionTime_{0}".format(i))
        beforeinfo_drop_list.append("racer_{0}".format(i))
    # drop
    beforeinfo_df.drop(columns=beforeinfo_drop_list, inplace=True)

    merged_df = pd.merge(merged_df, beforeinfo_df,
                         how="left",
                         on=column_list_index
                         )

    return merged_df


def merge_statistic_df(race_result_df, racer_df):
    """

    :param race_result_df: 開催日時、開催場所、レース番号をindexにとるdf.
                            普通make_race_result_dfでreturnされたdfを入れる
    :param racer_df:
    :return:

    """

    # racer_dfのデータの一部をマージ
    for i in range(1, 7):
        # 枠ごとの平均スタート順位，枠ごとの連帯率をマージ
        for_merge_df = racer_df[["racerName_ch",
                                 "class",
                                 "aveST_frame{0}".format(i),
                                 "placeRate_frame{0}".format(i)
                                 ]]

        # レーサー名に対して一つしかないカラムたちは枠版を付けたカラム名に変更
        for_merge_df = for_merge_df.rename(columns={'class': 'class_{0}'.format(i)})

        # レーサー名をkeyとしてマージ
        # TODO: ほんとはracer IDのほうがいい
        merged_df = pd.merge(race_result_df, for_merge_df, how="left",
                             left_on="racerName_{0}".format(i), right_on="racerName_ch")

    return merged_df


if __name__ == "__main__":

    # the_race_result_df = load_race_results()
    # print(the_race_result_df[["date", "venue", "raceNumber"]])

    # racer_df = load_racer_data()
    # print(racer_df[["dateFrom", "dateTo"]])

    # the_race_results_supplementary_df = load_race_results_supplementary_data(race_results_supplementary_path)
    # print(the_race_results_supplementary_df)

    # the_beforeinfo_df = load_race_results_supplementary_data(beforeinfo_path)
    # print(the_beforeinfo_df["date"])

    the_merged_df = make_race_result_df()
    # the_merged_df.to_csv("/Users/grice/mywork/boatrace/data/motor_and_boat/test<.csv")
    print(the_merged_df[["exhibition_cource_1", "exhibition_ST_1"]])