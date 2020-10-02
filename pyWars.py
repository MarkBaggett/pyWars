import requests
import json
import pickle
import codecs
import zipfile
import pathlib
import tempfile
import sys
from io import BytesIO

if sys.version_info.major==2:
    input = raw_input

class exercise(object):
    def __init__(self,url=None):
        if not url:
            self.server = "http://127.0.0.1:10000"
        else:
            self.server = url
        self.browser = requests.session()
        self.browser.headers['User-Agent']='sanspywarsgpyc 4.0'
        self.names = []
        self.hold_username = None
        self.hold_password = None
        self.loggedin = False
        self.file_location = pathlib.Path().home() / "Desktop"
        
    def new_acct(self,uname,password,reg_code):
        """Use this method to create an account.  It takes three arguments, a username, a password and a registration code."""
        url = f"{self.server}/usernew/"
        resp = self.post_json(url, {'user':uname,'password':password,"reg_code":reg_code} )
        return resp.get("text")

    def login(self,uname = None,password = None):
        """Use this method to login. It requires two arguments, a username and password."""
        if not uname:
            uname = self.hold_username
        if not password:
            password = self.hold_password
        if not uname or not password:
            return "Username and Password are required."
        url = f"{self.server}/userlogin/"
        resp = self.post_json(url,{'user':uname,'password':password})
        login = resp.get("text")
        if login == "Login Success":
            self.hold_username = uname
            self.hold_password = password
            self.names = resp.get("question_names")
            self.loggedin = True
            return "Login Success"
        else:
            return login

    def logout(self):
        """Use this method to logout your account."""
        url = f"{self.server}/userlogout/"
        self.names = []
        self.loggedin = False
        resp = self.browser.get(url).json()
        return resp.get("text")

    def score(self,show_all=False):
        """This method will print your score.  If you pass True as the first argument it shows all scores."""
        if not self.loggedin:
            return "Please login first"
        url = f"{self.server}/score/"
        resp = self.post_json(url, {'show_all':show_all} )
        sb = resp.get("text",{})
        if not isinstance(sb,dict):
            print(sb)
        for name,score_tuple in sorted(sb.items(), key=lambda x:x[1][0], reverse=True):
            score,complete,lastscore = score_tuple
            print(f"{name[:15]: ^15}-Points:{score:0>3} Scored:{lastscore[5:-4]} Completed:{collapse_points(complete)}")
        return None

    def question(self,qnum):
        """This method given a question name or number will return the question text."""
        if not self.loggedin:
            return "Please login first"
        if isinstance(qnum, str):
            qnum = self.name2num(qnum)
            if qnum == -1:
                return "Invalid Question Name"
        elif not isinstance(qnum,int):
            return "Invalid Question Number"
        url = f"{self.server}/question/{qnum}"
        resp = self.browser.get(url).json()
        qtxt = resp.get("text")
        if "timeout" in resp:
            print("Question: {} - {}".format(qnum, self.names[qnum]))
            print("Points  : {}".format(resp.get("points") ))
            print("Timeout : {}".format(resp.get("timeout") or "Not Timed"))
            print("Attempts: {}".format(resp.get("tries") or "UNLIMITED"))
            print("PREREQ  : {}".format(resp.get("prereq") or "NONE"))
            print("TEXT    :\n\n{}".format(qtxt))
        else:
            return qtxt

    def data(self,qnum, store=False):
        """This method given a question name or number will return the data for the question.  If you also pass True it will assume the data is a zip, write it to your desktop and unzip it."""
        if not self.loggedin:
            return "Please login first"
        if isinstance(qnum, str):
            new_folder = qnum
            qnum = self.name2num(qnum)
            if qnum < 0:
                return "Invalid Question Name"
        elif not isinstance(qnum,int):
            return "Invalid Question Number"
        else:
            new_folder = f"data{qnum}"
        tgt_path = pathlib.Path(self.file_location) / new_folder            
        url = f"{self.server}/data/{qnum}"
        data_blob = self.browser.get(url).json().get("blob").encode()
        data_var = pickle.loads(codecs.decode(data_blob,"base64"))
        if store and tgt_path.exists():
            overwrite = input("The path already exists. Do you want to over write the current directory,\"yes\" or \"no\"? ").lower()
            if overwrite != "yes":
                print("Data ignored. The original directory was not changed.")
        elif store:
            if (not isinstance(data_var,bytes)) or (not data_var.startswith(b"PK")):
                print("Data does not appear to be a zip file. Storage skipped.")
            else:             
                with tgt_path as write_zip:
                    with zipfile.ZipFile(BytesIO(data_var),"r") as zip_ref:
                        zip_ref.extractall(write_zip)
                data_var = f"Zip extracted to {str(tgt_path)}"
        return data_var

    def answer(self,answer,notanswer=None):
        """This method takes one argument which should be the answer to the data object you queried last."""
        if notanswer:
            print("Note: In this version .answer() does not require the question number. Only the answer.")
            print(f"I fixed it for you this time and submitted .answer({notanswer})")
            answer = notanswer
        if not self.loggedin:
            return "Please login first"
        url = f"{self.server}/answer/"
        resp = self.post_json(url, {'answer':str(answer).strip()})
        return resp.get("text")

    def password(self,current_password,new_password):
        """This changes your password. Provide the current password and the new password."""
        if not self.loggedin:
            return "Please login first.  If you dont know your password contact SANS or your instructor to reset it."
        url = f"{self.server}/userpassword/"
        resp = self.post_json(url, {'currentpass':current_password,"newpass":new_password})
        return resp.get("text")

    def name2num(self,name):
        """The DNS of pywars questions. Given a question name returns the question number"""
        if name.lower() in self.names:
            return self.names.index(name.lower())
        else:
            return -1

    def solution(self, source_code):
        """This method takes your source code and submits it to the server for review. It should be single file or a directory."""
        if not self.loggedin:
            return "Please login first"
        if not isinstance(source_code,str):
            return "This method is expecting a path to a file or directory."
        src_path = pathlib.Path(source_code)
        src_path = src_path.expanduser().resolve(strict=True)
        if src_path.is_dir():
            file_list = src_path.rglob('*')
        elif src_path.is_file():
            file_list = [src_path]
            src_path = src_path.parent
        else:
            return "This method is expecting a path to a file or directory."
        with tempfile.TemporaryFile() as tmpfile:
            with zipfile.ZipFile(tmpfile, 'w', zipfile.ZIP_DEFLATED) as newfile:
                for file in file_list:
                    newfile.write(file, file.relative_to(src_path))
            tmpfile.flush()
            tmpfile.seek(0)
            data = tmpfile.read()
        data = codecs.encode(data, "base64").decode()
        url = f"{self.server}/unittest/"
        resp = self.post_json(url,{'code':data.strip()})
        if resp.get("text"):
            print(resp.get('text'))
        if resp.get("blob"):
            results = codecs.decode(resp.get("blob").encode(), "base64")
            print(results.decode())
        return
    
    def post_json(self,url, dict):
        """Internal Only - Posts to the website and process the response. """
        try:
            data = json.dumps(dict)
        except Exception as e:
            print("Improperly Formatted Data")
            return {}
        resp = self.browser.post(url,data)
        if resp.status_code != 200:
            print(f"Bad Reqeust. Pywars responded {resp.status_code}")
            return {}
        return resp.json()

def collapse_points(lon):
    """Internal Only-Make scoreboard look nice"""
    lon.sort()
    lon.append(-999999999999999999999999)
    inrange = False
    result = []
    for pos,eachnum in enumerate(lon[:-1]):
        if (not inrange) and (eachnum == lon[pos+1]-1):
            inrange = True
            result.append(str(eachnum)+"-" ) 
        elif not eachnum == lon[pos+1]-1:
            inrange = False
            result.append(str(eachnum))
    answer = ""
    for eachval in result:
        if eachval[-1] == "-":
            answer += eachval
        else:
            answer += eachval+","
    return answer[:-1]