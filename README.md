This is the the pyWars client used in SEC573 and SEC673.

# Installation
To install the client run the following commands:
```
$ git clone http://github.com/markbaggett/pyWars
$ cd pyWars
$ pip install .
```

# Use
To use the client you must have two pieces of information provided by the SANS Instructor.  You must have the Address of the pyWars server and a registration code.  With those two pieces of information you can create your account as follows:

```
$ import pyWars
>>> d = pyWars.exercise("address provided by instructor")
>>> d.new_acct("Your Chosen Username","Your Chosen Password", "Registration code provide by instructor")
>>> d.login("Your email address","Your Chosen Password")
```

Once your account the account is created and logged in you can use the following methods to interact with the server:
 - ```d.question(<question name or number>)``` - Retrieve and show the question.
 - ```d.data(<question name or number>)``` - Retrieve and show a sample of the data. If True is second argument data is unzipped for you.
 - ```d.answer(<your answer>)``` - Submit the answer for the last data you queried.
 - ```d.solution(<path to your solution script>)``` - Submit your code for review and scoring
 - ```d.score([True])``` - Retrieve and show the scoreboard.  If True is passed it will display all scocres instead of only yours.
 - ```d.displayname(NewDisplayName)``` - Set your displayname on the scoreboard
 - ```d.logout()``` - Log out from your current session.
 - ```d.password(current,new)``` - Change the password for the logged on account from current to new.
 - ```print(d.names)``` - show a list of all loaded challenge names
 - ```d.name2num(<question name>)``` - Lookup a question number from its name.
 - ```d.num2name(<question number>)``` - Lookup a question name from its number.

 The following attributes change the behavior of the pywars methods:
 - ```d.show_all_scores``` - By default only your score is shown on the scoreboard
 - ```d.print_rich_text``` - By default unformated text is rendered to the screen. Enable this if your terminal supportes it. 


 Note: You must know the current password to change it.  The SANS Instructor or SANS Support can reset your password. 



## pywars client V5 - 2023
There is a new pywars client also available for testing. No support is offered for this client during class until its official release. 

### Installation

Install from the @version5 branch
```
student@SEC573:~/Downloads$ python -m venv ~/python-envs/pywars5
student@SEC573:~/Downloads$ source ~/python-envs/pywars5/bin/activate
(pywars5) student@SEC573:~/Downloads$ pip install git+https://github.com/markbaggett/pywars@version5
Collecting git+https://github.com/markbaggett/pywars@version5
  Cloning https://github.com/markbaggett/pywars (to revision version5) to /tmp/pip-req-build-rt07i8zv
  Running command git clone -q https://github.com/markbaggett/pywars /tmp/pip-req-build-rt07i8zv
  Running command git checkout -b version5 --track origin/version5
  Switched to a new branch 'version5'
```

Output truncated.

### Changes to module

I've decided to use PEP-8 compliant names for this next version.  Exercise() is now Client() as it more accuratly describes the purpose.

```
(pw-client) student@SEC573:~/git/pywars$ python
>>> import pywars
>>> d = pywars.Client('https://live.sec573.com:10000')
>>> d.login('mbaggett@sans.org','MyPassword1')
```

Also, when a profile exists it will be reloaded. Profiles hold the server, username, password and other student preference settings such as print_rich_text and show_all_scores. Students can usually restart a session with just running these commands.

```
import pywars
d = pywars.Client()
d.login()
```

Students can restart a session by just typing `pywars` at a bash prompt. See pywars command section for more details.

```
$ pywars
Welcome to pyWars
>>> d.score()
                      Scoreboard                       
┏━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Rank ┃ Name  ┃ Score ┃ Last Scored     ┃ Completed  ┃
┡━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 001  │ markb │ 009   │ Sep,13 19:57:45 │ 1,3-7,9-12 │
└──────┴───────┴───────┴─────────────────┴────────────┘
>>> 
```

### pywars command.

You now have a pywars command which helps with setup and maintains user profiles for CTF and days 1-5.
If provided username does not exists it prompts for registration code and creates the account, then logs you in.

```
(pywars5) student@SEC573:~/Downloads$ pywars
What is the hostname (example: live.sec573.com) of the server? live.sec573.com
What is registration email address on the SANS Portal? mbaggett@sans.org
Give me a new pyWars password for this class (keystrokes not displayed): TYPE PASSWORD HERE
Welcome to pyWars
>>> 
now exiting InteractiveConsole...
```

You can setup a new profile for CTF with -n

```
(pywars5) student@SEC573:~/Downloads$ pywars -n
What is the hostname (example: live.sec573.com) of the server? live.sec573.com
What is registration email address on the SANS Portal? CTF-LOGIN
Give me a new pyWars password for this class (keystrokes not displayed): CTF PASSWORD HERE
Welcome to pyWars
>>> 
now exiting InteractiveConsole...
```

You can switch between user profiles with -s.

```
(pywars5) student@SEC573:~/Downloads$ pywars -s
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ # ┃ Server                        ┃ Username          ┃ Current Default ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 0 │ https://live.sec573.com:10000 │ mbaggett@sans.org │ Y               │
│ 1 │ https://live.sec573.com:10000 │ ctf-team-login    │ N               │
└───┴───────────────────────────────┴───────────────────┴─────────────────┘
Which profile number would you like to load?0
Welcome to pyWars
>>> 
now exiting InteractiveConsole...
```

And the bash command `pywars` just reloads the default (selected) profile and logs you in.

```
$ pywars
Welcome to pyWars
>>> d.score()
                      Scoreboard                       
┏━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Rank ┃ Name  ┃ Score ┃ Last Scored     ┃ Completed  ┃
┡━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 001  │ markb │ 009   │ Sep,13 19:57:45 │ 1,3-7,9-12 │
└──────┴───────┴───────┴─────────────────┴────────────┘
>>> 
```






