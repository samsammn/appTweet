from flask import Flask, request, jsonify, redirect, url_for, session, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename

# from user import user_api
import os, json, datetime, time, jwt
import psycopg2, psycopg2.extras

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asalaja'
cors = CORS(app)

# Membuat koneksi ke database di PostGreSQL
con = psycopg2.connect(database=os.getenv('DATABASE'),user=os.getenv('USER'),password=os.getenv('PASSWORD'),host=os.getenv('HOSTDB'),port=os.getenv('PORTDB'))
ALLOWED_EXTENSIONS = set(['jpg','jpeg','png','gif','mkv','mp4'])
skey = "moemoekyun"

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/cekLogin', methods=['POST'])
def cekLogin():
    try:
        token = request.json['token']
        decod = jwt.decode(token, skey, algorithms=['HS256'])
        idUser = decod['id']

        curCekLogin = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        curCekLogin.execute("Select * from users where id=%s",(idUser,))
        jml = curCekLogin.rowcount

        if jml > 0:
            return "Sukses", 200
        else:
            return "Gagal", 400
    except:
        return "Gagal", 400

@app.route('/signUp', methods=['POST'])
def signUp():
    # Mengambil data dari inputan user
    username = request.json['username']
    fullname = request.json['fullname']
    email = request.json['email']
    password = request.json['password']

    cursorSignUp = con.cursor()
    cursorSignUp.execute("Insert into users (username,fullname,email,password,bio,photoprofile) values (%s,%s,%s,%s,%s,%s)",(username,fullname,email,password,'','none'))
    con.commit()

    return "Sukses", 201

@app.route('/signIn', methods=['POST'])
def signIn():

    email = request.json['email']
    password = request.json['password']

    cursorSignIn = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorSignIn.execute("Select * from users where email = %s and password = %s",(email,password))
    jml = cursorSignIn.rowcount

    dataUser = []
    for row in cursorSignIn.fetchall():
        dataUser.append(dict(row))

    con.commit()

    if jml > 0:
        id = (dataUser[0]['id'])

        payload = {"id": id}
        enkrip = jwt.encode(payload, skey, algorithm='HS256').decode('utf-8')

        b = ({"token": str(enkrip)})
        dataUser[0].update(b)

        return jsonify(dataUser), 200
    else:
        "Gagal", 400

@app.route('/addtweet', methods=['POST','GET'])
def addTweet():

    token = request.form['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']
    tweet = request.form['tweet']
    tgl = request.form['tgl']

    if 'file' not in request.files:
        curInsertTweet = con.cursor()
        curInsertTweet.execute("rollback")
        curInsertTweet.execute("Insert into tweet (id_user,tweet,media_image,media_video,tgl) values (%s,%s,%s,%s,%s)",(idUser,tweet,'none','none',tgl))
        con.commit()

        return redirect('http://localhost:8000/index.html')

    else:
        file = request.files['file']
        if file.filename == '':
            filename = 'none'
        else:
            if file and allowed_file(file.filename):

                filename = secure_filename(file.filename)
                eks = (filename.rsplit('.', 1)[1].lower())

                tglfilter = datetime.datetime.now().strftime("%d %Y")
                tglfile = datetime.datetime.now().strftime("%Y%d")

                cekJmlTweet = con.cursor()
                cekJmlTweet.execute("Select * from tweet where id_user=%s and tgl like %s",(idUser,'%'+tglfilter+'%'))
                jml = cekJmlTweet.rowcount
                con.commit()

                tglwithcounter = tglfile+str(jml)

                if eks == "mp4" or eks == "mkv":
                    mediaImg = "none"
                    mediaVid = 'mv_'+str(idUser)+'_'+tglwithcounter+'.'+eks
                    nmFile = mediaVid
                else:
                    mediaVid = "none"
                    mediaImg = 'mi_'+str(idUser)+'_'+tglwithcounter+'.'+eks
                    nmFile = mediaImg

                file.save(os.path.join('E:\Praktek\python\\front1\image\media',nmFile))

                curInsertTweet = con.cursor()
                curInsertTweet.execute("rollback")
                curInsertTweet.execute("Insert into tweet (id_user,tweet,media_image,media_video,tgl) values (%s,%s,%s,%s,%s)",(idUser,tweet,mediaImg,mediaVid,tgl))
                con.commit()

                return redirect('http://localhost:8000/index.html')

@app.route('/readTweetHome', methods=['POST'])
def readTweet():

    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']

    curgetTweet = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curgetTweet.execute("Select * from gethomeuser(%s)",(idUser,))

    tweets = []
    keytoken = []
    for row in curgetTweet.fetchall():
        id = row[0]
        payload = {"id": id}
        enkrip = jwt.encode(payload, skey, algorithm='HS256').decode('utf-8')

        keytoken.append(enkrip)
        tweets.append(dict(row))

    for idx,tkn in enumerate(keytoken):
        tweets[int(idx)].update({"token":str(tkn)})

    con.commit()
    return jsonify(tweets), 200

