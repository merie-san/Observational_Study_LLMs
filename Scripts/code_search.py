import json
import os
import requests
from tqdm import tqdm
from openai import OpenAI
import time

SEARCH_QUERY_OPENAI = "import OpenAI"
SEARCH_QUERY_GOOGLE = "from google import genai"
SEARCH_QUERY_XAI = "from xai_sdk"
INPUT_FILE = "repo_metadata.json"
OUTPUT_FILE = "repo_metadata_with_openai.json"
CODE_SEARCH_URL = "https://api.github.com/search/code"

keyword_list = ["import OpenAI", "from google import genai", "from xai_sdk import Client"]


headers = {
    "Authorization": f"Bearer {os.getenv("GITHUB_TOKEN")}",
    "Accept": "application/vnd.github.v3+json"
}

client = OpenAI(
    api_key =  os.getenv("OPENAI_API_KEY")
)
openai_models = client.models.list()

def search_openai():
    data = send_request(SEARCH_QUERY_OPENAI)
    #print(data)
    if data.get("total_count", 0) == 0:
        return "no results", True, "none"

    model_arr = ["deepseekchat", "grok-4", "Llama-4-Maverick-17B-128E-Instruct-FP8", "Llama-4-Scout-17B-16E-Instruct-FP8"]
    for model in openai_models:
        model_arr.append(model.id)

    for item in data.get("items", []):
        raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            code = requests.get(raw_url, headers=headers).text
            for model in model_arr:
                var = code.count(model)
                if var > 0:
                    data["model"] = model + "_OpenAI"
                    return model + "_OpenAI", False, data
        except Exception:
            pass
    data["model"] = "Other_OpenAI"
    return "Other_OpenAI", False, data

def search_gemini():
    data = send_request(SEARCH_QUERY_GOOGLE)
    if data.get("total_count", 0) == 0:
        return "no results", True, "none"

    model_arr = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-2.0-flash-lite"]
    for item in data.get("items", []):
        raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            code = requests.get(raw_url, headers=headers).text
            for model in model_arr:
                var = code.count(model)
                if var > 0:
                    data["model"] = model + "_Gemini"
                    return model + "_Gemini", False, data
        except Exception:
            pass
    data["model"] = "Other_Gemini"
    return "Other_Gemini", False, data

def search_grok():
    data = send_request(SEARCH_QUERY_XAI)
    if data.get("total_count", 0) == 0:
        return "no results", True, "none"

    model_arr = ["grok-code-fast-1", "grok-4-fast-reasoning", "grok-4-fast-non-reasoning", "grok-4-0709", "grok-3-mini", "grok-3", "grok-2-vision-1212", "grok-2-image-1212"]
    for item in data.get("items", []):
        raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        try:
            code = requests.get(raw_url, headers=headers).text
            for model in model_arr:
                var = code.count(model)
                if var > 0:
                    data["model"] = model + "_Grok"
                    return model + "_xAI", False, data
        except Exception:
            pass
    data["model"] = "Other_Grok"
    return "Other_xAI", False, data


def send_request(keyword):
    params = {
        "q": f"{keyword} language:Python",
        "sort": "stars",
        "order": "desc",
        "per_page": 10,
        "page": 5,
    }

    i = 1
    while True:
        resp = requests.get(CODE_SEARCH_URL, headers=headers, params=params)

        # Se tutto ok, ritorna i dati
        if resp.status_code == 200:
            print(resp.text)
            return resp.json()

        # Se rate limit superato
        if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
            reset_timestamp = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_time = reset_timestamp - time.time() + 5  # margine 5 secondi
            sleep_time = max(sleep_time, 0)
            print(f"Rate limit raggiunto, attendo {sleep_time:.0f} secondi... (tentativo #{i})")
            time.sleep(sleep_time)
            i += 1
            continue

    print(f"Errore inatteso: {resp.status_code}")
    resp.raise_for_status()


# === MAIN SCRIPT ===
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

arr = []

#data.extend(repos)  # aggiunge i nuovi elementi

openai_result, keep_going, repo_data_o = search_openai()
print(f"model: {openai_result} - {keep_going}")
#data.extend(repo_data)
arr.append(repo_data_o)

if keep_going == True:
    gemini_result, keep_going, repo_data_ge = search_gemini()
    print(f"model: {openai_result} - {keep_going}")
    #data.extend(repo_data)
    arr.append(repo_data_ge)

if keep_going == True:
    grok_result, keep_going, repo_data_gr = search_grok()
    print(f"model: {grok_result} - {keep_going}")
    #data.extend(repo_data)
    arr.append(repo_data_gr)

time.sleep(1)  # per evitare rate limit

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(arr, f, ensure_ascii=False, indent=2)
print(f"\nAnalisi completata. File aggiornato: {OUTPUT_FILE}")
