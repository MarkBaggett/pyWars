import pathlib
import socket
import code
import argparse
import re
import getpass
import json
import sys
import atexit
import rlcompleter
import readline


from pywars.client import Client

def get_hostname():
    while True:
        hostname = input("What is the hostname (example: live.sec573.com) of the server? ")
        if not re.match(r"\w+\.sec[56]73\.com",hostname):
            print("That is not an authorized hostname.")
            continue
        try:
            socket.gethostbyname(hostname)
        except:
            print("That host is not reachable. Check your network connection and confirm the hostname.")
        else:
            break
    return f"https://{hostname}:10000"

def get_username():
    #Get email
    while True:
        username = input("What is registration email address on the SANS Portal? ")
        if len(username) < 4:
            print("Your username must be at least 4 letters.")
        else:
            break
    return username

def get_password():
    #get password
    while True:
        passwd = getpass.getpass("Give me a new pyWars password for this class (keystrokes not displayed): ")
        if len(passwd) < 10 or not( 
            any(map(lambda x:x.islower(),passwd)) and
            any(map(lambda x:x.isupper(),passwd)) and
            any(map(lambda x:x.isdigit(),passwd)) ):
                print("Must be 10 characters with an upper, lower and a digit.")
        else:
            break
    return passwd

def new_profile(pywars_client):
    pywars_client.default_profile.parent.mkdir(exist_ok=True)
    pywars_client.server = get_hostname()
    dconfig = {"profile":"profile1.config","host":pywars_client.server }
    pywars_client.default_profile.write_text(json.dumps(dconfig))
    pywars_client.hold_username = get_username()
    pywars_client.hold_password = get_password()
    pywars_client.profile = "profile1.config"
    pywars_client.config_file = pathlib.Path().home() / f".pywars/{pywars_client.profile}"
    account_exists = pywars_client.login()
    while account_exists != 'Login Success':
        create = input("That account does not exist. Check the password and try again. In Person class student type YES to create it now: ").lower()
        if create == "yes":
            reg_code = input("What is the registration code provided by the intructor? ")
            pywars_client.new_acct(pywars_client.hold_username, pywars_client.hold_password, reg_code)
        else:
            pywars_client.hold_username = get_username()
            pywars_client.hold_password = get_password()
        account_exists = pywars_client.login()


###   
#      pywars_client.default_profile = pathlib.Path().home() / ".pywars/default.config"
        # if not pywars_client.default_profile.is_file():
        #     pywars_client.default_profile.parent.mkdir(exist_ok=True)
        #     pywars_client.server = get_hostname()
        #     dconfig = {"profile":"profile1.config","host":pywars_client.server }
        #     pywars_client.default_profile.write_text(json.dumps(dconfig))
        #     pywars_client.profile = "profile1.config"
        #     pywars_client.hold_username = get_username()
        #     pywars_client.hold_password = get_password()
        #     pywars_client.config_file = pathlib.Path().home() / f".pywars/{pywars_client.profile}"
        # else:
        #     try:
        #         with pywars_client.default_profile.open("rt") as fp:
        #             config = json.load(fp)
        #         pywars_client.profile = config.get("profile")
        #         pywars_client.server = pywars_client.server or config.get("host", None)
        #         pywars_client.config_file = pathlib.Path().home() / f".pywars/{pywars_client.profile}"
        #         if pywars_client.config_file.is_file():
        #             pywars_client.load_profile()
        #         else:
        #             print("No config loaded.")
        #     except Exception as e:
        #         print(f"An error occured loading the config. {str(e)}.")

def save_history():
    with (pathlib.Path().home() / ".python_history") as history_path:
        readline.write_history_file(history_path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('-n','--new',action='store_true',required=False,help='Create a new connection profile')
    parser.add_argument('-s','--switch',action='store_true',required=False,help='Select an existing connection profile.')
    parser.add_argument('-r','--reset',action='store_true',required=False,help='Erase all profiles and start over.')
    
    args=parser.parse_args()

    #Ondemand already has username and password
    #Ctf already has username and password
    #Live students need to register
    pywars_client = Client()
    if not pywars_client.default_profile.is_file() or args.new:
        new_profile(pywars_client)
    elif args.switch:
        pywars_client.select_profile()
    elif args.reset:
        prof_folder = pathlib.Path().home() / ".pywars"
        for eachfile in prof_folder.glob("*.config"):
            eachfile.unlink()
        print("Profiles reset.")
        sys.exit(0)
        
    #Create a client and interact
    
    try:
        pywars_client.login()
    except Exception as e:
        print("An error occurred connecing to pywars. Please check your network configuration.\n\n", str(e))
    else:
        d = pywars_client
        with (pathlib.Path().home() / ".python_history") as history_path:
            readline.read_history_file(history_path)                                                    
        readline.set_completer(rlcompleter.Completer(locals()).complete)
        readline.parse_and_bind("tab: complete")
        atexit.register(save_history)
        code.interact(local=locals())