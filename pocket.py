import httpx
from typing import List
import argparse
import pandas as pd
from loguru import logger
from yutils import normalize_url

CONSUMER_KEY = ""


def authenticate():
    redirect_uri = "http://localhost/pocket"
    data = {
        "consumer_key": CONSUMER_KEY,
        "redirect_uri": redirect_uri,
    }
    rsp = httpx.post("https://getpocket.com/v3/oauth/request", data=data)
    code = rsp.text.replace("code=", "")
    req_url_temp = "https://getpocket.com/auth/authorize?request_token={code}&redirect_uri={redirect_uri}"
    req_url = req_url_temp.format(code=code, redirect_uri=redirect_uri)
    logger.info("Open in your browser and click authorize: {}", req_url)
    # webbrowser.open(req_url, new=1)
    input("Press Enter to continue...")

    authorize_data = {"consumer_key": CONSUMER_KEY, "code": code}
    rsp = httpx.post(
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
    rsp = httpx.get("https://getpocket.com/v3/get", params=params)
    post_list = []
    for post_json in rsp.json()["list"].values():
        url = post_json["given_url"]
        url = normalize_url(url)
        title = post_json["given_title"] or post_json["resolved_title"]
        post_list.append({"url": url, "title": title})
    return post_list


def main():
    access_token = authenticate()
    logger.info("Access token is {}", access_token)
    post_list = retrive_list(access_token)
    df = pd.DataFrame(post_list)
    df.to_csv("pocket.csv", index=False)


if __name__ == "__main__":
    main()
