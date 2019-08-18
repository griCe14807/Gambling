# -*- coding=utf8 =*-
# 必要なモジュールのインポート

from sklearn.linear_model import LogisticRegression
import pickle

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '../../data_preparing/'))
sys.path.append(os.path.join(current_dir, '../../analyze/'))

# my module
import loader
import analyzer_conf


# logistic regressionを利用した学習

def make_df_for_analyze(merged_df, fv_list, column_list_label, odds_list):
    """
    parameters
        fv_list: dfのうち、特徴量として用いるカラム名のリスト
        column_list_label: dfのうち、labelとして用いるカラム名のリスト
    """

    # 解析用dfを作成
    fv_label_odds_df = merged_df[fv_list + column_list_label + odds_list]

    # nanを含む行を削除
    fv_label_odds_df = fv_label_odds_df.dropna()

    # oddsはないバージョンのdf
    fv_label_df = fv_label_odds_df[fv_list + column_list_label]

    # クラスカラムを，A1 =0, A2 = 1のように数字に変換する
    class_dict = {"A1": 0, "A2": 1, "B1": 2, "B2": 3}
    for key, value in class_dict.items():
        fv_label_df.replace(key, value, inplace=True)

    # なぜかdtypeがstrになっちゃうのでintに戻す
    fv_label_df = fv_label_df.astype(float)

    # ラベルをbooleanに変換
    fv_label_df = analyzer_conf.make_label_boolean_ver1(fv_label_df, column_list_label)
    print("解析用dfの行数は.{0}".format(len(fv_label_df)))
    print(fv_label_df.dtypes)

    """
    # 特徴量を標準化
    fv_label_df = analyzer_conf.standerdize_feature_values(
        fv_label_df, column_list_label)
    """
    return fv_label_df, fv_label_odds_df


def separate_train_test_dataset(for_analysis_df, train_data_ratio):
    # 解析用df（特徴量+label）を、学習用データとテストデータのarrayに分ける
    train_size = int(len(for_analysis_df) * train_data_ratio)
    train_data = for_analysis_df[:train_size].values
    test_data = for_analysis_df[train_size:].values

    return train_data, test_data, train_size


def learn_logistic_regression(train_data, column_list_label):
    """
    1枠が1着になるかどうか？2枠以降に関しては3着以内に入るかどうか？を scikit-lernのlogistic regressionを用いて学習する。
    複数のラベルをリストとして入力することが可能で、戻り値はそれぞれのlabelに対して学習を行なった結果のモデルを各要素にもつリスト

    return
        clf_list: 各ラベルについて学習したモデルのlist

    TODO
        ラベルの作成方法などもinput parameterとして指定できた方がいい。
        むしろregressionの方法もinputにして超汎用的な関数を外側に作るか？

    """
    # ラベルとしてもちいる部分の数。labelと特徴量を分ける際に使用、
    num_labels = len(column_list_label)

    # 特徴量部分のarray
    train_x = train_data[:, :-num_labels]

    # ロジスティック回帰を行なった結果得られるオブジェクトをリストに格納
    clf_list = []

    for i, column_label in enumerate(column_list_label):
        # ラベルを指定
        train_t = train_data[:, - num_labels + i]

        # ロジスティック回帰
        clf = LogisticRegression()
        clf.fit(train_x, train_t)

        clf_list.append(clf)

    return clf_list


if __name__ == "__main__":

    # ----------input-------------
    # 解析に使う特徴量カラム
    fv_list = []
    for i in range(1, 7):
        # 各枠のレーサーのクラス
        fv_list.append("class_{0}".format(i))
        # 各枠の平均ST
        fv_list.append("aveST_frame{0}".format(i))
        # 連帯率
        fv_list.append("placeRate_frame{0}".format(i))
        # 展示タイム
        fv_list.append("exhibitionTime_{0}".format(i))
        # 各モーターの2連率, 3連率
        fv_list.append("motor_place2Ratio_{0}".format(i))
        fv_list.append("motor_place3Ratio_{0}".format(i))

        # 各ボートの2連率, 3連率
        fv_list.append("boat_place2Ratio_{0}".format(i))
        fv_list.append("boat_place3Ratio_{0}".format(i))

    # 解析に使うラベルカラム: 今回は一枠が一着になるかどうか？を予測
    column_list_label = ["rank_{0}".format(i) for i in range(1, 7)]

    # 回収率計算に使用するオッズラベルのリスト
    odds_list = ["win", "winOdds",
                 "place_1", "placeOdds_1",
                 "place_2", "placeOdds_2",
                 "exacta", "exactaOdds",
                 "quinella", "quinellaOdds",
                 "wide_1", "wideOdds_1",
                 "wide_2", "wideOdds_2",
                 "wide_3", "wideOdds_3",
                 "trifecta", "trifectaOdds",
                 "trio", "trioOdds"]

    # データのうち、教師データとして使う割合（残りをテストデータとして用いる）
    train_data_ratio = 1

    # --------------------------------

    # main

    # 過去のレース結果をdfとして取得
    the_merged_df = loader.main()
    # dfをソート
    the_merged_df = the_merged_df.sort_values(["date", "venue", "raceNumber"])
    # print(the_merged_df["exhibitionTime_1"])

    # 学習に使う特徴量、ラベルを用意
    fv_label_df, fv_label_odds_df = make_df_for_analyze(the_merged_df, fv_list, column_list_label, odds_list)

    # 学習データおよびテストデータを用意
    train_data, test_data, train_size = separate_train_test_dataset(fv_label_df, train_data_ratio)

    # 学習
    clf_list = learn_logistic_regression(train_data, column_list_label)

    # 学習結果をファイルに出力
    output_file = os.path.join(current_dir, 'LR_dump')
    pickle.dump(clf_list, open(output_file, 'wb'))

    # 以下データの正しさ確認用に最適化された結果の切片と重みを取得
    for i, clf in enumerate(clf_list):
        intercept = clf.intercept_
        coef = clf.coef_
        print("切片は{0}".format(intercept))
        for j in range(coef.shape[1]):
            print(fv_list[j], coef[0, j], "\n")
