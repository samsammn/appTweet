# Tweet aweetan

Aplikasi ini hanya dibuat sederhana dengan python yang menggunakan sistem file untuk penyimpanannya. Silahkan kembangkan lagi aplikasi sederhana ini, karena aplikasi ini hanya tugas dan latihan dalam belajar backend dengan python.

Untuk selanjutnya mungkin bisa membuat sebuah tweeter yang dibuat dengan frontend nya juga, dan mamakai database untuk penyimpanannya.

# Fitur :
* Create
* Read
* Update
* Delete

# Sistem File
* Membaca dan memindahkan kedalam variabel
```python
with open(os.getcwd()+'/userData.txt') as dataUser:
    User = json.load(dataUser)

with open(os.getcwd()+'/tweetData.txt') as dataTweet:
    Tweets = json.load(dataTweet)
```

* Untuk mengupdate / menambahkan data ke file
```python
def tambahUser():
    with open(os.getcwd()+'/userData.txt','w') as isiData:
        json.dump(User,isiData,indent=4)

def tambahTweet():
    with open(os.getcwd()+'/tweetData.txt','w') as isiData:
        json.dump(Tweets,isiData,indent=4)
```

# Validasi Input

* Untuk mengecek keberadaan email
```python
def checkEmailExists(email,check):
    if check == True:
        for data in User:
            if data["email"] == email:
                abort(400, "Email sudah digunakan")

        return email
    elif check == False:
        for data in User:
            if data["email"] == email:
                return email

        abort(400, "Email tidak ditemukan")
```

* Validasi yang mengharuskan mengisi kolom yang ditentukan
```python
def isRequired(field):
    parser = reqparse.RequestParser()
    for kolom in field:
        parser.add_argument(kolom,required = True, location = ["json"], help = "Kolom "+kolom+" tidak ditemukan")
    return parser.parse_args()
```
# Class-class untuk melakukan CRUD
## SignUp
Sebelum melakukan login ke tweet, kita buat dulu class untuk menambahkan akun kedalam file, atau daftar akun agar bisa melakukan login, code nya :
```python
class signUp(Resource):
    def post(self):
        #validasi kolom dlu
        isRequired(["username","email","password","fullname"])

        #cek email dulu bro
        checkEmailExists(request.json["email"],True)

        req = request.json
        req.update({"tweet":[]})

        User.append(req)
        tambahUser()

        Tweets[request.json["email"]] = []
        tambahTweet()
        return "Daftar Berhasil!", 201    
```

## SignIn
Setelah kita mempunyai akun kita harus login, dan login tersebut menggunakan email dan password. kemudian kita akan mengecek apakah email dan password yang kita masukan benar atau tidak, dengan memanggil fungsi cek email yang sudah disiapkan diatas. Code untuk signin nya :
```python
class signIn(Resource):
    def post(self):
        isRequired(["email","password"])
        
        email = request.json["email"]
        password = request.json["password"]

        for login in User:
            if login["email"] == email and login["password"] == password:
                login["tweet"] = Tweets[login["email"]]

                return login

        return "Email atau Password salah!", 401
```

## Add Tweet
Untuk menambahkan data sebagai status/tweet baru.
```python
class Tweet(Resource):
    def post(self):
        #validasi kolom dulu
        isRequired(["email","tweet"])

        #check email dlu bro
        checkEmailExists(request.json["email"],False)
        Tweets[request.json["email"]].append(request.json["tweet"])
        tambahTweet()

        return "Tweet Berhasil", 201
```

## Delete Tweet
Menghapus tweet yang sudah ada, kita harus menginputkan email dan tweet yang telah kita masukan sebelumnya.

```ptyhon
class delTweet(Resource):
    def post(self):
        email = request.json["email"]
        tweet = request.json["tweet"]

        checkEmailExists(request.json["email"],False)
        for keyEmail in Tweets:
            if keyEmail == email:
                for index,tw in enumerate(Tweets[keyEmail]):
                    if tw == tweet:
                        # print('a')
                        del Tweets[keyEmail][index]
                        tambahTweet()
                        return "Tweet berhasil dihapus!",200
                
                return "Tweet '"+tweet+"' tidak ditemukan!", 400
```

## Inisialisasi API dan Setting Route/Endpoint

```python
user_api = Blueprint('users',__name__)
api = Api(user_api)

api.add_resource(signUp,'/signUp')
api.add_resource(signIn,'/signIn')
api.add_resource(Tweet,'/tweet')
api.add_resource(delTweet,'/deltweet')
```