@app.route('/readTweetProfile', methods=['POST'])
def readTweetProfile():

    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']
    
    curgetTweet = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curgetTweet.execute("Select * from gettweetuser(%s)",(idUser,))

    tweets = []
    keytoken = []
    for row in curgetTweet.fetchall():
        id = row[0]
        payload = {"id": id}
        enkrip = jwt.encode(payload, skey, algorithm='HS256').decode('utf-8')

        keytoken.append(enkrip)
        tweets.append(dict(row))

    for idx,tkn in enumerate(keytoken):
        tweets[int(idx)].update({"token":str(tkn)})

    con.commit()
    return jsonify(tweets), 200

@app.route('/readMediaUser', methods=['POST'])
def readMediaUser():
    
    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']

    curMediaUser = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curMediaUser.execute("Select * from tweet where media_image != 'none' and id_user=%s or media_video != 'none' and id_user=%s",(idUser,idUser))

    dataMedia = []
    for row in curMediaUser.fetchall():
        dataMedia.append(dict(row))

    return jsonify(dataMedia), 200

@app.route('/readUser', methods=['POST'])
def readUser():

    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']

    curgetUser = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curgetUser.execute("Select * from users where id != %s and id not in (select following from follow where id_user=%s)",(idUser,idUser))

    user = []
    for row in curgetUser.fetchall():
        user.append(dict(row))

    con.commit()
    return jsonify(user), 200

@app.route('/readSearch', methods=['POST'])
def readSearch():
    cari = request.json['cari']

    curCari = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curCari.execute("Select * from users where fullname like %s or username like %s",('%'+cari+'%','%'+cari+'%'))

    dataCari = []
    keyToken = []
    for row in curCari.fetchall():
        payload = {"id": row[0]}
        enkrip = jwt.encode(payload, skey, algorithm='HS256').decode('utf-8')

        keyToken.append(enkrip)
        dataCari.append(dict(row))

    con.commit()
    for idx,tkn in enumerate(keyToken):
        dataCari[int(idx)].update({"token":str(tkn)})

    return jsonify(dataCari), 200

@app.route('/getUser', methods=['POST'])
def getUser():
    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']

    curgetUser = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curgetUser.execute("Select * from users where id=%s ;", (int(idUser),))

    data = []
    for row in curgetUser.fetchall():
        data.append(dict(row))
    
    con.commit()
    id = (data[0]['id'])

    payload = {"id": id}
    enkrip = jwt.encode(payload, skey, algorithm='HS256').decode('utf-8')

    b = ({"token": str(enkrip)})
    data[0].update(b)    
    return jsonify(data), 200

@app.route('/listFollowing', methods=['POST'])
def listFollowing():
    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']
    
    curListFollowing = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curListFollowing.execute("Select * from users inner join follow on users.id=follow.following where follow.id_user=%s",(idUser,))

    listFwing = []
    keytoken = []
    for row in curListFollowing.fetchall():
        id = row[0]
        payload = {"id": id}
        enkrip = jwt.encode(payload, skey, algorithm='HS256').decode('utf-8')

        keytoken.append(enkrip)
        listFwing.append(dict(row))

    for idx,tkn in enumerate(keytoken):
        listFwing[int(idx)].update({"token":str(tkn)})

    con.commit()
    return jsonify(listFwing), 200

@app.route('/listFollowers', methods=['POST'])
def listFollowers():
    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']
    
    curListFollowing = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curListFollowing.execute("select * from users inner join follow on users.id=follow.id_user where follow.following=%s",(idUser,))

    listFwing = []
    keytoken = []
    for row in curListFollowing.fetchall():
        id = row[0]
        payload = {"id": id}
        enkrip = jwt.encode(payload, skey, algorithm='HS256').decode('utf-8')

        keytoken.append(enkrip)
        listFwing.append(dict(row))

    for idx,tkn in enumerate(keytoken):
        listFwing[int(idx)].update({"token":str(tkn)})

    con.commit()
    return jsonify(listFwing), 200

@app.route('/delTweet', methods=['POST'])
def delTweet():

    idTweet = request.json['idtweet']

    curDelFile = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curDelFile.execute("Select * from tweet where id=%s",(idTweet,))

    for data in curDelFile.fetchall():
        if data[3] != "none":
            nFile = 'E:\Praktek\python\\front1\image\media\\'+data[3]
        elif data[4] != "none":
            nFile = 'E:\Praktek\python\\front1\image\media\\'+data[4]
        else:
            nFile = 'E:\Praktek\python\\front1\image\media\kosong.jpg'

    if (os.path.exists(nFile)):
        os.remove(nFile)

    curDelTweet = con.cursor()
    curDelTweet.execute("Delete from tweet where id=%s",(idTweet,))

    con.commit()
    return "Sukses Delete", 200

