import json
import os
import requests
from tqdm import tqdm
import time

SEARCH_QUERY_OPENAI = "import OpenAI"
SEARCH_QUERY_GOOGLE = "from google import genai"
SEARCH_QUERY_XAI = "from xai_sdk import Client"
INPUT_FILE = "repo_metadata.json"
OUTPUT_FILE = "repo_metadata_with_openai.json"
CODE_SEARCH_URL = "https://api.github.com/search/code"

# === HEADER AUTENTICAZIONE ===
headers = {
    "Authorization": f"Bearer {os.getenv("GITHUB_TOKEN")}",
    "Accept": "application/vnd.github.v3+json"
}

def search_openai_in_repo(repo_full_name):
    params = {
        "q": f'"{SEARCH_QUERY_OPENAI}" repo:{repo_full_name}'
    }
    resp = requests.get(CODE_SEARCH_URL, headers=headers, params=params)

    # Gestione del rate limit
    if resp.status_code == 403 and "X-RateLimit-Remaining" in resp.headers and resp.headers["X-RateLimit-Remaining"] == "0":
        reset_time = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
        wait = reset_time - time.time() + 5
        print(f"Rate limit raggiunto. Aspetto {wait:.0f}s...")
        time.sleep(wait)
        return search_openai_in_repo(repo_full_name)

    if resp.status_code != 200:
        print(f"Errore {resp.status_code} su {repo_full_name}: {resp.text}")
        return 0, 0

    data = resp.json()
    total_files = data.get("total_count", 0)
    total_occurrences = 0

    # Conto le occorrenze nel codice (opzionale ma più accurato)
    for item in data.get("items", []):
        raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            code = requests.get(raw_url, headers=headers).text
            total_occurrences += code.count("from google import genai")
        except Exception:
            pass

    return total_files, total_occurrences

def search_gemini_in_repo(repo_full_name):
    params = {
        "q": f'"{SEARCH_QUERY_GOOGLE}" repo:{repo_full_name}'
    }
    resp = requests.get(CODE_SEARCH_URL, headers=headers, params=params)

    # Gestione del rate limit
    if resp.status_code == 403 and "X-RateLimit-Remaining" in resp.headers and resp.headers["X-RateLimit-Remaining"] == "0":
        reset_time = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
        wait = reset_time - time.time() + 5
        print(f"Rate limit raggiunto. Aspetto {wait:.0f}s...")
        time.sleep(wait)
        return search_openai_in_repo(repo_full_name)

    if resp.status_code != 200:
        print(f"Errore {resp.status_code} su {repo_full_name}: {resp.text}")
        return 0, 0

    data = resp.json()
    total_files = data.get("total_count", 0)
    total_occurrences = 0

    # Conto le occorrenze nel codice (opzionale ma più accurato)
    for item in data.get("items", []):
        raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            code = requests.get(raw_url, headers=headers).text
            total_occurrences += code.count("import OpenAI")
        except Exception:
            pass

    return total_files, total_occurrences


# === MAIN SCRIPT ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    repos = json.load(f)

for repo in tqdm(repos, desc="Analisi repository"):
    repo_name = repo["full_name"]
    files_count, occurrences = search_openai_in_repo(repo_name)
    repo["openai_import_files"] = files_count
    repo["openai_import_count"] = occurrences
    #time.sleep(2)  # per evitare rate limit

# Salvo il nuovo file JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(repos, f, ensure_ascii=False, indent=2)

print(f"\nAnalisi completata. File aggiornato: {OUTPUT_FILE}")
