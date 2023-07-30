from curl_cffi import requests
from typing import List
import argparse
import pandas as pd
from loguru import logger
# from yutils import normalize_url

CONSUMER_KEY = ""


def authenticate(key: str):
    redirect_uri = "http://localhost/pocket"
    data = {
        "consumer_key": key,
        "redirect_uri": redirect_uri,
    }
    rsp = requests.post("https://getpocket.com/v3/oauth/request", data=data)
    code = rsp.text.replace("code=", "")
    req_url_temp = "https://getpocket.com/auth/authorize?request_token={code}&redirect_uri={redirect_uri}"
    req_url = req_url_temp.format(code=code, redirect_uri=redirect_uri)
    logger.info("Open in your browser and click authorize: {}", req_url)
    # webbrowser.open(req_url, new=1)
    input("Press Enter to continue...")

    authorize_data = {"consumer_key": key, "code": code}
    rsp = requests.post(
        "https://getpocket.com/v3/oauth/authorize",
        json=authorize_data,
        headers={"X-Accept": "application/json"},
    )
    print(rsp.text)
    return rsp.json()["access_token"]


def retrive_list(access_token: str, state: str = "all") -> List[dict]:
    params = {
        "consumer_key": CONSUMER_KEY,
        "access_token": access_token,
        "state": state,
        "detailType": "simple",
    }
    logger.info("Start to retrive the list")
    rsp = requests.get("https://getpocket.com/v3/get", params=params)
    post_list = []
    for post_json in rsp.json()["list"].values():
        url = post_json["given_url"]
        # url = normalize_url(url)
        title = post_json["given_title"] or post_json["resolved_title"]
        post_list.append({"url": url, "title": title})
    return post_list


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="Pocket access key to use.")
    args = parser.parse_args()
    access_token = authenticate(args.key)
    logger.info("Access token is {}", access_token)
    post_list = retrive_list(access_token)
    df = pd.DataFrame(post_list)
    df.to_csv("pocket.csv", index=False)


if __name__ == "__main__":
    main()
