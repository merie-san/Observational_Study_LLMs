import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import datetime


def show_library_imports(file_path: str, suffix):
    provider_dict = {
        "OpenAI": 0,
        "xAI": 0,
        "Anthropic": 0,
        "Mistral": 0,
        "Google": 0,
        "unknown_lib": 0,
    }
    with open(file_path, "r") as f:
        dicts = json.load(f)
        for dict in dicts:
            for tag in dict["tags"]:
                if "OpenAI" in tag:
                    provider_dict["OpenAI"] += 1
                elif "xAI" in tag:
                    provider_dict["xAI"] += 1
                elif "Anthropic" in tag:
                    provider_dict["Anthropic"] += 1
                elif "Mistral" in tag:
                    provider_dict["Mistral"] += 1
                elif "Google" in tag:
                    provider_dict["Google"] += 1
                elif "unknown_lib" in tag:
                    provider_dict["unknown_lib"] += 1
    labels = ["openai", "anthropic", "mistral", "google", "xai", "other"]
    x = np.arange(len(labels))
    values = [
        provider_dict["OpenAI"],
        provider_dict["Anthropic"],
        provider_dict["Mistral"],
        provider_dict["Google"],
        provider_dict["xAI"],
        provider_dict["unknown_lib"],
    ]
    plt.figure(figsize=(12, 6))
    plt.bar(x, values, color="skyblue", label="Number of repos for each provider")
    plt.yscale("log")
    plt.xlabel("Provider")
    plt.ylabel("Number of repos")
    plt.title(f"Provider of LLM library by number of repos")
    plt.xticks(x, labels)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"../Figures/llm_library_usage_{suffix}.png")
    plt.close()


def show_model_frequency(file_path, suffix):
    models = []
    with open("model_provider_dict.json", "r") as f:
        dict_json = json.load(f)
        models = dict_json.keys()
    model_counts = {}
    for model in models:
        model_counts[model] = 0
    with open(file_path, "r") as f:
        dicts = json.load(f)
        for dict in dicts:
            for tag in dict["tags"]:
                for model in models:
                    if model in tag:
                        model_counts[model] += 1
    count_array = []
    for count in model_counts.values():
        count_array.append(count)
    count_array.sort(reverse=True)
    total_count = np.sum(count_array)
    top_20p = 0
    top_n = int(len(count_array) * 0.2)
    for i in range(top_n):
        top_20p += count_array[i]
    plt.figure(figsize=(12, 6))
    x = np.arange(len(count_array))
    plt.fill_between(x[:top_n], count_array[:top_n], color="orange", alpha=0.3, label="Top 20%")
    plt.plot(x, count_array, color="skyblue", label="number of repo for each model")
    plt.xlabel("Models ordered by how much they are referenced")
    plt.ylabel("Number of repos")
    plt.title(f"LLM Model by number of repos")
    plt.legend()
    plt.text(
        0.95,
        0.95,
        f"Top 20% of models make {top_20p/total_count:.1%} of total usage",
        transform=plt.gca().transAxes,
        ha="right",
        va="top",
        fontsize=12,
    )
    plt.tight_layout()
    num_ticks = 5
    tick_positions = np.linspace(0, len(count_array) - 1, num_ticks, dtype=int)
    tick_labels = [f"Top {pos + 1}" for pos in tick_positions]

    plt.xticks(tick_positions, tick_labels)
    plt.savefig(f"../Figures/llm_model_usage_{suffix}.png")
    plt.close()


if __name__ == "__main__":
    show_library_imports("Data/collected_repos_python.json", "python")
    show_model_frequency("Data/collected_repos_python.json", "python")
    show_library_imports("Data/collected_repos_java.json", "java")
    show_model_frequency("Data/collected_repos_java.json", "java")
    show_library_imports("Data/collected_repos_go.json", "go")
    show_model_frequency("Data/collected_repos_go.json", "go")