@app.route('/ubahTweet', methods=['POST'])
def ubahTweet():

    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']

    tweetlama = request.json['tweet']
    tweetbaru = request.json['tweetbaru']

    curEditTweet = con.cursor()
    curEditTweet.execute("Update tweet set tweet=%s where id_user=%s and tweet=%s",(tweetbaru,idUser,tweetlama))

    con.commit()
    return "Sukses Edit", 200

@app.route('/ubahProfile', methods=['POST','GET'])
def getFile():
    if request.method == 'POST':
        print(request.form)
        if 'file' not in request.files:
            print('No file part')
            return "No file part"
            # return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            print('No selected file')
            return "No selected file"
            # return redirect(request.url)

        if file and allowed_file(file.filename):
            token = request.form['token']
            decod = jwt.decode(token, skey, algorithms=['HS256'])
            idUser = decod['id']

            filename = secure_filename(file.filename)
            ekstensi = filename.rsplit('.', 1)[1].lower()

            nmProfile = str(idUser)+'.'+ekstensi
            file.save(os.path.join('E:\Praktek\python\\front1\image\profile', nmProfile))
            
            curProfile = con.cursor()
            curProfile.execute("Update users set photoprofile=%s where id=%s",(nmProfile,idUser))
            con.commit()

            return redirect("http://localhost:8000/index.html")
    else:
        return "Method Not Allowed"

@app.route('/addfollow', methods=['POST'])
def addFollow():

    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']
    following = request.json['following']

    curFollow = con.cursor()
    curFollow.execute("Insert into follow (id_user, following) values (%s,%s)",(idUser, following))

    con.commit()
    return "Sukses Follow", 200

@app.route('/cancelfollow', methods=['POST'])
def batalFollow():
    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']
    following = request.json['following']

    curFollow = con.cursor()
    curFollow.execute("rollback")
    curFollow.execute("delete from follow where id_user=%s and following=%s",(idUser, following))

    con.commit()
    return "Batalkan Follow", 200

@app.route('/getCountFollow', methods=['POST'])
def getFollow():

    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']

    curFollows = con.cursor()
    curFollows.execute("rollback")
    curFollows.execute("select * from follow where id_user=%s", (idUser,))
    jmlFollows = curFollows.rowcount
    con.commit()

    curFollowed = con.cursor()
    curFollowed.execute("rollback")
    curFollowed.execute("select * from follow where following=%s", (idUser,))
    jmlFollowed = curFollowed.rowcount
    con.commit()

    nilai = {
        "jmlFollows": jmlFollows,
        "jmlFollowed": jmlFollowed
    }

    return jsonify(nilai), 200

@app.route('/cekBtnUser', methods=['POST'])
def cekBtnUser():
    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']

    mytoken = request.json['mytoken']
    mydecod = jwt.decode(mytoken, skey, algorithms=['HS256'])
    myId = mydecod['id']

    curCekBtn = con.cursor()
    curCekBtn.execute("select * from follow where following=%s and id_user=%s",(idUser,myId))
    jmlCek = curCekBtn.rowcount

    if jmlCek > 0:
        return "Teman", 200
    else:
        return "Asing", 200


@app.route('/ubahAkun', methods=['POST'])
def ubahAkun():

    token = request.json['token']
    decod = jwt.decode(token, skey, algorithms=['HS256'])
    idUser = decod['id']
    
    username = request.json['username']
    fullname = request.json['fullname']
    email = request.json['email']
    bio = request.json['bio']

    curUbahAkun = con.cursor()
    curUbahAkun.execute("Update users set username=%s, fullname=%s, email=%s, bio=%s where id=%s",(username,fullname,email,bio,idUser))
    con.commit()

    return "Sukses Ubah Akun", 200

@app.route('/ubahPassword', methods=['POST'])
def ubahPassword():

    idUser = request.json['token']
    passCurr = request.json['current_pass']
    passNew = request.json['new_pass']
    passVer = request.json['ver_pass']

    cekPass = con.cursor()
    cekPass.execute("Select * from users where id=%s and password=%s",(idUser,passCurr))
    jml = cekPass.rowcount

    if (jml > 1):
        curUbahAkun = con.cursor()
        curUbahAkun.execute("Update users set password=%s where id=%s and password=%s",(passNew,idUser,passCurr))
        con.commit()
        return "Sukses Ubah Akun", 200
    else:
        return "Password Not Found", 400


if __name__ == "__main__":
    app.run(debug=os.getenv('DEBUG'),host=os.getenv('HOST'),port=os.getenv('PORT'))