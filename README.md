# sqlitem
Sqlite multithreaded version named sqlitem. Sqlitem is a way to use sqlite in multithreaded mode which allows you to execute multiple command from any thread you want. I love using sqlite in my projects because of its simplicity, and I decided to make Sqlitem to use it in my new project. One of most simple ways to use sqlite in any thread is to connect and close inside fo thread. But that's boring! 😑


## What can Sqlitem do :
- Work in multiple threads
- Handle auto commits
- execute up to 8000 commands per seconds

When you execute a command in Sqlitem it appends it to a list with an ID and waits for return in a dictionary. It's most simple way to use sqlite in multithreaded mode, Instead it uses more RAM resources. For more information read code...

<br />

> 8000 commands/second happened with insert commands!


> I decided to add an option to execute method to use a function as result checker and now we can avoid high RAM resources usage. It simply returns rows of data from cursor to checker function and there you can make conditions to check returned data and do anything you want. In this way results will not be returned in execute command and RAM will be safe. #not_overusing_RAM 

<br />
<br />

## How to use Sqlitem

### Import Sqlitem to your project file

```python
from sqlitem import SqliteMultiThreadedHandler
```
<br />

### Connect to database
```python
db = SqliteMultiThreadedHandler()
db.connect("path-to-database", create_if_not_exists=False, rest_time=0.0001)
```
As you can see we have two more options. **"create_if_not_exists"** create's database with it's folders given in path if you give th parameter True. And **"rest_time"** means checking each x time in seconds for new command to execute, which is important and it depends on your hardware resources. When it happens and loop's condition detects new more than 0 command in list, it starts executing until the list is empty.

<br />

### Set Auto commits
```python
db.set_auto_commit_by_request(100)
db.set_auto_commit_in_rest(1)
db.set_auto_commit_per_time(60)
```
Using auto commits you can make sure there is safety and enough speed to proceed all commands. You can use all at once and the result of values above is something like this :

- commit after every 100 requests
- commit after 1 second if there is nothing in list and have get in rest mode
- commit every minute (60s)

These auto commits made my own life easier...

<br />

### Execute commands
```python
db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)" commit=True)
db.execute("INSERT INTO users(name, phone)VALUES(?, ?)", args=("someone0", "+1xxxx"), commit=True)
db.execute("INSERT INTO users(name, phone)VALUES(?, ?)", args=("someone1", "+1xxxx"), commit=False)
db.execute("SELECT * FROM users")
```
You can execute command like codes above and give args and commit after execution. 
> By default commit=False and args=tuple()

<br />

### Get returned data of db.execute
The output type is **SqlitemOutputItem** which has fetchone, fetchall and fetchmany methods :
```python
result = db.execute("SELECT * FROM users")
result.fetchone()
result.fetchall()
result.fetchmany(10)
```

<br />

### Get returned data with a function (Avoid overusing RAM resources)
In this way we can make a function to check and get useful returned data
```python
result = []
def check_results(data_row):
    if data_row[0] == 12:
        result.append(data_row)

finished = db.execute("select * from users where name=?", args=("tony",), gfunc=check_results)
print(result)
print(finished)
```
> **OUTPUT :** <br /> [(12, "tony", "+1xxxx")] <br /> []

As you can see the output is a tuple inside of result list and finished variable is an empty list because we told the execute method to return rows of data to **check_result** function (As mentioned in the title). 

<br />

### Commit
```python
db.commit()
```

<br />

### Close Database
```python
db.close(commit_requests=False)
```
You can commit all request at the end by setting commit_requests=True. Ensure that all requests have been processed and then close the database, otherwise all remaining requests will be deleted from the non-executing list.

<br />

### Close database in safe mode
```python
db.safe_close()
```
After safe close you will not be able to add any command to execution list. Then all of remained commands will be executed and then database will be closed with a commit at the end. 😄

<br />
<br />

## Example Of Sqlitem Usage (!!!)
```python

import threading
from sqlitem import SqliteMultiThreadedHandler


class TestMode:
    def __init__(self):
        self.db = SqliteMultiThreadedHandler()
        self.db.connect("./test.db")  # you can set create_if_not_exists and rest_time if needed
        table = """CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)"""
        self.db.execute(table)
        
        #self.db.set_auto_commit_per_time(30)
        #self.db.set_auto_commit_in_rest(10)
        #self.db.set_auto_commit_by_request(10)

    def add_user(self, name, phone):
        self.db.execute("INSERT INTO users(name, phone)VALUES(?, ?)", args=(name, phone), commit=False)

    def get_user(self, name):
        user = self.db.execute("SELECT * FROM users WHERE name=?", args=(name,))
        return user.fetchall()

    def get_desired_users(self):
        results = []

        def check_result(data_row):
            if "Tony" in data_row[1]:
                results.append(data_row)

        self.db.execute("SELECT * FROM users", gfunc=check_result)
        return results

    def close(self):
        self.db.safe_close()




test = TestMode()

def add_users():
    users = ["Tony Kulaei", "Someone Else", "Giga Me", "Am I A Person"]
    for i in range(1000):
        for user in users:
            test.add_user(user, "0")
    
    test.db.commit()


def get_user():
    for i in range(100):
        print(test.get_user("Someone Else"))


def get_userssss():
    for i in range(100):
        print(test.get_desired_users())


threading.Thread(target=add_users).start()
threading.Thread(target=get_user).start()
threading.Thread(target=get_userssss).start()
``` 

<br />

## \> coming soon ^
- [ ] Adding executemany
- [ ] Adding executescript

<br />
<br />


<sup> sudo apt update && sudo apt upgrade </sup> :octocat:
