import requests
import json
from datetime import datetime
from time import sleep
genres ={'Экшен'        :'Action',
         'Драмма'       :'Drama',
         'Роман'        :'Romance',
         'Школа'        :'School',
         'Фентези'      :'Fantasy',
         'Этти'         :'Ecchi',
         'Трагедия'     :'Tragedy',
         'Сёнен-ай'     :'Shounen Ai',
         'Сёдзе-ай'     :'Shoujo Ai',
         'Психология'   :'Psychological',
         'Космос'       :'Space',
         'Меха'         :'Mecha'}


def req(path):
    ''' Get request to API '''
    headers = {'content-type':'application/vnd.api+json','Accept':'application/vnd.api+json'} 
    url = 'https://kitsu.io/api/edge'
    response = requests.get(url+path,headers=headers)
    return json.loads(response.text)

def AskNAnime(genre,sorting='endDate',count=3,sort='ask'):
    '''Возвращает count новых "законченных" аниме, фильтр по genre. (сортированы по средней популярности)
    {
    'title':          'Fairy Tail Movie 2: Dragon Cry',
    'popularityRank': 2643,
    'averageRating':  '56.82',
    'id':             '10922',
    'endDate':        '2017-05-06'
    }
    '''
    path='/anime?filter[genres]='+str(genre)
    path+='&filter[status]=finished'
    path+='&sort=-'+str(sorting)
    path+='&page[limit]='+str(count)
    jsonObj=req(path)
    arrAns=[]
    if jsonObj.get('errors'):
        return arrAns
    jsonObj=jsonObj["data"]
    i=1
    for item in jsonObj:
        name=list(item["attributes"]["titles"].keys())[0]
        popularityRank=str(item["attributes"]["popularityRank"])
        averageRating=str(item["attributes"]["averageRating"])
        arrAns.append({})
        i=len(arrAns)-1
        arrAns[i]["title"]=item["attributes"]["titles"][name]
        arrAns[i]["popularityRank"]=float(popularityRank)if(popularityRank!='None') else 0
        arrAns[i]["averageRating"]=float(averageRating)if(averageRating!='None') else 0
        arrAns[i]["id"]=item["id"]
        arrAns[i]["endDate"]=item["attributes"]["endDate"]
        arrAns[i]["annotation"]=item["attributes"]["synopsis"]
    reversev=True if sort=='ask' else False
    return sorted(arrAns,key=lambda anime:anime[sorting],reverse=reversev)
'''
#Найдем 20 новых аниме (сортировка по endDate)
new_anime=AskNAnime(genre,'endDate',20,'desk')
print(new_anime)
#возьмем для опроса 1 новых самых популярных аниме:
new_anime=new_anime[0:1]
print(new_anime)
#Найдем 20 самых популярных аниме (сортировка по averageRating)
popular_anime=AskNAnime(genre,'averageRating',20)
#возьмем для опроса 4 самых популярных аниме:
popular_anime=popular_anime[0:4]
print(popular_anime)
#Допустим оценки user:
user_values=[{'id':'12611','val':5},{'id':'3936','val':5},{'id':'6448','val':3},{'id':'176','val':5},{'id':'1','val':0}]
#Выберем только те аниме, которые user смотрел
user_values=[x for x in user_values if x['val']!=0]
'''
def FindUsersId(user_values,count=10):
    ''' Находит юзеров, что смотрели хотя бы одно аниме '''
    sleep(0.50)
    UsersId=[]
    if len(user_values)==0:
        print("FindUsersId: len(user_values)==0 !!!")
        return UsersId
    path='/library-entries?filter[animeId]='+str(user_values[0]['id'])
    for i in range(1,len(user_values)):
        path+=','+str(user_values[i]['id'])
    #path+='&sort=-ratingTwenty'
    path+='&page[limit]='+str(count)
    jsonObj=req(path)
    if not jsonObj.get('data'):
        print("no id for users")
    else:
        jsonObj=jsonObj["data"]
        for item in jsonObj:
            UsersId.append(item["id"])
    return UsersId
'''
#Найдем по 10 id_users что смотрели те же аниме:
id_users=FindUsersId(user_values,10)
print(id_users)
'''
#Найдем по 10 аниме у users с их оценками
def FindAnimeFromUsers(id_users,count=10):
    UsersAnimes=[]
    for user in id_users:
        sleep(0.10)
        id_user=str(user)
        path='/library-entries?filter[userId]='+str(id_user)
        path+='&filter[kind]=anime'
        path+='&sort=-rating'
        path+='&include=anime'
        path+='&page[limit]='+str(count)
        jsonObj=req(path)
        if jsonObj.get('errors'):
            print("no")
        else:
            jsonData=jsonObj["data"]
            UsersAnimes.append({})
            i=len(UsersAnimes)-1
            user_name="user "+str(id_user)
            UsersAnimes[i]["avg"]=0
            UsersAnimes[i]["names"]={}
            UsersAnimes[i]["values"]={}
            if len(jsonData)>0:
                animeObj=jsonObj["included"]
                avg=0
                for j in range(0,len(animeObj)):
                    id_anime=animeObj[j]["id"]
                    rateing=float(jsonData[j]['attributes']['rating'])
                    UsersAnimes[i]["values"][str(id_anime)]=rateing
                    avg+=rateing
                    name=list(animeObj[j]["attributes"]["titles"].keys())[0]
                    UsersAnimes[i]["names"][id_anime]=animeObj[j]["attributes"]["titles"][name]
                UsersAnimes[i]["avg"]=avg/len(animeObj)
                
    UsersAnimes = {str(i): UsersAnimes[i] for i in range(0, len(UsersAnimes))}    
    return UsersAnimes


import operator
import math
#Create similarity dict{'name_user':'simUV'} for user-argument
def Similarity(dictionaryUsers,user,key='values'):
    similarity={}
    for name in dictionaryUsers.keys():
        if str(name)==user:
            similarity[name]=-1
        else:
            simUV = 0
            usqrt = 0
            vsqrt = 0
            for movie in dictionaryUsers[user][key].keys():
                if dictionaryUsers[user][key][movie]!=0 and (movie in dictionaryUsers[name][key].keys()):
                    simUV+=dictionaryUsers[user][key][movie]*dictionaryUsers[name][key][movie]
                    usqrt+=dictionaryUsers[user][key][movie]**2
                    vsqrt+=dictionaryUsers[name][key][movie]**2
            if simUV>0:
                similarity[name]=round(simUV/((usqrt**(1/2))*(vsqrt**(1/2))),3)
            else:
                similarity[name] = 0
    return similarity

#find "count" nearest users for current user-argument 
def find5Nearest(similarity,user,count=3):
    return dict(sorted(similarity.items(), key=operator.itemgetter(1), reverse=True)[0:count])

'''                                                   
TableAnimeUsers=FindAnimeFromUsers(id_users)
print(TableAnimeUsers)'''
#Дальше алгоритм рекомендаций (может еще добавить к этим оценкам, оценки за выбранные пользователем аниме)

def CreateAns(TableAnimeUsers,nearestUsers,user_values):
    DataAns=[]
    userAns=[item["id"] for item in user_values]
    for user in nearestUsers.keys():
        for anime in TableAnimeUsers[user]["names"].keys():
            DataAns.append({"id":anime,"title":TableAnimeUsers[user]["names"][anime]})
        DataAns = [item for item in DataAns if item["id"] not in userAns]
    return DataAns
