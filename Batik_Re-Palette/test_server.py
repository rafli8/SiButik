import urllib.request
import time
import sys

print('Testing Gradio server stability...', flush=True)
for i in range(3):
    try:
        r = urllib.request.urlopen('http://127.0.0.1:7860/', timeout=5)
        print(f'[Test {i+1}] HTTP {r.status} - OK ({r.headers.get("content-length")} bytes)', flush=True)
    except Exception as e:
        print(f'[Test {i+1}] FAIL: {e}', flush=True)
    time.sleep(2)

try:
    r = urllib.request.urlopen('http://127.0.0.1:7860/gradio_api/info', timeout=5)
    print(f'[Gradio API] HTTP {r.status}', flush=True)
except Exception as e:
    print(f'[Gradio API] FAIL: {e}', flush=True)

print('DONE', flush=True)