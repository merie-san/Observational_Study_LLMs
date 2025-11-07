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
    with open(f"model_counts_{suffix}.json", "w") as f:
        json.dump(model_counts, f)
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
    plt.fill_between(
        x[:top_n], count_array[:top_n], color="orange", alpha=0.3, label="Top 20%"
    )
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


def show_top_models(file_path, suffix):
    with open(file_path, "r") as f:
        model_counts = json.load(f)
        top20 = sorted(model_counts, key=model_counts.get, reverse=True)[:20]
        with open(f"top_20_models_{suffix}.json", "w") as f:
            json.dump(top20, f, indent=2)
        x = np.arange(20)
        labels = top20
        y = [model_counts[model] for model in top20]
        plt.figure(figsize=(12, 6))
        plt.bar(x, y, color="skyblue", label="Number of repos for each model")
        plt.xlabel("Models")
        plt.ylabel("Number of repos")
        plt.title(f"Top 20 models by number of repos")
        plt.xticks(x, labels, rotation=80)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"../Figures/top_models_{suffix}.png")
        plt.close()


def show_library_most_pop_model(file_path_most_pop_models, data, suffix):
    pop_models = []
    data_dicts = []
    with open(file_path_most_pop_models, "r") as f:
        pop_models = json.load(f)
    with open(data, "r") as f:
        data_dicts = json.load(f)
    result_dicts = []
    for dict_value in data_dicts:
        for tag in dict_value["tags"]:
            for model in pop_models:
                if model in tag:
                    result_dicts.append(dict_value)
                    break
    with open(f"Data/reduced_repos_{suffix}.json", "w") as f:
        json.dump(result_dicts, f, indent=2 )

    provider_list = ["OpenAI", "xAI", "Anthropic", "Mistral", "Google", "unknown_lib"]
    count_dict = {}

    for model in pop_models:
        count_dict[model] = {provider: 0 for provider in provider_list}
        count_dict[model]["tot"] = 0

    for dict_value in result_dicts:
        provider_encountered = []
        models_encountered = []
        for tag in dict_value["tags"]:
            if "_" in tag:
                res = tag.split("_")
                if res[1] in pop_models:
                    count_dict[res[1]]["tot"] += 1
                    count_dict[res[1]][res[0]] += 1
            else:
                if tag in provider_list:
                    provider_encountered.append(tag)
                if tag in pop_models:
                    models_encountered.append(tag)
        if models_encountered and len(provider_encountered) == 1:
            for model in models_encountered:
                count_dict[model]["tot"] += 1
                count_dict[model][provider_encountered[0]] += 1

    ratios = {provider: [] for provider in provider_list}

    for model in pop_models:
        counts = count_dict[model]
        total = count_dict[model]["tot"]
        if total == 0:
            total = 1
        for provider in provider_list:
            ratios[provider].append(counts[provider] / total)

    x = np.arange(len(pop_models))
    bottom = np.zeros(len(pop_models))

    plt.figure(figsize=(14, 6))

    color_list = ["skyblue", "limegreen", "tomato", "c", "m", "0.5"]

    for i in range(len(provider_list)):
        plt.bar(
            x,
            ratios[provider_list[i]],
            bottom=bottom,
            label=provider_list[i],
            color=color_list[i],
        )
        bottom += np.array(ratios[provider_list[i]])

    plt.xticks(x, pop_models, rotation=80)
    plt.yticks(np.linspace(0, 1, 6))
    plt.ylim(0, 1)
    plt.ylabel("Proportion of Provider in most popular models")
    plt.title("Provider Ratios per Model (Normalized)")
    plt.legend(title="Provider", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(f"../Figures/top_models_prop_{suffix}.png")
    plt.close()


if __name__ == "__main__":
    show_library_imports("Data/collected_repos_python.json", "python")
    show_model_frequency("Data/collected_repos_python.json", "python")
    show_library_imports("Data/collected_repos_java.json", "java")
    show_model_frequency("Data/collected_repos_java.json", "java")
    show_library_imports("Data/collected_repos_go.json", "go")
    show_model_frequency("Data/collected_repos_go.json", "go")
    show_top_models("model_counts_python.json", "python")
    show_top_models("model_counts_java.json", "java")
    show_top_models("model_counts_go.json", "go")
    show_library_most_pop_model(
        "top_20_models_python.json", "Data/collected_repos_python.json", "python"
    )
    show_library_most_pop_model(
        "top_20_models_java.json", "Data/collected_repos_java.json", "java"
    )
    show_library_most_pop_model(
        "top_20_models_go.json", "Data/collected_repos_go.json", "go"
    )
