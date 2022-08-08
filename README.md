# sqlitem
Sqlite multithreaded version named sqlitem. Sqlitem is a way to use sqlite in multithreaded mode which allows you to execute multiple command from any thread you want. I love using sqlite in my programs because of its simplicity, and I decided to make Sqlitem to use it in my new project. One of most simple ways to use sqlite in any thread is to connect and close inside fo thread. But that's boring!


## What can Sqlitem do :
- Work in multiple threads
- Handle auto commits
- execute up to 8000 commands per seconds

When you execute a command in Sqlitem it appends it to a list with an ID and waits for return in a dictionary. It's most simple way to use sqlite in multithreaded mode, Instead it uses more RAM resources. For more information read code...

<br />

> 8000 commands/second happened with insert commands!


> You can solve high RAM resources usage by executing right commands. For example instead of selecting all users and searching in python try searching with sql commands. This way sqlite can handle it, and if you need to select large amount of data then you still have this problem.

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

- commit each 100 requests
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

#### Get the output of db.execute
The output type is **SqlitemOutputItem** which has fetchone, fetchall and fetchmany methods :
```python
result = db.execute("SELECT * FROM users")
result.fetchone()
result.fetchall()
result.fetchmany(10)
```

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
<br />
<br />

## Problems and updates

The unsolved problem is that we can't use generators to lower RAM resource usage.
- Add safe close mode
- Find a way to lower RAM resource usage
