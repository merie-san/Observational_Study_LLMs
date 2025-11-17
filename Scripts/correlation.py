import numpy as np
import json
import matplotlib.pyplot as plt


def spearman_corr_heatmap(data_path: str, suffix: str):
    # Load data
    with open(data_path, "r") as f:
        data_list = json.load(f)

    stargazers_counts = []
    open_issues_counts = []
    sizes = []
    subscribers_counts = []
    network_counts = []

    for data in data_list:
        stargazers_counts.append(data.get("stargazers_count", 0))
        open_issues_counts.append(data.get("open_issues_count", 0))
        sizes.append(data.get("size", 0))
        subscribers_counts.append(data.get("subscribers_count", 0))
        network_counts.append(data.get("network_count", 0))

    X = np.column_stack(
        [
            stargazers_counts,
            open_issues_counts,
            sizes,
            subscribers_counts,
            network_counts,
        ]
    )

    # Rank-transform
    ranks = np.apply_along_axis(lambda x: np.argsort(np.argsort(x)), axis=0, arr=X)

    # Spearman correlation
    rho = np.corrcoef(ranks, rowvar=False)

    # Plot heatmap
    attribute_names = [
        "stargazers_count",
        "open_issues_count",
        "size",
        "subscribers_count",
        "network_count",
    ]

    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.matshow(rho, cmap="coolwarm", vmin=-1, vmax=1)

    # Add colorbar
    fig.colorbar(cax)

    # Set ticks and labels
    ax.set_xticks(range(len(attribute_names)))
    ax.set_yticks(range(len(attribute_names)))
    ax.set_xticklabels(attribute_names, rotation=45, ha="left")
    ax.set_yticklabels(attribute_names)

    # Annotate correlation values
    for i in range(len(attribute_names)):
        for j in range(len(attribute_names)):
            ax.text(j, i, f"{rho[i,j]:.2f}", va="center", ha="center", color="black")

    plt.title("Spearman Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(f"../Figures/table_corr_{suffix}")


# Example usage
if __name__ == "__main__":
    spearman_corr_heatmap("Data/sampled_repo_python.json", "python")
    spearman_corr_heatmap("Data/sampled_repo_go.json", "go")
    spearman_corr_heatmap("Data/sampled_repo_java.json", "java")
