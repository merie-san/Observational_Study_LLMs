import json
import os
import sys
import time
import requests

CODE_SEARCH_URL = "https://api.github.com/search/code"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
}


class repo:
    """Class representing a GitHub repository with labeles for each file."""

    def __init__(self, full_name, html_url):
        self.full_name = full_name
        self.html_url = html_url
        self.labels = {}

    def __hash__(self) -> int:
        return hash(self.full_name)

    def __eq__(self, other) -> bool:
        return isinstance(other, repo) and self.full_name == other.full_name

    def add_file_label(self, label: str, file_path: str):
        if label in self.labels:
            self.labels[label].add(file_path)
        else:
            self.labels[label] = set([file_path])

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "html_url": self.html_url,
            "labels": {k: list(v) for k, v in self.labels.items()},
        }

    @classmethod
    def from_dict(cls, dict):
        obj = cls(dict["full_name"], dict["html_url"])
        obj.labels = {k: set(v) for k, v in dict.get("labels", {}).items()}
        return obj


def retrieve_all(query: str, start_size_delta: int):
    """Retrieve all results for a given query by chunking with repo size"""

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
            if response.status_code == 401:
                raise Exception(
                    "Unauthorized: Check your GITHUB_TOKEN environment variable."
                )
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
                        print(f"GitHub API request failed with status code {response.status_code}")
                        time.sleep(3)
                        continue
                else:
                    if response.status_code != 200:
                        print(f"GitHub API request failed with status code {response.status_code}")
                        time.sleep(3)
                        continue

            data = response.json()
            items = data.get("items", [])
            if not items:
                break
            for item in items:
                repo_v = item.get("repository")
                if repo_v:
                    yield {
                        "full_name": repo_v.get("full_name"),
                        "html_url": repo_v.get("html_url"),
                        "file_path": item.get("path"),
                    }
            request_n += len(items)
            print(f'Retrieved {request_n} results for "query:{params["q"]}" so far...')
            time.sleep(1)

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


def collect_repo_by_language(language: str, keyword_dict: dict, suffix: str = ""):
    if not keyword_dict:
        print(f"No keywords for {language}, skipping.")
        return
    repo_dict = {}
    try:
        for keyword, group in keyword_dict.items():
            print(f"Searching for keyword: {keyword}")
            for data in retrieve_all(f'language:{language} "{keyword}"', 5):
                print(
                    f"Found reference of \"{keyword}\" for {language}. repo - {data['full_name']}, file - {data['file_path']}"
                )
                full_name = data["full_name"]
                if full_name not in repo_dict:
                    repo_dict[full_name] = repo(full_name, data["html_url"])
                repo_dict[full_name].add_file_label(group, data["file_path"])
        with open(
            f"Data/collected_repos_{language}{"_"+suffix if suffix!="" else ""}.json",
            "w",
        ) as f:
            json.dump([r.to_dict() for r in repo_dict.values()], f, indent=2)
    except KeyboardInterrupt as e:
        print(
            f"keyboard interrupt detected, found {len(repo_dict)} repos. Saving intermediary results..."
        )
        with open(
            f"Data/collected_repos_{language}{"_"+suffix if suffix!="" else ""}.json",
            "w"
        ) as f:
            json.dump([r.to_dict() for r in repo_dict.values()], f, indent=2)
        sys.exit(0)


if __name__ == "__main__":
    with open("model_keyword_dict.json", "r") as f:
        model_keyword_dict = json.load(f)

    # Python LLM usage
    collect_repo_by_language(
        "python",
        {
            "import openai": "OpenAI",
            "from google import genai": "Google",
            "import google.genai": "Google",
            "import anthropic": "Anthropic",
            "from anthropic import Anthropic": "Anthropic",
            "from xai_sdk import Client": "xAI",
            "import xai_sdk.Client": "xAI",
            "from llama_api_client import LlamaAPIClient": "Meta",
            "import llama_api_client.LlamaAPIClient": "Meta",
            "from mistralai import Mistral": "Mistral",
            "import mistralai.Mistral": "Mistral",
        },
        suffix="library",
    )

    # Python LLM model usage
    collect_repo_by_language("python", model_keyword_dict, suffix="model")

    # Java LLM usage
    collect_repo_by_language(
        "java",
        {
            "import com.openai.client.OpenAIClient;": "OpenAI",
            "import com.openai.client.*;": "OpenAI",
            "import com.google.genai.Client;": "Google",
            "import com.google.genai.*;": "Google",
            "import com.anthropic.client.AnthropicClient;": "Anthropic",
            "import com.anthropic.client.*;": "Anthropic",
        },
        suffix="library",
    )

    # Java LLM model usage
    collect_repo_by_language("java", model_keyword_dict, suffix="model")

    # Go LLM usage
    collect_repo_by_language(
        "go",
        {
            "github.com/openai/openai-go": "OpenAI",
            "google.golang.org/genai": "Google",
            "github.com/anthropics": "Anthropic",
            "github.com/liushuangls/go-anthropic": "Go-anthropic",
            'anthropic "github.com/adamchol/go-anthropic-sdk"': "Go-anthropic",
            "github.com/gage-technologies/mistral-go": "Mistral",
        },
        suffix="library",
    )

    # Go LLM model usage
    collect_repo_by_language("go", model_keyword_dict, suffix="model")
