import csv
import requests


# read all from file
def ReadFile(filename):
    f = open(filename)
    table = []
    # cчитывает построчно, игнорируя пробелы после разделителя
    for row in csv.reader(f, skipinitialspace=True):
        table.append(row)
    f.close()
    return table


# parce column names
# возвращает кортеж - неизменяемый список фильмов
def GetColumnsList(table):
    columns = table[0]
    columns.pop(0)
    return tuple(columns)


# parce row names
# возвращает кортеж - неизменяемый список пользователей
def GetRowsList(table):
    i = 1
    rows = []
    while i < len(table):
        row = table[i][0]
        rows.append(row)
        i = i + 1
    return tuple(rows)


# parce mentions for users
# возвращает словарь словарей
# пользователь:фильм:оценка
def GetMentionDict(table):
    i = 1
    mentions = dict()
    for user in g_users:
        mentions[user] = dict()
        j = 1
        for mv in g_movies:
            rate = int(table[i][j])
            if rate > 0:
                mentions[user][mv] = rate
            j = j + 1
        i = i + 1
    return mentions


# parce mentions for users
# возвращает словарь словарей
# пользователь:(выходные/будни),фильм:оценка
def GetMentionDict2(table_d, table_c):
    i = 1
    mentions = dict()
    for user in g_users:
        mentions[user] = dict()
        j = 1
        for mv in g_movies:
            rate = int(table_d[i][j])
            if rate > 0:
                if table_c[i][j] in ("Sun", "Sat"):
                    mentions[user][(0, mv)] = rate
                else:
                    mentions[user][(1, mv)] = rate
            j = j + 1
        i = i + 1
    return mentions


# cosinus метрика сходства для пары словарей
# возвращает число
import math


def GetSim(dict1, dict2):
    sum1 = 0
    sum2 = 0
    sum12 = 0
    sim = 0
    for key in dict1:
        if key in dict2:
            rate1 = dict1[key]
            rate2 = dict2[key]

            if rate1 > 0 and rate2 > 0:
                sum1 = sum1 + rate1 * rate1
                sum2 = sum2 + rate2 * rate2
                sum12 = sum12 + rate1 * rate2

    if sum12 > 0:
        sim = sum12 / (math.sqrt(sum1) * math.sqrt(sum2))
    return sim


# метрики сходства для выбранного словаря с остальными
# возвращает словарь
# имя словаря:метрика сходства
def GetSimDict(item, d_values):
    sims = dict()

    for it in d_values:
        if it != item:
            sim = GetSim(d_values[it], d_values[item])
            if sim > 0:
                sims[it] = sim
    return sims


# сортирует словарь по значению, по убыванию
# возвращает n_sims элементов из топа
def GetBestSims(sims, n_sims):
    best_sims = sorted(sims.items(), key=lambda item: item[1], reverse=True)[:n_sims]
    return best_sims


# расчитывает оценки для данного user
# возвращает словарь
def GetPrediction(user, d_movie, d_values, best_sims):
    r_u = sum(d_values[user].values()) / len(d_values[user])

    new_values = dict()

    for movie in d_movie:
        if movie not in d_values[user]:
            temp_sum1 = 0
            temp_sum2 = 0

            for item in best_sims:
                v_user = item[0]
                v_sim = item[1]
                r_v = sum(d_values[v_user].values()) / len(d_values[v_user])
                if movie in d_values[v_user]:
                    r_vi = d_values[v_user][movie]
                    temp_sum1 = temp_sum1 + (r_vi - r_v) * v_sim
                    temp_sum2 = temp_sum2 + v_sim
            if temp_sum2 > 0:
                r_ui = r_u + temp_sum1 / temp_sum2
            else:
                r_ui = -1

            new_values[movie] = r_ui

    return new_values


def GetRecommendation(mentions):
    sort_mentions = sorted(mentions.items(), key=lambda item: item[1], reverse=True)
    return sort_mentions[0]


def main():
    global g_users
    global g_movies

    table_data = ReadFile("data.csv")
    table_context = ReadFile("context.csv")

    g_movies = GetColumnsList(table_data)
    g_users = GetRowsList(table_data)

    mentions = GetMentionDict(table_data)

    user_id = input("Input id (1-40):  ")
    user = "User " + user_id

    sims = GetSimDict(user, mentions)
    best_sims = GetBestSims(sims, 5)
    new_mentions1 = GetPrediction(user, g_movies, mentions, best_sims)

    print("Most correlated with ", user, " users:")
    for it in best_sims:
        print("  ", it[0], " with Coeff = ", round(it[1], 2))
    for movie in new_mentions1:
        print("For ", movie, " expected rate is ", round(new_mentions1[movie], 2))

    mentions2 = GetMentionDict2(table_data, table_context)
    sims = GetSimDict(user, mentions2)
    best_sims = GetBestSims(sims, 5)
    new_mentions2 = GetPrediction(user, g_movies, mentions, best_sims)

    print("Most correlated with ", user, " users:")
    for it in best_sims:
        print("  ", it[0], " with Coeff = ", round(it[1], 2))
    for movie in new_mentions2:
        print("For ", movie, " expected rate is ", round(new_mentions2[movie], 2))

    best_movie = GetRecommendation(new_mentions2)

    print("We suggest ", best_movie[0], ", expected rate is ", round(best_movie[1], 2))

    url = 'http://cit-home1.herokuapp.com/api/rs_homework_1'
    headers = {'Content-type': 'application/json'}

    r = requests.post(url, headers=headers, json={'user': 12})
    print(r.status_code, r.reason)
    print(r.text)

    return

