import time
import requests

for i in range(10):
    try:
        requests.get("http://127.0.0.1:5112/shutdown")
        time.sleep(5)
        break
    except Exception as e:
        print(f"ERROR: ({type(e)}) - {e}")
