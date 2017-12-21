from telebot import TeleBot, types
import config
import requests
import json

from kitsu import *   #  всё по работе с kitsu
import structure # (не додумана) всё для построения общения с ботом

genres = genres
bot = TeleBot(config.token)
cmd = structure.comands
chosenGenres = []
new_anime = []
summ = {}
lastCommand = {}
usersAnswer = {}

def chengeCommand(message, text):
        global lastCommand
        if(message.chat.id in lastCommand):
                lastCommand[message.chat.id] = text
        else:
                lastCommand.update({message.chat.id: text})


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
        bot.send_message(message.chat.id, 'Добро пожаловать. Я Kitsu, рекомендующий аниме.\nНапишите "Хочу аниме" чтобы начать искать аниме.\nТак же я могу порекомендовать вам аниме, основываясь на ваших предпочтениях.\nДля этого просто напиши мне "порекамендуй"')
        chengeCommand(message, '/start')

        
        
@bot.message_handler(func=lambda message: True)
def any_message(message):
        global lastCommand
        # Вызов функции  поределения команды
        if(message.text.lower() in cmd.keys() or message.text in genres):
                lC = lastCommand[message.chat.id]
                if(lC == 'бред' or lC == '...' or lC == '/start'):
                        chengeCommand(message, 'хочу аниме')
                if(message.text.lower() == 'порекомендуй'):
                        chengeCommand(message, 'порекомендуй')
                chooseComand(lastCommand[message.chat.id], message)
        else:
        # Обработчик любой непонятной херни непонятной херни
                if(message.chat.id in lastCommand):
                        lC = lastCommand[message.chat.id]
                        
                        if(not(message.text.lower() in cmd.keys()) and lC != 'бред' and lC!='...' and message.text != 'Назад'):
                                chengeCommand(message, 'бред')
                                bot.send_message(message.chat.id,"Извините, но я вас не понимаю")
                        elif(lastCommand[message.chat.id] == 'бред'):
                                chengeCommand(message, '...')
                                bot.send_message(message.chat.id,"Всё равно не понимаю")
                        else:
                                chengeCommand(message, '...')
                                if(message.text != 'Назад'):
                                        bot.send_message(message.chat.id,"...")   
                else:
                        chengeCommand(message, 'бред')
                        bot.send_message(message.chat.id,"Извините, но я вас не понимаю")

