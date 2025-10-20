import json
import os
import requests
from tqdm import tqdm
import time

SEARCH_QUERY_OPENAI = "import OpenAI"
SEARCH_QUERY_GOOGLE = "from google import genai"
SEARCH_QUERY_XAI = "from xai_sdk"
INPUT_FILE = "repo_metadata.json"
OUTPUT_FILE = "repo_metadata_with_openai.json"
CODE_SEARCH_URL = "https://api.github.com/search/code"

keyword_list = ["import OpenAI", "from google import genai", "from xai_sdk import Client"]
# === HEADER AUTENTICAZIONE ===
headers = {
    "Authorization": f"Bearer {os.getenv("GITHUB_TOKEN")}",
    "Accept": "application/vnd.github.v3+json"
}

def search_openai_in_repo(repo_full_name, keep_going):
    if not keep_going:
        return "skipped", False
    data = send_request(repo_full_name, SEARCH_QUERY_OPENAI)
    if data.get("total_count", 0) == 0:
        return "no results", True

    # Conto le occorrenze nel codice (opzionale ma più accurato)
    model_arr = ["gpt-5", "gpt-5-nano", "gpt-5-mini", "gpt-pro", "gpt-4.1", "deepseekchat", "grok-4", "Llama-4-Maverick-17B-128E-Instruct-FP8", "Llama-4-Scout-17B-16E-Instruct-FP8"]
    for item in data.get("items", []):
        raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            code = requests.get(raw_url, headers=headers).text
            for model in model_arr:
                var = code.count(model)
                if var > 0:
                    return model + "_OpenAI", False
        except Exception:
            pass

    return "Other_OpenAI", False

def search_gemini_in_repo(repo_full_name, keep_going):
    if not keep_going:
        return "skipped", False
    data = send_request(repo_full_name, SEARCH_QUERY_GOOGLE)
    if data.get("total_count", 0) == 0:
        return "no results", True

    # Conto le occorrenze nel codice (opzionale ma più accurato)
    model_arr = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
    for item in data.get("items", []):
        raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            code = requests.get(raw_url, headers=headers).text
            for model in model_arr:
                var = code.count(model)
                if var > 0:
                    return model + "_Gemini", False
        except Exception:
            pass

    return "Other_Gemini", False

def search_grok_in_repo(repo_full_name, keep_going):
    if not keep_going:
        return "skipped", False
    data = send_request(repo_full_name, SEARCH_QUERY_XAI)
    if data.get("total_count", 0) == 0:
        return "no results", True

    # Conto le occorrenze nel codice (opzionale ma più accurato)
    model_arr = [""]
    for item in data.get("items", []):
        raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            code = requests.get(raw_url, headers=headers).text
            for model in model_arr:
                var = code.count(model)
                if var > 0:
                    return model + "_OpenAI", False
        except Exception:
            pass

    return "Other_OpenAI", False


def send_request(repo_full_name, keyword):
    params = {
        "q": f'"{keyword}" repo:{repo_full_name}',

    }
    resp = requests.get(CODE_SEARCH_URL, headers=headers, params=params)

    # Gestione del rate limit
    if resp.status_code == 403:
        reset_time = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
        wait = max(reset_time - time.time(), 1)
        print(f"Rate limit raggiunto. Aspetto {wait:.0f}s...")
        time.sleep(wait)

    if resp.status_code != 200:
        raise IOError(f"Errore {resp.status_code} su {repo_full_name}: {resp.text}")

    data = resp.json()

    return data


# === MAIN SCRIPT ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    repos = json.load(f)

for repo in tqdm(repos, desc="Analisi repository"):
    repo_name = repo["full_name"]
    openai_result, keep_going = search_openai_in_repo(repo_name, True)
    gemini_result, keep_going = search_gemini_in_repo(repo_name,keep_going)
    grok_result, keep_going = search_grok_in_repo(repo_name,keep_going)

    #time.sleep(2)  # per evitare rate limit

# Salvo il nuovo file JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(repos, f, ensure_ascii=False, indent=2)

print(f"\nAnalisi completata. File aggiornato: {OUTPUT_FILE}")
