import json
import os
import time
import numpy as np
import requests

CODE_SEARCH_URL = "https://api.github.com/search/code"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
}


def retrieve_all(query: str, start_size_delta: int):
    """retrieve all results for a given query by chunking by size"""

    request_ns = []
    seen_repos = set()
    size_delta = start_size_delta
    curr_size = 0
    while curr_size < 5000:

        params = {
            "q": query + f" size:{curr_size}..{curr_size+size_delta-1}",
            "per_page": 100,
        }

        request_n = 0
        for i in range(10):
            params["page"] = i + 1
            response = requests.get(CODE_SEARCH_URL, headers=HEADERS, params=params)
            if response.status_code != 200:
                if int(response.headers.get("X-RateLimit-Remaining", "0")) == 0:
                    reset_time = int(
                        response.headers.get("X-RateLimit-Reset", time.time())
                    )
                    current_time = int(time.time())
                    wait_time = reset_time - current_time + 1
                    print(f"Rate limit exceeded, sleeping {wait_time} seconds...")
                    time.sleep(wait_time)

                    print("Resuming requests...")
                    response = requests.get(
                        CODE_SEARCH_URL, headers=HEADERS, params=params
                    )

                    if response.status_code != 200:
                        raise Exception(
                            f"GitHub API request failed with status code {response.status_code}: {response.json().get('message',"No message")}"
                        )
                else:
                    raise Exception(
                        f"GitHub API request failed with status code {response.status_code}: {response.json().get('message',"No message")}"
                    )

            data = response.json()
            items = data.get("items", [])
            if not items:
                break
            for item in items:
                repo = item.get("repository")
                if repo and repo["full_name"] not in seen_repos:
                    seen_repos.add(repo["full_name"])
                    yield {
                        "full_name": repo.get("full_name"),
                        "html_url": repo.get("html_url"),
                    }
            request_n += len(items)
            print(f'Retrieved {request_n} results for "query:{params["q"]}" so far...')
            time.sleep(1)
        request_ns.append(request_n)

        if request_n >= 1000:
            if size_delta <= 1:
                raise Exception(
                    "GitHub API code search limit reached with 1kb size delta, chunking failed."
                )
            else:
                size_delta = int(size_delta / 2)
                continue
        curr_size += size_delta
        if request_n > 600 and size_delta > 1:
            size_delta = int(size_delta / 2)
        elif request_n < 300:
            size_delta += 1
        elif request_n < 100:
            size_delta += 5


if __name__ == "__main__":
    # Python LLM usage
    python_keyword_dict = {"import OpenAI": "OpenAI"}
    python_repo_set = set()
    for keyword, provider in python_keyword_dict.items():
        print(f"Searching for keyword: {keyword}")
        for repo in retrieve_all(f'language:python "{keyword}"', 5):
            print(f"Found unique repo: {repo['full_name']} at {repo['html_url']}")
            repo["llm_sdk"] = provider
            python_repo_set.add(repo)
    with open("collected_repos_python.json", "w") as f:
        json.dump(python_repo_set, f, indent=2)
    # Java LLM usage
    java_keyword_dict = {}
    java_repo_set =set()
    for keyword, provider in java_keyword_dict.items():
        print(f"Searching for keyword: {keyword}")
        for repo in retrieve_all(f'language:java "{keyword}"', 5):
            print(f"Found unique repo: {repo['full_name']} at {repo['html_url']}")
            repo["llm_sdk"] = provider
            java_repo_set.add(repo)
    with open("collected_repos_java.json", "w") as f:
        json.dump(java_repo_set, f, indent=2)
    # Javascript LLM usage
    javascript_keyword_dict = {}
    javascript_repo_set = set()
    for keyword, provider in javascript_keyword_dict.items():
        print(f"Searching for keyword: {keyword}")
        for repo in retrieve_all(f'language:javascript "{keyword}"', 5):
            print(f"Found unique repo: {repo['full_name']} at {repo['html_url']}")
            repo["llm_sdk"] = provider
            javascript_repo_set.add(repo)
    with open("collected_repos_javascript.json", "w") as f:
        json.dump(javascript_repo_set, f, indent=2)
    # Go LLM usage
    go_keyword_dict = {}
    go_repo_set = set()
    for keyword, provider in go_keyword_dict.items():
        print(f"Searching for keyword: {keyword}")
        for repo in retrieve_all(f'language:go "{keyword}"', 5):
            print(f"Found unique repo: {repo['full_name']} at {repo['html_url']}")
            repo["llm_sdk"] = provider
            go_repo_set.add(repo)
    with open("collected_repos_go.json", "w") as f:
        json.dump(go_repo_set, f, indent=2)
    # C# LLM usage
    csharp_keyword_dict = {}
    csharp_repo_set = set()
    for keyword, provider in csharp_keyword_dict.items():
        print(f"Searching for keyword: {keyword}")
        for repo in retrieve_all(f'language:c# "{keyword}"', 5):
            print(f"Found unique repo: {repo['full_name']} at {repo['html_url']}")
            repo["llm_sdk"] = provider
            csharp_repo_set.add(repo)
    with open("collected_repos_csharp.json", "w") as f:
        json.dump(csharp_repo_set, f, indent=2)
