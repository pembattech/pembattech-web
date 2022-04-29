from flask import Flask, render_template
import json, sqlite3, time, threading

from yt_stats import YTstats

template_dir = "template"
app = Flask(__name__, template_folder=template_dir)

def get_db_connection():
    conn = sqlite3.connect('yt_stats.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS PTT__YT_video_data(PUBLISHED_AT TEXT, TITLE TEXT, THUMBNAIL TEXT, LINK TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS PTT__YT_video_count(NAME TEXT, TOTAL_VIDEO TEXT)")
    
    return cursor, conn

def read_yt_stats():
    while True:
        API_KEY = 'xyz'
        CHANNEL_ID = 'xyz'

        cursor, conn = get_db_connection()
    
        yt = YTstats(API_KEY, CHANNEL_ID)
        yt.extract_all()
        yt.dump()

        f = open('ptt.json')
        data = json.load(f)

        videocount = data[CHANNEL_ID]["channel_statistics"]["videoCount"]
        result = conn.execute('SELECT * FROM PTT__YT_video_count').fetchone()
        if result == None or 0:
            cursor.execute("INSERT INTO PTT__YT_video_count(NAME, TOTAL_VIDEO) VALUES (?, ?)", ("PTT_VIDEOS_COUNT", videocount))
        else:
            cursor.execute("UPDATE PTT__YT_video_count SET TOTAL_VIDEO = '{videocount}' WHERE NAME = '{PTT_VIDEOS_COUNT}'")
        conn.commit()

        vid_ids = []
        for vid_id in data[CHANNEL_ID]["video_data"]:
            vid_ids.append(vid_id)

        publishedAt_= []
        title_ = []
        thumbnails_ = []
        link_ = []

        for i in vid_ids:
            print(i)
            _published_At_ = data[CHANNEL_ID]["video_data"][f"{i}"]["publishedAt"]
            _title_ = data[CHANNEL_ID]["video_data"][f"{i}"]["title"]
            _thumbnails_= f"https://i.ytimg.com/vi/{i}/hqdefault.jpg"
            _link_ = f"https://www.youtube.com/watch?v={i}"

            publishedAt_.append(_published_At_)
            title_.append(_title_)
            thumbnails_.append(_thumbnails_)
            link_.append(_link_)
        
        for published_dt, name, picture, link in zip(publishedAt_, title_, thumbnails_, link_):
            cursor.execute(f"SELECT * FROM PTT__YT_video_data WHERE PUBLISHED_AT = '{published_dt}'")
            if cursor.fetchone():
                return False
            else:
                cursor.execute("INSERT INTO PTT__YT_video_data(PUBLISHED_AT, TITLE, THUMBNAIL, LINK) VALUES (?, ?, ?, ?)", (published_dt, name, str(picture), str(link)))
                conn.commit()
        conn.close()
        time.sleep(600) # i.e 10 minutes
threading.Thread(target=read_yt_stats).start()


@app.route("/")
def homepage():
    conn = get_db_connection()[1]
    vid_count = conn.execute('SELECT * FROM PTT__YT_video_count WHERE NAME = "PTT_VIDEOS_COUNT"').fetchone()[1] # 0 index is for NAME FIELD, 1 index for TOTAL_VIDEO FIELD
    vid_data = conn.execute('SELECT * FROM PTT__YT_video_data').fetchall()

    vid_publisheddt = []
    vid_name = []
    vid_picture = []
    vid_link = []

    for row in vid_data:
        vid_publisheddt.append(row[0])
        vid_name.append(row[1]) 
        vid_picture.append(row[2])
        vid_link.append(row[3])

    conn.close()

    return render_template("home.html", num_of_vidcards = int(vid_count), vid_info = zip(vid_publisheddt, vid_name, vid_picture, vid_link))

@app.route("/about")
def about():
    return render_template("about.html")
    
@app.route("/ytvideos")
def yt_Videos():
    conn = get_db_connection()[1]
    vid_count = conn.execute('SELECT * FROM PTT__YT_video_count WHERE NAME = "PTT_VIDEOS_COUNT"').fetchone()[1] # 0 index is for NAME FIELD, 1 index for TOTAL_VIDEO FIELD
    vid_data = conn.execute('SELECT * FROM PTT__YT_video_data').fetchall()

    vid_publisheddt = []
    vid_name = []
    vid_picture = []
    vid_link = []

    for row in vid_data:
        vid_publisheddt.append(row[0])
        vid_name.append(row[1]) 
        vid_picture.append(row[2])
        vid_link.append(row[3])

    conn.close()

    return render_template("ytvideos.html", num_of_vidcards = int(vid_count), vid_info = zip(vid_publisheddt, vid_name, vid_picture, vid_link))

@app.route("/cheatsheet")
def cheatsheet():
    return render_template("comingsoon.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/tutorials")
def tutorials():
    return render_template("comingsoon.html")

@app.route("/community")
def community():
    return render_template("community.html")



if __name__ == "__main__":
    app.run(port="7782", debug=True)

