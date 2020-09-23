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
>>> d.login("Your Chosen Username","Your Chosen Password")
```

Once your account the account is created and logged in you can use the following methods to interact with the server:
 - ```d.question(<question name or number>)``` - Retrieve and show the question.
 - ```d.data(<question name or number>,[True])``` - Retrieve and show a sample of the data. If True is second argument data is unzipped for you.
 - ```d.answer(<your answer>)``` - Submit the answer for the last data you queried.
 - ```d.solution(<path to your solution script>)``` - Submit your code for review and scoring
 - ```d.score([True])``` - Retrieve and show the scoreboard.  If True is passed it will display all scocres instead of only yours.
 - ```d.logout()``` - Log out from your current session.
 - ```d.password(current,new)``` - Change the password for the logged on account from current to new.
 - ```print(d.names)``` - show a list of all loaded challenge names
 






