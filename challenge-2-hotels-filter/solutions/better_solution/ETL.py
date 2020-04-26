import subprocess
import os
import requests
import time

FNULL = open(os.devnull, "w")
proc = subprocess.Popen(
    ["python", "flask_prep.py"], stderr=FNULL, stdout=FNULL
)

print("STARTING proc pid: ", proc.pid)

while True:
    try:
        time.sleep(1)
        requests.get("http://127.0.0.1:5112/started")
        time.sleep(4)
        break
    except Exception as e:
        print(f"ERROR: ({type(e)}) -  {e}")
