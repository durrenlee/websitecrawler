from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import lxml
import requests
import uuid
import requests
import re
from pathlib import Path
import os
import warnings
warnings.filterwarnings("ignore")

headers = {"User-agent": UserAgent().random,
           "Accept-Encoding": "gzip, deflate, br",
           "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
           "Connection": "keep-alive"}


# img_re = re.compile('"thumbURL":"(.*?)"')
# img_format = re.compile("f=(.*).*?w")


def file_op(a_link_str, root_url, root_local):
    if len(a_link_str.split('/')):
        sub_folder = root_local
        # check folder exists and creation
        for a_folder in a_link_str.split('/')[1:-1]:
            sub_folder = sub_folder + "/" + a_folder
            my_file = Path(sub_folder.lstrip().lstrip())
            if not my_file.exists():
                os.makedirs(my_file)
        # get file from internet and save it to local folder
        save_file(root_url, a_link_str)


def save_file(root_url, a_link_str):
    # read file content
    file_full_url = root_url + a_link_str
    print(file_full_url)
    r = requests.Session()
    file_rsp = r.get(url=file_full_url, verify=False)
    # parse css file to download image files
    if file_full_url.__contains__('.css'):
        for line in file_rsp.iter_lines():
            if line.decode().__contains__('background: url(') \
                    and not line.decode().__contains__('/*') \
                    and not line.decode().__contains__('*/'):
                print(line)
                start = 'url('
                end = ')'
                line_str = line.decode()
                img_uri = line_str[line_str.find(start) + len(start):line_str.rfind(end)]
                # print(img_uri)
                if not img_uri.__contains__('loading.gif'):
                    parent_folders = a_link_str[0:a_link_str.find('css')-1]
                    # print(parent_folders)
                    img_uri = img_uri.replace('..', parent_folders)
                    # print(img_uri)
                    img_url = root_url + img_uri
                    print(img_url)
                    r_img = requests.Session()
                    img_file_rsp = r_img.get(url=img_url, verify=False)
                    img_full_path_name = root_local + img_uri
                    print(img_full_path_name)
                    with open(file=img_full_path_name, mode="wb") as file:
                        file.write(img_file_rsp.content)

    full_path_name = root_local + a_link_str
    print(full_path_name)
    with open(file=full_path_name, mode="wb") as file:
        file.write(file_rsp.content)


def xhr_url(url_xhr, root_local):
    s = requests.Session()
    response = s.get(url_xhr, verify=False)
    # save index.html
    index_name = root_local + "/" + "index.html"
    with open(file=index_name, mode="wb") as file:
        file.write(response.content)

    # parse content
    if response.status_code == 200:
        # print(response.text)
        soup = BeautifulSoup(response.text, 'lxml')
        # parse head tag to download css files and fonts file
        links = soup.select('link')
        for a_link in links:
            if a_link.has_attr('href'):
                a_link_str = a_link.get('href')
                file_op(a_link_str, url_xhr, root_local)
        # parse script tag to download JS files
        scripts = soup.select('script')
        for a_script in scripts:
            if a_script.has_attr('src'):
                a_script_str = a_script.get('src')
                if not a_script_str.lower().__contains__("http:") and not a_script_str.lower().__contains__("https:"):
                    file_op(a_script_str, url_xhr, root_local)
        # parse img tag to download image files
        images = soup.select('img')
        for an_image in images:
            if an_image.has_attr('src'):
                an_image_str = an_image.get('src')
                if not an_image_str.lower().__contains__("http:") and not an_image_str.lower().__contains__("https:"):
                    file_op(an_image_str, url_xhr, root_local)

        # parse div tag to download image files from background:url
        # no background:url in source code


if __name__ != "__main__":
    pass
else:
    org_url = "https://www.sprixin.com"
    root_local = "D:/github/webspider"
    xhr_url(url_xhr=org_url, root_local=root_local)
