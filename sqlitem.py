# 786

# code by Tony Kulaei

"""
<< Sqlitem >>

Sqlite database's multithread mode!  sqlite locks the database for safety and
that's good but we want it in multithreaded mode to execute commands from any
thread in program. Sqlitem solves this problem.

Created By Tony Kulaei - August 7, 2022
Github : https://github.com/slashTony
Update : August 16, 2022
"""
import os
import time
import sqlite3
import threading
from traceback import format_exc


class SqlitemOutputItem(object):
    def __init__(self, mainlist=None):
        super(SqlitemOutputItem, self).__init__()
        self.output_list = []
        if mainlist != None and type(mainlist) == list:
            self.output_list = mainlist

    def fetchone(self):
        if len(self.output_list) > 0:
            return self.output_list[0]
        else:
            return None
    def fetchall(self):
        return self.output_list
    def fetchmany(self, size):
        return self.output_list[:size]
    def __str__(self):
        return f"{self.output_list}"




class SqliteMultiThreadedHandler:
    """
    << Sqlite MultiThreaded Handler >>

    The way it works is simple. we just need to put requests in a list to execute in a loop one by one
    in order. And then putting answer in another list or dictionary to return it in the request method
    to avoid locking problem!

    Please read the code... Code is always valid and honest
    """
    def __init__(self):
        self.__request_input_list = []
        self.__request_output_dict = {}
        self.__request_id = 0
        self.__keep_running = True
        self.__auto_commit_counter = None
        self.__auto_commit_in_rest_interval = None
        self.__commit_requests_on_close = False
        self.__safe_close_mode = False


    def connect(self, path:str, create_if_not_exists: bool = False, rest_time: float = 0.001):
        self.rest_time = rest_time
        if create_if_not_exists:
            dir_path = "/".join(path.split("/")[:-1])
            os.makedirs(dir_path)
            
        exec_thread = threading.Thread(target=self.__exec, args=(path, rest_time))
        exec_thread.start()

    def __exec(self, path, rest_time):
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        request_counter = 0
        rest_counter = 0
        
        while self.__keep_running:
            if len(self.__request_input_list) > 0:
                rest_counter = 0
                item = self.__request_input_list[0]
                item_id = item["id"]
                request = item["request"]
                args = item["args"]
                gfunc = item["gfunc"]
                commit = item["commit"]
                result = []
                if request == "commit":
                    conn.commit()
                else:
                    try:
                        cursor.execute(request, args)
                        if commit == True:
                            conn.commit()

                        # generator function output
                        if callable(gfunc) == True:
                            for row in cursor:
                                gfunc(row)
                        elif gfunc == None:
                            result = cursor.fetchall()
                        elif callable(gfunc) == False:
                            raise Exception("given argument as gfunc is not callable")


                        # checking auto commit per request
                        if (self.__auto_commit_counter != None) and (request_counter >= self.__auto_commit_counter):
                            conn.commit()
                            request_counter = 0

                    except Exception as err:
                        result.append(err)
                        print(format_exc())
                        print("command : ", request)

                    self.__request_output_dict[item_id] = result
                self.__request_input_list.pop(0)
                request_counter += 1

            else:
                time.sleep(rest_time)
                # counting rest time and commiting
                rest_counter += rest_time
                if (self.__auto_commit_in_rest_interval != None) and (rest_counter >= self.__auto_commit_in_rest_interval):
                    conn.commit()
                    rest_counter = 0

                if self.__safe_close_mode == True:
                    self.close(commit_requests=True)
                    break


        if self.__commit_requests_on_close == True:
            conn.commit()
        cursor.close()


    def execute(self, request:str, args: tuple = tuple(), gfunc=None, commit: bool = False):
        if self.__safe_close_mode == False:
            self.__request_id += 1
            request_id = self.__request_id
            new_request = {"id" : request_id, "request" : request, "args" : args, "gfunc" : gfunc, "commit" : commit}
            self.__request_input_list.append(new_request)
            # getting answer
            answer = False
            while answer == False:
                answer = self.__request_output_dict.get(request_id, False)
                time.sleep(self.rest_time)

            self.__request_output_dict.pop(request_id)
            return SqlitemOutputItem(answer)
        else:
            raise Exception("Safe close mode is enabled. Adding new commands to execution list is not possible, database will be closed soon.")


    def commit(self):
        self.__request_id += 1
        request_id = self.__request_id
        new_request = {"id": request_id, "request": "commit", "args": (), "gfunc" : None, "commit": True}
        self.__request_input_list.append(new_request)

    def set_auto_commit_per_time(self, timeout: float = 60.0):
        threading.Thread(target=self.__auto_commit_timer_exec, args=(timeout,)).start()
    def __auto_commit_timer_exec(self, timeout):
        counter = 0
        while self.__keep_running:
            if counter >= timeout:
                self.commit()
                counter = 0
            counter += 1
            time.sleep(1)


    def set_auto_commit_by_request(self, interval: int or None = 10):
        self.__auto_commit_counter = interval

    def set_auto_commit_in_rest(self, timeout: float or None = 10.0):
        self.__auto_commit_in_rest_interval = timeout

    def close(self, commit_requests: bool = False):
        self.__commit_requests_on_close = commit_requests
        self.__keep_running = False

    def safe_close(self):
        """
        Safe close means ignoring any input to list
        of commands and executing all the list and
        then closing database safely with commit at
        the end.
        """
        self.__safe_close_mode = True
