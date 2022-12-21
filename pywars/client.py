import requests
import json
import pickle
import codecs
import zipfile
import pathlib
import tempfile
import sys
import datetime
import getpass
import json
import re

from io import BytesIO
from rich.console import Console
from rich.table import Table 

if sys.version_info.major==2:
    input = raw_input


class Client(object):
    def __init__(self,url=None):
        self.server = url 
        self.browser = requests.session()
        self.browser.headers['User-Agent']='sanspywarsgpyc 5.0'
        self.names = []
        self.loggedin = False
        self.hold_username = None
        self.hold_password = None
        self.print_rich_text = True
        self.show_all_scores = False
        self.show_answer_warnings = True
        self.console = Console()
        self.file_location = pathlib.Path().home() / "Desktop"
        self.default_profile = pathlib.Path().home() / ".pywars/default.config"
        #If they didn't specify a URL then try to load a profile
        if self.default_profile.is_file() and self.server == None:
            try:
                with self.default_profile.open("rt") as fp:
                    config = json.load(fp)
                self.profile = config.get("profile")
                self.server = self.server or config.get("host", None)
                self.config_file = pathlib.Path().home() / f".pywars/{self.profile}"
                if self.config_file.is_file():
                    self.load_profile()
                else:
                    print("No config loaded.")
            except Exception as e:
                print(f"An error occured loading the config. {str(e)}.")
        else:
            self.profile = "profile1.config"
            self.config_file = pathlib.Path().home() / f".pywars/{self.profile}"

    def select_profile(self,profile_name=None):
        """This method is used to select which client setting to use by default"""
        #Load the list of Profiles
        profile_list = list((pathlib.Path().home() / ".pywars").glob("*.config"))
        current_default = json.loads(self.default_profile.read_text()).get("profile",None)
        profile_list = [x for x in profile_list if x.stem != "default"]
        ptable = Table("#","Server","Username","Current Default")
        for pos, each_profile in enumerate(profile_list):
            config_info = json.loads(each_profile.read_text())
            current = "Y" if each_profile.name == current_default else "N"
            ptable.add_row(str(pos), config_info['server'], config_info['hold_username'], current )
        #Select one 
        while profile_name == None:
            self.console.print(ptable)
            try:
                profile_num = int(input("Which profile number would you like to load?"))
                profile_name = profile_list[profile_num].name
            except:
                print("That is an invalid profile number")
                pass
        #set as Default
        dconfig = {"profile":f"{profile_name}","host":self.server }
        self.default_profile.write_text(json.dumps(dconfig))
        self.profile = profile_name
        #Load it
        self.config_file = pathlib.Path().home() / f".pywars/{profile_name}"
        self.load_profile()


    def load_profile(self):
        """This method will load the current configuration file."""
        if not self.config_file.is_file():
            print("No Configuration file found.")
            self.save_profile()
        else:
            try:
                with self.config_file.open("rt") as fp:
                    config = json.load(fp)
            except Exception as e:
                print(f"An error occured loading the config. {str(e)}.")
            else:
                vars(self).update(config)

    def save_profile(self, no_new_profile=False):
        """This profile saves the current settings to a profile. If the login info changed it creates a new profile unless the no_new_profile argument is True."""
        #Load the current config for comparison to check for changes
        current_config = {}
        try:
            current_config = json.loads(self.config_file.read_text())
        except Exception as e:
            #no saved config
            no_new_profile = True

        #If in memory username/pw are different create a new profile unless no_new_profile is set
        if (no_new_profile == False) and \
           ((current_config.get("server") != self.server) or \
           (current_config.get("hold_username") != self.hold_username) or \
           (current_config.get("hold_password") != self.hold_password)):

           profile_number = re.search(r"\d+$", self.config_file.stem).group()
           new_number = int(profile_number) + 1
           self.profile = f"profile{new_number}.config"
           self.config_file = pathlib.Path().home() / f".pywars/{self.profile}"
        #Make sure .pywars folder exists
        self.config_file.parent.mkdir(exist_ok=True)

        #set the default profile to be the current profile
        dconfig = {"profile":f"{self.profile}","host":self.server }
        self.default_profile.write_text(json.dumps(dconfig))

        #save the current object to the current profile name   
        config = dict(vars(self))
        del config['names']
        del config['browser']
        del config['config_file']
        del config['file_location']
        del config['profile']
        del config['default_profile']
        del config['console']
        with self.config_file.open("wt") as fp:
            json.dump(config, fp)

    def new_acct(self,uname=None, password=None, reg_code=None):
        """Use this method to create an account.  It takes three arguments, a username, a password and a registration code."""
        url = f"{self.server}/usernew/"
        if not uname:
            uname = input("Enter your username (usually your SANS email): ")
        if not password:
            password = getpass.getpass("Type a password for your new account: ")
        if not reg_code:
            reg_code = input("Enter the registration code provided by the instructor")
        resp = self.__post_json(url, {'user':uname,'password':password,"reg_code":reg_code} )
        result = resp.get("text","Account Registration Failed")
        if result == "Success":
            self.hold_username = uname
            self.hold_password = password
            self.save_profile()
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
            self.save_profile()
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
            return
        position = 1
        score_table = Table("Rank","Name","Score","Last Scored","Completed", title="Scoreboard", show_lines=True)
        for name,score_tuple in sorted(sb.items(), key=lambda x:(x[1][0],_time_elapsed(x[1][2])), reverse=True):
            score,complete,lastscore = score_tuple
            lsd = datetime.datetime.strptime(lastscore, "%a, %d %b %Y %H:%M:%S %Z")
            lsd = lsd.replace(tzinfo=datetime.timezone.utc).astimezone()
            date_hour = datetime.datetime.strftime(lsd, "%b,%d %H:%M:%S")
            finished = _collapse_points(complete)
            score_table.add_row(f"{position:0>3}",f"{name}", f"{score:0>3}", f"{date_hour}", f"{finished}")
            if not self.print_rich_text:
                print(f"{position:0>3}-{name[:15]: ^15} Points:{score:0>3}   Scored:{date_hour}   Completed:{finished}")
            position += 1
        if self.print_rich_text:
            self.console.print(score_table)
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
        q_attach = resp.get("has_attachment",False)
        if q_attach:
            self.attachment(qnum)
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
            self.console.print(qtable)
            self.console.print("TEXT:\n{}".format(qtxt))
        return None

    def attachment(self, qnum, overwrite=None):
        """This method given a question name or number will retreive an attachment."""
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
        if tgt_path.exists() and overwrite==None:
            self.console.print("[bold red]Folder download skipped because the folder already exists. Call .attachment('labname',overwrite=True) to redownload and overwrite the exiting folder.[/bold red]") 
            return False
        url = f"{self.server}/attachment/{qnum}"
        resp = self.browser.get(url).json()
        attachment = codecs.decode(resp.get("blob").encode(),"base64")
        with tgt_path as write_zip:
            with zipfile.ZipFile(BytesIO(attachment),"r") as zip_ref:
                zip_ref.extractall(write_zip)
        return f"Zip extracted to {str(tgt_path)}"


    def data(self,qnum):
        """This method given a question name or number will return the data for the question. Optionally set overwrite to control whether existing folders are overwritten. Only all caps YES will cause it to overwrite. Any version of 'no' will return the data to you instead of overwriting the folder if the folder already exists."""
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
        json_blob = self.browser.get(url).json()
        if not "blob" in json_blob:
            if self.print_rich_text:
                self.console.print("[red on bright_yellow] {} ".format(json_blob.get("text","UNABLE TO RETREIVE DATA")))
            else:
                print("*** {} ***".format(json_blob.get("text", "UNABLE TO RETRIEVE DATA" )))
            return None
        data_blob = json_blob.get("blob").encode()
        data_var = pickle.loads(codecs.decode(data_blob,"base64"))
        #Remove these two lines for data to just be data and not a zip.
        if isinstance(data_var,bytes) and data_var.startswith(b"PK"):
            with tgt_path as write_zip:
                with zipfile.ZipFile(BytesIO(data_var),"r") as zip_ref:
                    zip_ref.extractall(write_zip)
            return f"Zip extracted to {str(tgt_path)}"
        return data_var


    def answer(self,answer,notanswer=None):
        """This method takes one argument which should be the answer to the data object you queried last."""
        if notanswer:
            if self.show_answer_warnings:
                self.console.print("[red] Note: In this version .answer() does not require the question number. Only the answer.")
                self.console.print(f"I fixed it for you this time and submitted .answer({notanswer})")
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
            self.console.print(resp.get('text'))
        if resp.get("blob"):
            results = codecs.decode(resp.get("blob").encode(), "base64")
            self.console.print(results.decode())
        return
    
    def __post_json(self,url, dict):
        """Internal Only - Posts to the website and process the response. """
        try:
            data = json.dumps(dict)
        except Exception as e:
            print("Improperly Formatted Data")
            return {}
        try:
            resp = self.browser.post(url,data)
        except Exception as e:
            print("An error occured connecting to pyWars. Please check your internet connection and try again.\n\n",str(e))
            return {}
        if resp.status_code != 200:
            print(f"Bad Request. Pywars responded {resp.status_code}")
            return {}
        return resp.json()

def _time_elapsed(timestr):
    as_dt = datetime.datetime.strptime(timestr, "%a, %d %b %Y %H:%M:%S %Z")
    return (datetime.datetime.now() - as_dt).total_seconds()

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
