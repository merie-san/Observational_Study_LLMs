import json
import os
import time
import requests
import random

REPOSITORY_URL = "https://api.github.com/repos"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
}


def github_get(url, headers):
    """GET request to GitHub with intelligent rate limit handling."""
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            raise Exception(
                "Unauthorized: Check your GITHUB_TOKEN environment variable."
            )
        if response.status_code != 200:
            if int(response.headers.get("X-RateLimit-Remaining", "0")) == 0:
                reset_time = int(response.headers.get("X-RateLimit-Reset", time.time()))
                current_time = int(time.time())
                wait_time = reset_time - current_time + 1
                print(f"Rate limit exceeded, sleeping {wait_time} seconds...")
                time.sleep(wait_time)
                print("Resuming requests...")
                continue
            else:
                print(
                    f"GitHub API request failed with status code {response.status_code}"
                )
                print(response)
                time.sleep(3)
                continue
        else:
            time.sleep(0.25)
            return response


def attribute_searching(data_file: str, suffix: str):
    with open(data_file, "r") as f:
        data_dicts = json.load(f)
    sampled_dicts = random.sample(data_dicts, 1000)
    responses = []
    for repo in sampled_dicts:
        response = github_get(f"{REPOSITORY_URL}/{repo["fullname"]}", headers=HEADERS)

        item = response.json()

        responses.append(
            {
                "id": item.get("id"),
                "full_name": item.get("full_name"),
                "html_url": item.get("html_url"),
                "description": item.get("description"),
                "language": item.get("language"),
                "created_at": item.get("created_at"),
                "stargazers_count": item.get("stargazers_count"),
                "open_issues_count": item.get("open_issues_count"),
                "size": item.get("size") / 1000,
                "topics": item.get("topics", []),
                "license": (
                    item.get("license", {}).get("key") if item.get("license") else None
                ),
                "owner_login": (item["owner"]["login"] if item.get("owner") else None),
                "owner_type": (item["owner"]["type"] if item.get("owner") else None),
                "archived": item.get("archived"),
                "subscribers_count": item.get("subscribers_count"),
                "network_count": item.get("network_count"),
            }
        )
        print(
            f"appended repo {item.get("full_name")} created at {item.get("created_at")}"
        )
    with open(f"Data/sampled_repo_{suffix.lower()}.json", "w") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)

    return


if __name__ == "__main__":
    attribute_searching("Data/collected_repos_go.json", "go")
