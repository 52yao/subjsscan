import argparse
import os
import re
import requests
import time
import concurrent.futures
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm


def extract_strings(text):
    pattern = r"['\"{}\(\)\[\]]([A-Za-z0-9\\/\.]{1,100})['\"{}\(\)\[\]]"
    matches = re.findall(pattern, text)
    return matches


def extract_title(text):
    soup = BeautifulSoup(text, "html.parser")
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.text.strip()
    return ""


def save_to_file(strings, filename):
    existing_strings = set()

    # 检查现有的 zifu.txt 文件，将已存在的字符串添加到集合中
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                existing_strings.add(line.strip())

    # 过滤重复的字符串并将新字符串保存到文件中
    new_strings = []
    for string in strings:
        if string not in existing_strings:
            new_strings.append(string)
            existing_strings.add(string)

    if new_strings:
        with open(filename, "a", encoding="utf-8") as file:
            for string in new_strings:
                file.write(string + "\n")


def download_file(url, folder_name):
    response = requests.get(url, verify=True)
    if response.status_code == 200:
        file_name = get_valid_filename(url.split("/")[-1].split("?")[0])
        file_path = os.path.join(folder_name, file_name)
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"文件已下载: {file_name}")
        if file_name.endswith(".js"):
            # 如果是JavaScript文件，则提取满足要求的字符串并保存到zifu.txt文件中
            with open(file_path, "r", encoding="utf-8") as js_file:
                content = js_file.read()
                strings = extract_strings(content)
                save_to_file(strings, os.path.join(folder_name, "zifu.txt"))


def download_pages(url):
    # 创建以URL命名的文件夹
    folder_name = get_valid_filename(url)
    os.makedirs(folder_name, exist_ok=True)

    response = requests.get(url, verify=True)
    if response.status_code == 200:
        content_type = response.headers.get("content-type")
        if "text/html" in content_type:
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.prettify()

            # 保存页面内容到文件
            file_name = "page.html"
            file_path = os.path.join(folder_name, file_name)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text)

            # 提取满足要求的字符串并保存到文件
            strings = extract_strings(text)
            save_to_file(strings, os.path.join(folder_name, "zifu.txt"))

            # 下载JavaScript文件
            script_tags = soup.find_all("script")
            for script_tag in script_tags:
                if script_tag.get("src"):
                    script_url = urljoin(url, script_tag["src"])
                    download_file(script_url, folder_name)

            print(f"页面已下载并保存至文件夹 {folder_name}")
        else:
            print("不是HTML响应")
    else:
        print("无法获取URL")


def get_valid_filename(filename):
    # 替换文件名中的非法字符
    filename = re.sub(r'[\\/:*?"<>|]', "_", filename)
    return filename

def process_url(suburl):
    response = requests.get(suburl, verify=True)
    if response.status_code == 200:
        status_code = response.status_code
        content_length = len(response.content)
        title = extract_title(response.content)
        with open("over.txt", "a", encoding="utf-8") as file:
            file.write(f"URL: {suburl}\t状态码: {status_code}\t返回包大小: {content_length}\t标题: {title}\n")
    else:
        with open("over.txt", "a", encoding="utf-8") as file:
            file.write(f"URL: {suburl}\t请求失败\n")


def main():
    parser = argparse.ArgumentParser(description="从URL下载并提取字符串")
    parser.add_argument("-u", "--url", required=True, help="要下载的URL")
    args = parser.parse_args()

    url = args.url
    download_pages(url)

    print("已提取关键词完毕")
    time.sleep(5)  # 暂停5秒钟

    folder_name = get_valid_filename(url)
    suburl_file = os.path.join(folder_name, "suburl.txt")

    if os.path.isfile(suburl_file):
        with open(suburl_file, "a", encoding="utf-8") as outfile:
            zifu_file = os.path.join(folder_name, "zifu.txt")
            if os.path.isfile(zifu_file):
                with open(zifu_file, "r", encoding="utf-8") as file:
                    zifu_strings = file.read().splitlines()
                    progress_bar = tqdm(zifu_strings, desc="保存目录", unit="URL", bar_format="{l_bar}{bar}")
                    for string in progress_bar:
                        suburl = url + string
                        outfile.write(suburl + "\n")
            else:
                print("无法找到zifu.txt文件")
    else:
        with open(suburl_file, "w", encoding="utf-8") as outfile:
            zifu_file = os.path.join(folder_name, "zifu.txt")
            if os.path.isfile(zifu_file):
                with open(zifu_file, "r", encoding="utf-8") as file:
                    zifu_strings = file.read().splitlines()
                    progress_bar = tqdm(zifu_strings, desc="保存目录2", unit="URL", bar_format="{l_bar}{bar}")
                    for string in progress_bar:
                        suburl = url + string
                        outfile.write(suburl + "\n")
            else:
                print("无法找到zifu.txt文件")

    print("等待2秒钟")
    time.sleep(2)


    outfile = os.path.join(folder_name, "over.txt")
    with open(suburl_file, "r", encoding="utf-8") as file:
        urls = file.read().splitlines()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:     #指定线程数为10
            futures = []
            for suburl in urls:
                future = executor.submit(process_url, suburl)
                futures.append(future)
                
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="访问拼接关键词后的目录", unit="URL"):
                pass

    print("结束")

if __name__ == "__main__":
    main()

