import requests
import json
import pickle
import codecs
import zipfile
import pathlib
import tempfile
import sys
import datetime
from io import BytesIO
from rich.console import Console
from rich.table import Table 

if sys.version_info.major==2:
    input = raw_input

class exercise(object):
    def __init__(self,url):
        self.server = url
        self.browser = requests.session()
        self.browser.headers['User-Agent']='sanspywarsgpyc 4.0'
        self.names = []
        self.hold_username = None
        self.hold_password = None
        self.loggedin = False
        self.print_rich_text = False
        self.show_all_scores = False
        self.show_answer_warnings = True
        self.file_location = pathlib.Path().home() / "Desktop"
        
    def new_acct(self,uname,password,reg_code):
        """Use this method to create an account.  It takes three arguments, a username, a password and a registration code."""
        url = f"{self.server}/usernew/"
        resp = self.__post_json(url, {'user':uname,'password':password,"reg_code":reg_code} )
        result = resp.get("text","Account Registration Failed")
        if result == "Success":
            self.hold_username = uname
            self.hold_password = password
        return result

    def login(self,uname = None,password = None):
        """Use this method to login. It requires two arguments, a username and password."""
        if not uname:
            uname = self.hold_username
        if not password:
            password = self.hold_password
        if not uname or not password:
            return "Username and Password are required."
        url = f"{self.server}/userlogin/"
        resp = self.__post_json(url,{'user':uname,'password':password})
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
        show_all = show_all or self.show_all_scores
        resp = self.__post_json(url, {'show_all':show_all} )
        sb = resp.get("text",{})
        if not isinstance(sb,dict):
            print(sb)
        position = 1
        score_table = Table("Rank","Name","Score","Last Scored","Completed", title="Scoreboard", show_lines=True)
        for name,score_tuple in sorted(sb.items(), key=lambda x:x[1][0], reverse=True):
            score,complete,lastscore = score_tuple
            lsd = datetime.datetime.strptime(lastscore, "%a, %d %b %Y %H:%M:%S %Z")
            lsd = lsd.replace(tzinfo=datetime.timezone.utc).astimezone()
            date_hour = datetime.datetime.strftime(lsd, "%b,%d %H:%M:%S")
            finished = _collapse_points(complete)
            score_table.add_row(f"{position:0>3}",f"{name}", f"{score:0>3}", f"{date_hour}", f"{finished}")
            if not self.print_rich_text:
                print(f"{position:0>3}-{name[:15]: ^15} Points:{score:0>3}   Scored:{date_hour}   Completed:{finished}")
        if self.print_rich_text:
            the_console.print(score_table)
        return None

    def question(self,qnum,show_detail=False):
        """This method given a question name or number will return the question text."""
        if not self.loggedin:
            return "Please login first"
        if isinstance(qnum, str):
            qnum = self.name2num(qnum)
            if qnum == -1:
                return "Invalid Question Name"
        elif isinstance(qnum,int):
            if not (0 <= qnum < len(self.names)):
                return "Invalid Question Number"
        else:
            return "Question number must be an integer or string"
        show_detail = show_detail or self.print_rich_text
        url = f"{self.server}/question/{qnum}"
        resp = self.browser.get(url).json()
        qtxt = resp.get("text")
        if not ("timeout" in resp) or (not self.print_rich_text):
            print(qtxt)
        else:
            qtable = Table("#","Question","Points","Timeout","Attempts","Prerequisites")
            qtable.add_row(
                    "{}".format(qnum),
                    "{}".format(self.names[qnum]),
                    "{}".format(resp.get("points")),
                    "{}".format(resp.get("timeout") or "Not Timed"),
                    "{}".format(resp.get("tries") or "UNLIMITED"),
                    "{}".format(resp.get("prereq") or "NONE"))
            the_console.print(qtable)
            the_console.print("TEXT:\n{}".format(qtxt))
        return None        

    def data(self,qnum):
        """This method given a question name or number will return the data for the question.  If you also pass True it will assume the data is a zip, write it to your desktop and unzip it."""
        if not self.loggedin:
            return "Please login first"
        if isinstance(qnum, str):
            new_folder = qnum
            qnum = self.name2num(qnum)
            if qnum == -1:
                return "Invalid Question Name"
        elif isinstance(qnum,int):
            new_folder = self.num2name(qnum)
            if new_folder == -1:
                return "Invalid Question Number"
        else:
            return "Question number must be an integer or string"
        tgt_path = pathlib.Path(self.file_location) / new_folder            
        url = f"{self.server}/data/{qnum}"
        data_blob = self.browser.get(url).json().get("blob").encode()
        data_var = pickle.loads(codecs.decode(data_blob,"base64"))
        if isinstance(data_var,bytes) and data_var.startswith(b"PK"):
            write_file = True
            if tgt_path.exists(): 
                write_file = input("The path already exists. Do you want to over write the current directory,\"yes\" or \"no\"? ").lower() == "yes"
            if write_file:             
                with tgt_path as write_zip:
                    with zipfile.ZipFile(BytesIO(data_var),"r") as zip_ref:
                        zip_ref.extractall(write_zip)
                return f"Zip extracted to {str(tgt_path)}"
            else:
                print("You did not type 'yes'. The original directory was not changed.")     
        return data_var

    def answer(self,answer,notanswer=None):
        """This method takes one argument which should be the answer to the data object you queried last."""
        if notanswer:
            if self.show_answer_warnings:
                the_console.print("[red] Note: In this version .answer() does not require the question number. Only the answer.")
                the_console.print(f"I fixed it for you this time and submitted .answer({notanswer})")
            answer = notanswer
        if not self.loggedin:
            return "Please login first"
        url = f"{self.server}/answer/"
        resp = self.__post_json(url, {'answer':str(answer).strip()})
        return resp.get("text")

    def password(self,current_password,new_password):
        """This changes your password. Provide the current password and the new password."""
        if not self.loggedin:
            return "Please login first.  If you dont know your password contact SANS or your instructor to reset it."
        url = f"{self.server}/userpassword/"
        resp = self.__post_json(url, {'currentpass':current_password,"newpass":new_password})
        if resp.get("text","") == "Success":
            self.hold_password = new_password
        return resp.get("text")

    def displayname(self,new_displayname):
        """This changes your display name on the scoreboard."""
        if not self.loggedin:
            return "Please login first"
        url = f"{self.server}/userdisplay/"
        resp = self.__post_json(url, {'displayname':new_displayname})
        return resp.get("text")

    def name2num(self,name):
        """The DNS of pywars questions. Given a question name returns the question number"""
        if name.lower() in self.names:
            return self.names.index(name.lower())
        else:
            return -1

    def num2name(self,qnum):
        """The reverse DNS of pywars questions. Given a question number returns the question name"""
        if 0 <= qnum < len(self.names):
            return self.names[qnum]
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
        resp = self.__post_json(url,{'code':data.strip()})
        if resp.get("text"):
            the_console.print(resp.get('text'))
        if resp.get("blob"):
            results = codecs.decode(resp.get("blob").encode(), "base64")
            the_console.print(results.decode())
        return
    
    def __post_json(self,url, dict):
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

def _collapse_points(lon):
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

the_console = Console()