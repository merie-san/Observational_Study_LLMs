import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import datetime

KEYWORD_LIST = [
    "llm",
    "ai",
    "llama",
    "gemini",
    "claude",
    "grok",
    "mistral",
    "gemma",
    "natural-language-processing",
    "nlp",
    "agent",
    "mcp",
    "ai-agents",
    "ai-tools",
    "multi-agent",
    "large-language-models",
    "artificial-intelligence",
    "openai",
    "transformer",
    "gpt",
    "chatgpt",
    "chat-gpt",
    "chatgpt3",
    "chatgpt4",
    "metagpt",
    "kimi",
    "open-ai",
    "agents",
    "autonomous-agents",
    "transformers",
    "devin",
    "trae",
    "stable-diffusion",
    "codegen",
    "code-generation",
    "copilot",
    "assistant",
    "chatbot",
    "agi",
    "rag",
]


def monthly_llm_ratio_graph(language: str) -> tuple[list[int], list[int]]:
    """Collect the proportion of LLM-related project by month"""
    llm_projects = {}
    projects = {}
    with open(f"Data/{language}_repo_metadata.json", "r") as f:
        data_dicts = json.load(f)
        for i in range(len(data_dicts)):
            month_key = datetime.fromisoformat(data_dicts[i]["created_at"]).strftime(
                "%Y-%m"
            )
            if any(
                (topic in (data_dicts[i]["topics"] or []))
                or (topic in (data_dicts[i]["description"] or "").lower())
                or (topic in (data_dicts[i]["name"] or "").lower())
                for topic in KEYWORD_LIST
            ):
                llm_projects[month_key] = llm_projects.get(month_key, 0) + 1
            projects[month_key] = projects.get(month_key, 0) + 1

    months = sorted(projects.keys())
    projects_n = [projects[m] for m in months]
    llm_projects_n = [llm_projects.get(m, 0) for m in months]
    llm_fraction = [llm_projects.get(m, 0) / projects[m] for m in months]
    other_fraction = [1 - x for x in llm_fraction]

    x = np.arange(len(months))
    plt.figure(figsize=(12, 6))
    plt.bar(x, llm_fraction, color="skyblue", label="LLM-related projects")
    plt.bar(
        x,
        other_fraction,
        bottom=llm_fraction,
        color="lightgray",
        label="Other projects",
    )
    plt.ylim(0, 1)
    plt.xlabel("Month")
    plt.ylabel("Fraction")
    plt.title(f"Fraction of LLM-related GitHub Projects in {language} per Month")
    plt.xticks(x, months, rotation=80)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"../Figures/{language}_llm_fraction.png")

    return projects_n, llm_projects_n


def total_llm_ratio_graph(
    language_list: list[str],
    n_repos_language: list[int],
    n_llm_repo_language: list[int],
):
    """Collect the proportion of LLM-related project by language"""
    llm_repo_ratio_language = [
        n_llm_repo_language[i] / n_repos_language[i] for i in range(len(language_list))
    ]
    other_repo_ratio_language = [1 - llm_ratio for llm_ratio in llm_repo_ratio_language]

    x = np.arange(len(language_list))
    plt.figure(figsize=(12, 6))
    plt.bar(x, llm_repo_ratio_language, color="skyblue", label="LLM-related projects")
    plt.bar(
        x,
        other_repo_ratio_language,
        bottom=llm_repo_ratio_language,
        color="lightgray",
        label="Other projects",
    )
    plt.ylim(0, 1)
    plt.xlabel("Language")
    plt.ylabel("Fraction")
    plt.title(f"Fraction of LLM-related GitHub Projects by Programming Language")
    plt.xticks(x, language_list)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"../Figures/llm_fraction_languages.png")


def popularity_llm_ratio_graph(language: str):
    """Collect the proportion of LLM-related project by number of stars"""
    projects_number = np.zeros(5)
    llm_projects_number = np.zeros(5)
    with open(f"Data/{language}_repo_metadata.json", "r") as f:
        data_dicts = json.load(f)
        max_stars = max(dict["stargazers_count"] for dict in data_dicts)
        min_stars = min(dict["stargazers_count"] for dict in data_dicts)
        intervals = np.linspace(min_stars, max_stars + 1, 6)
        for i in range(len(data_dicts)):
            index = (
                np.searchsorted(
                    intervals, data_dicts[i]["stargazers_count"], side="right"
                )
                - 1
            )
            if any(
                (topic in (data_dicts[i]["topics"] or []))
                or (topic in (data_dicts[i]["description"] or "").lower())
                or (topic in (data_dicts[i]["name"] or "").lower())
                for topic in KEYWORD_LIST
            ):
                llm_projects_number[index] += 1
            projects_number[index] += 1

    x = np.arange(5)
    labels = [
        f"{int(intervals[i])} - {int(intervals[i+1])}"
        for i in range(len(intervals) - 1)
    ]
    llm_ratio = llm_projects_number / np.maximum(projects_number, 1)
    other_ratio = [1 - llm_ratio[i] for i in range(len(llm_ratio))]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(x, llm_ratio, color="skyblue", label="LLM-related projects")
    ax.bar(
        x,
        other_ratio,
        bottom=llm_ratio,
        color="lightgray",
        label="Other projects",
    )
    ax.set_ylabel("Fraction")
    ax.set_ylim(0, 1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=80)
    ax.legend(loc="upper left")

    cum_ratio = np.cumsum(projects_number) / np.sum(projects_number)
    ax2 = ax.twinx()
    ax2.plot(
        x, cum_ratio, color="red", marker="o", label="Cumulative ratio of projects"
    )
    ax2.set_ylabel("Cumulative ratio of projects")
    ax2.legend(loc="upper right")
    plt.title(f"{language} Ratio of LLM-ralated Projects by Number of Stars")
    plt.tight_layout()
    plt.savefig(f"../Figures/{language}_llm_fraction_stars.png")


if __name__ == "__main__":
    ppn, pp_llm_n = monthly_llm_ratio_graph("python")
    jpn, jp_llm_n = monthly_llm_ratio_graph("java")
    cpn, cp_llm_n = monthly_llm_ratio_graph("c#")
    jspn, jsp_llm_n = monthly_llm_ratio_graph("javascript")
    gpn, gp_llm_n = monthly_llm_ratio_graph("go")
    languages = ["python", "java", "c#", "javascript", "go"]
    n_repos = [np.sum(ppn), np.sum(jpn), np.sum(cpn), np.sum(jspn), np.sum(gpn)]
    n_llm_repos = [
        np.sum(pp_llm_n),
        np.sum(jp_llm_n),
        np.sum(cp_llm_n),
        np.sum(jsp_llm_n),
        np.sum(gp_llm_n),
    ]
    total_llm_ratio_graph(languages, n_repos, n_llm_repos)
    popularity_llm_ratio_graph("python")
    popularity_llm_ratio_graph("java")
    popularity_llm_ratio_graph("c#")
    popularity_llm_ratio_graph("javascript")
    popularity_llm_ratio_graph("go")
