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
    with open(f"Data/{language.lower()}_repo_metadata.json", "r") as f:
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
    plt.savefig(f"../Figures/{language.lower()}_llm_fraction.png")
    plt.close()

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
    plt.close()


def llm_ratio_graph(language: str, metric: str):
    """Collect the proportion of LLM-related project by number of stars"""
    projects_number = np.zeros(7)
    llm_projects_number = np.zeros(7)
    with open(f"Data/{language.lower()}_repo_metadata.json", "r") as f:
        data_dicts = json.load(f)
        max_stars = max(dict[metric] for dict in data_dicts)
        min_stars = min(dict[metric] for dict in data_dicts)
        intervals = np.linspace(0, 1, 8) ** 4
        intervals = intervals * (max_stars + 1 - min_stars) + min_stars
        for i in range(len(data_dicts)):
            index = np.searchsorted(intervals, data_dicts[i][metric], side="right") - 1
            if any(
                (topic in (data_dicts[i]["topics"] or []))
                or (topic in (data_dicts[i]["description"] or "").lower())
                or (topic in (data_dicts[i]["name"] or "").lower())
                for topic in KEYWORD_LIST
            ):
                llm_projects_number[index] += 1
            projects_number[index] += 1

    x = np.arange(7)
    labels = [
        f"{int(intervals[i])} - {int(intervals[i+1])}"
        for i in range(len(intervals) - 1)
    ]
    llm_ratio = llm_projects_number / np.maximum(projects_number, 1)
    other_ratio = [1 - llm_ratio[i] for i in range(len(llm_ratio))]

    _, ax = plt.subplots(figsize=(12, 6))

    ax.bar(x, llm_ratio, color="skyblue", label="LLM-related projects")
    ax.bar(
        x,
        other_ratio,
        bottom=llm_ratio,
        color="lightgray",
        label="Other projects",
    )
    ax.set_ylabel("Fraction")
    ax.set_xlabel(metric.capitalize())
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
    plt.title(f"Ratio of LLM-related Projects in {language} by {metric.capitalize()}")
    plt.tight_layout()
    plt.savefig(f"../Figures/{language.lower()}_llm_{metric}.png")
    plt.close()


def corr_and_fit(x, y):
    corr = np.corrcoef(x, y)[0, 1]
    try:
        slope, intercept = np.polyfit(x, y, 1)
        fit_x = np.linspace(x.min(), x.max(), 2)
        fit_y = slope * fit_x + intercept
    except Exception:
        fit_x, fit_y = np.array([]), np.array([])
    return corr, fit_x, fit_y


def correlation_analysis(language: str, data_dir="Data", output_dir="../Figures"):
    """
    Correlate stargazer_count with watchers_count and forks_count,
    and generate scatter plots with linear fit lines.
    """

    stars, forks, subscribers = [], [], []
    with open(f"Data/{language.lower()}_repo_metadata.json", "r") as f:
        data = json.load(f)
        for repo in data:
            stars_v = repo.get("stargazers_count")
            forks_v = repo.get("network_count")
            subscribers_v = repo.get("subscribers_count")
            if None in (stars_v, forks_v, subscribers_v):
                continue
            stars.append(stars_v)
            forks.append(forks_v)
            subscribers.append(subscribers_v)

    stars_np = np.array(stars)
    forks_np = np.array(forks)
    subs_np = np.array(subscribers)

    # Compute correlations and fit lines
    corr_star_fork, fitx_star_fork, fity_star_fork = corr_and_fit(stars_np, forks_np)
    corr_star_sub, fitx_star_sub, fity_star_sub = corr_and_fit(stars_np, subs_np)
    corr_sub_fork, fitx_sub_fork, fity_sub_fork = corr_and_fit(subs_np, forks_np)

    # Plot results
    fig, axs = plt.subplots(3, 1, figsize=(12, 8))
    fig.suptitle(
        f"Correlation Analysis for {language.capitalize()} Repositories",
        fontsize=16,
        weight="bold",
    )

    plot_data = [
        (
            axs[0],
            stars_np,
            forks_np,
            fitx_star_fork,
            fity_star_fork,
            "Number of Stars",
            "Network Count (Forks)",
            corr_star_fork,
        ),
        (
            axs[1],
            stars_np,
            subs_np,
            fitx_star_sub,
            fity_star_sub,
            "Number of Stars",
            "Number of Subscribers (Watchers)",
            corr_star_sub,
        ),
        (
            axs[2],
            subs_np,
            forks_np,
            fitx_sub_fork,
            fity_sub_fork,
            "Number of Subscribers (Watchers)",
            "Network Count (Forks)",
            corr_sub_fork,
        ),
    ]

    for ax, x, y, fx, fy, xlabel, ylabel, corr in plot_data:
        # Scatter + fit
        ax.scatter(x, y, alpha=0.6, edgecolor="k", linewidths=0.3)
        if corr > 0.5 or corr < -0.5:
            ax.plot(fx, fy, color="red")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(f"{ylabel} vs {xlabel}", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.text(
            0.95,
            0.05,
            f"Pearson r = {corr:.3f}" if not np.isnan(corr) else "Pearson r = N/A",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.6),
        )

    plt.tight_layout()
    plt.savefig(f"../Figures/{language.lower()}_correlation_analysis.png")
    plt.close()


if __name__ == "__main__":
    ppn, pp_llm_n = monthly_llm_ratio_graph("Python")
    jpn, jp_llm_n = monthly_llm_ratio_graph("Java")
    cpn, cp_llm_n = monthly_llm_ratio_graph("C#")
    jspn, jsp_llm_n = monthly_llm_ratio_graph("Javascript")
    gpn, gp_llm_n = monthly_llm_ratio_graph("Go")
    languages = ["Python", "Java", "C#", "Javascript", "Go"]
    n_repos = [np.sum(ppn), np.sum(jpn), np.sum(cpn), np.sum(jspn), np.sum(gpn)]
    n_llm_repos = [
        np.sum(pp_llm_n),
        np.sum(jp_llm_n),
        np.sum(cp_llm_n),
        np.sum(jsp_llm_n),
        np.sum(gp_llm_n),
    ]
    total_llm_ratio_graph(languages, n_repos, n_llm_repos)
    llm_ratio_graph("Python", "stargazers_count")
    llm_ratio_graph("Java", "stargazers_count")
    llm_ratio_graph("C#", "stargazers_count")
    llm_ratio_graph("Javascript", "stargazers_count")
    llm_ratio_graph("Go", "stargazers_count")
    llm_ratio_graph("Python", "size")
    llm_ratio_graph("Java", "size")
    llm_ratio_graph("C#", "size")
    llm_ratio_graph("Javascript", "size")
    llm_ratio_graph("Go", "size")

    correlation_analysis("Python")
    correlation_analysis("Java")
    correlation_analysis("C#")
    correlation_analysis("Javascript")
    correlation_analysis("Go")
