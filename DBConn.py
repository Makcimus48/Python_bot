import psycopg2
import config
import requests


def connect():
    db = psycopg2.connect(dbname=config.dbname, host=config.host,
                          port=config.port, user=config.user, password=config.passwd)
    return db



def selectAllUsers():
    db = connect()
    cur = db.cursor()
    try:
        cur.execute('SELECT * from public.UserOpinion;')
    except:
        print("I can't SELECT from UserOpinion")

    rows = cur.fetchall()
    return(rows)

def selectActivity(chat_id):
    db = connect()
    cur = db.cursor()
    rows = []
    try:
        cur.execute("""
                        SELECT * FROM public.UserOpinion
                        WHERE ID = %s;
                        """,
                    (chat_id))
        rows = cur.fetchall()
    except:
        print("I can't SELECT into UserOpinion")

    return (rows)


def addUser(chat_id,anime_id, mark, title):
    db = connect()
    cur = db.cursor()
    try:
        cur.execute("""
                    INSERT INTO public.UserOpinion(ID,AnimeID,Mark,AnimeTitle) 
                    VALUES (%s,%s,%s,%s);
                    """,
                    (chat_id,anime_id, mark, title))
        print('DONE')
        db.commit()
    except:
        print("I can't add row")