def chooseComand(cmd, message):
        global chosenGenres, new_anime, usersAnswer
        if (cmd == 'хочу аниме'):
                if (message.text in genres.keys()):
                        chosenGenres = genres[message.text]
                        chooseParam(message)
                else:
                        chooseGenersFunc(message,'хочу аниме')
                        bot.send_message(message.chat.id,'Прошу выберите из предложенных')
        elif(cmd == 'выбор состояния'):
                if(message.text == 'По новизне'):
                        new_anime = AskNAnime(chosenGenres,'endDate',20,'desk')
                        animeList(message, new_anime)
                elif(message.text == 'По популярности'):
                        new_anime = AskNAnime(chosenGenres,'averageRating',20,'desk')
                        animeList(message, new_anime)
                elif(message.text == 'Вернуться'):
                        chengeCommand(message, 'бред')
                        print("Откатывает состояние команд")
        elif(cmd == 'порекомендуй'):
                if(message.text.lower() == 'порекомендуй'):
                        chooseGenersFunc(message, 'порекомендуй')
                else:
                        chosenGenres = genres[message.text]
                        new_anime = AskNAnime(chosenGenres,'averageRating',20,'desk')
                        chengeCommand(message, 'опрос')                        
                        summ[message.chat.id] = 0
                        bot.send_message(message.chat.id,"\t"+new_anime[0]['title']+"\nhttps://kitsu.io/anime/"+new_anime[0]['id'])
                        usersAnswer[message.chat.id] = []
                        usersAnswer[message.chat.id].append({'id': new_anime[0]['id'],'val':-1})
                        recomend(message)
        elif(cmd == 'опрос'):
                if(summ[message.chat.id]<5):
                        val = -1
                        for elem in usersAnswer:
                                if(message.text == 'Нравится'):
                                        val = 5
                                if(message.text == 'Не нравится'):
                                        val = 2
                                if(message.text == 'Не знаю'):
                                        val = 0
                        arr = usersAnswer[message.chat.id]
                        idA = '1'
                        for item in arr:
                                if(item['val'] == -1):
                                        item['val'] = val
                                        idA = item['id']
                        new_anime = [item for item in new_anime if item["id"] !=idA]
                        summ[message.chat.id] += 1
                        bot.send_message(message.chat.id,"\t"+new_anime[0]['title']+"\nhttps://kitsu.io/anime/"+new_anime[0]['id'])
                        usersAnswer[message.chat.id].append({'id': new_anime[0]['id'],'val':-1})
                        recomend(message)
                else:
                        chengeCommand(message, 'бред')
                        usersAnswer[message.chat.id] =[x for x in usersAnswer[message.chat.id] if x['val']!=0]
                        for j in range(0,4):
                                bot.send_message(message.chat.id,"Подождите, это может занять некоторое время.")
                                id_users=FindUsersId(usersAnswer[message.chat.id],10)
                                if(len(id_users) > 0):
                                        TableAnimeUsers=FindAnimeFromUsers(id_users)
                                        user={"avg":0,"names":{},"values":{}}
                                        avg=0
                                        for item in usersAnswer[message.chat.id]:
                                                val=float(item["val"])
                                                user["values"][str(item["id"])]=val
                                                avg+=val
                                        user["avg"] = avg/len(usersAnswer[message.chat.id])
                                        #Делаем отбор похожих юзеров
                                        TableAnimeUsers["current"]=user
                                        similarity=Similarity(TableAnimeUsers,"current",'values')
                                        nearestUsers=find5Nearest(similarity,"current")
                                        DataAns = CreateAns(TableAnimeUsers,nearestUsers,usersAnswer[message.chat.id])
                                        print(DataAns)
                                        if(len(DataAns) == 0):
                                                DataAns = AskNAnime(chosenGenres,'averageRating',7,'desk')
                                        
                                        length = 10 if len(DataAns) > 10 else len(DataAns)
                                        bot.send_message(message.chat.id,"Рекомендую такие анимешки")
                                        for i in range(0, length):
                                                bot.send_message(message.chat.id,"\t"+DataAns[i]['title']+"\nhttps://kitsu.io/anime/"+DataAns[i]['id'])
                                        break                                               
                                else:
                                        bot.send_message(message.chat.id,"Проблемы с сервером (500)")
                                        
                                
                        
        
                        
                

def animeList(message, anime):
        for elem in anime:
                bot.send_message(message.chat.id,"\t"+elem['title']+"\nhttps://kitsu.io/anime/"+elem['id'])
        

def chooseParam(message):
        keyboard = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton('По новизне')
        btn2 = types.KeyboardButton('По популярности')
        btn3 = types.KeyboardButton('Назад')
        keyboard.add(btn1,btn2,btn3)
        chengeCommand(message, 'выбор состояния')
        bot.send_message(message.chat.id, "Выбирать:",reply_markup=keyboard)


def chooseGenersFunc(message, arg):
        keyboard = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True)
        arr = []
        for name in genres.keys():
                arr.append(name)
        for i in range(0,11,3):
                btn1 = types.KeyboardButton(text=arr[i])
                btn2 = types.KeyboardButton(text=arr[i+1])
                btn3 = types.KeyboardButton(text=arr[i+2])
                keyboard.add(btn1,btn2,btn3)
        btn = types.KeyboardButton('Назад')
        keyboard.add(btn)
        chengeCommand(message, arg)
        bot.send_message(message.chat.id, "Выберите свой жанр",reply_markup=keyboard)
                

def recomend(message):
        keyboard = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton('Нравится')
        btn2 = types.KeyboardButton('Не нравится')
        btn3 = types.KeyboardButton('Не знаю')
        keyboard.add(btn1,btn2,btn3)
        bot.send_message(message.chat.id, "Выберите:",reply_markup=keyboard)

                        
                

       

    


if __name__ == '__main__':
    bot.polling(none_stop=True)
