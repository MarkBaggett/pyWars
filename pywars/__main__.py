import os
import pathlib
import socket
import code
import argparse
import re
import getpass
import json
import sys
import atexit
import time

if os.name != "nt":
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

def new_profile(client):
    client.default_profile.parent.mkdir(exist_ok=True)
    client.server = get_hostname()
    dconfig = {"profile":"profile1.config","host":client.server }
    client.default_profile.write_text(json.dumps(dconfig))
    client.hold_username = get_username()
    client.hold_password = get_password()
    client.profile = "profile1.config"
    client.config_file = pathlib.Path().home() / f".pywars/{client.profile}"
    account_exists = client.login()
    while account_exists != 'Login Success':
        print("The password is incorrect or the account does not exist. Type 'no' to try another username and password. ")
        create = input("In person students should type 'yes' if the instructor has given you a registration code : ").lower()
        if create.startswith("y"):
            reg_code = input("What is the registration code provided by the instructor? ")
            print(client.new_acct(client.hold_username, client.hold_password, reg_code))
        else:
            client.hold_username = get_username()
            client.hold_password = get_password()
        time.sleep(1)
        account_exists = client.login()


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
    client = Client()
    if not client.default_profile.is_file() or args.new:
        new_profile(client)
    elif args.switch:
        client.select_profile()
    elif args.reset:
        prof_folder = pathlib.Path().home() / ".pywars"
        for eachfile in prof_folder.glob("*.config"):
            eachfile.unlink()
        print("Profiles reset.")
        sys.exit(0)
        
    #Create a client and interact
    
    try:
        client.login()
    except Exception as e:
        print("An error occurred connecing to pywars. Please check your network configuration.\n\n", str(e))
    else:
        if os.name != "nt":   
            with (pathlib.Path().home() / ".python_history") as history_path:
                readline.read_history_file(history_path)                                                    
            readline.set_completer(rlcompleter.Completer(locals()).complete)
            readline.parse_and_bind("tab: complete")
            atexit.register(save_history)
        d = client
        code.interact("Welcome to pywars!",local=locals())

if __name__=="__main__":
    main()
