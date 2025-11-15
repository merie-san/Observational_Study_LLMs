import matplotlib.pyplot as plt
import json

CONVERSATIONAL_AGENTS_KEYWORDS = [
    "assistant",
    "q&a",
    "chat",
    "helpdesk",
    "dialog",
    "conversation",
    "memory-enabled",
    "chatbot",
    "bot",
    "support agent",
    "customer service",
    "virtual agent",
    "voice assistant",
    "interactive",
    "persona",
    "roleplay",
    "prompt-based dialogue",
]

GENERATION_AGENTS_KEYWORDS = [
    "generation",
    "text",
    "code",
    "content",
    "story",
    "article",
    "completion",
    "summarization",
    "synthesis",
    "copilot",
    "creative",
    "llm generation",
    "code generation",
    "writing",
    "document generation",
    "template-based",
    "drafting",
    "ideation",
    "translation",
    "paraphrase",
]

RETRIEVAL_AUGMENTED_AGENTS_KEYWORDS = [
    "retrieval-augmented generation",
    "rag",
    "qa",
    "question answering",
    "external knowledge",
    "information retrieval",
    "vector search",
    "knowledge augmented",
    "embedding",
    "semantic search",
    "indexing",
    "chunking",
    "document retrieval",
    "context retrieval",
    "knowledge base",
    "rag pipeline",
    "retriever",
    "hybrid search",
]

AGENTIC_ORCHESTRATION_KEYWORDS = [
    "agent",
    "workflow",
    "automation",
    "tool-using",
    "chain-of-thought",
    "planning",
    "task",
    "auto-gpt",
    "orchestration",
    "orchestrator",
    "decision-making",
    "api-calling",
    "tool calling",
    "function calling",
    "multi-agent",
    "task planning",
    "autonomous",
    "scheduling",
    "agent framework",
    "langgraph",
    "swarm",
    "agentic",
]

MULTIMODAL_KEYWORDS = [
    "multimodal",
    "image",
    "captioning",
    "audio",
    "transcription",
    "video",
    "speech",
    "vision",
    "cross-modal",
    "multimodal reasoning",
    "ocr",
    "asr",
    "tts",
    "image generation",
    "voice",
    "sound",
    "embedding vision",
    "document vision",
]

DOMAIN_SPECIFIC_KEYWORDS = [
    "legal",
    "medical",
    "healthcare",
    "financial",
    "educational",
    "domain-specific",
    "scientific",
    "industry",
    "enterprise",
    "sector-specific",
    "research",
    "biomedical",
    "clinical",
    "fintech",
    "banking",
    "insurance",
    "pharma",
    "chemistry",
    "physics",
    "biology",
    "math",
    "education",
    "tutoring",
]


CATEGORY_KEYWORDS = {
    "Conversational Agents": CONVERSATIONAL_AGENTS_KEYWORDS,
    "Generation Agents": GENERATION_AGENTS_KEYWORDS,
    "Retrieval-Augmented": RETRIEVAL_AUGMENTED_AGENTS_KEYWORDS,
    "Agentic Orchestration": AGENTIC_ORCHESTRATION_KEYWORDS,
    "Multimodal": MULTIMODAL_KEYWORDS,
    "Domain-Specific": DOMAIN_SPECIFIC_KEYWORDS,
}


def category_llm_proportion_graph(data_path: str, language: str):
    """Compute proportions of GitHub repos per LLM usage category and plot a bar chart with unclassified repos"""
    category_counts = {cat: 0 for cat in CATEGORY_KEYWORDS.keys()}
    total_repos = 0
    unclassified_count = 0

    # Load repo metadata
    with open(data_path, "r") as f:
        data_dicts = json.load(f)

    total_repos = len(data_dicts)

    # Count repos per category
    for repo in data_dicts:
        repo_text = " ".join(
            [
                (repo.get("name") or "").lower(),
                (repo.get("description") or "").lower(),
                " ".join(repo.get("topics") or []).lower(),
            ]
        )
        matched = False
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword.lower() in repo_text for keyword in keywords):
                category_counts[category] += 1
                matched = True
        if not matched:
            unclassified_count += 1

    # Compute proportions
    proportions = [count / total_repos for count in category_counts.values()]
    categories = list(category_counts.keys())
    categories.append("Unclassified")
    proportions.append(unclassified_count / total_repos)

    # Plot bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(categories, proportions, color="skyblue")
    plt.xlabel("LLM Usage Category")
    plt.ylabel("Proportion of Repositories")
    plt.title(
        f"Proportion of LLM-Related GitHub Repositories by Category in {language}"
    )
    plt.xticks(rotation=45, ha="right")

    # Annotate bars
    for bar, prop in zip(bars, proportions):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{prop:.2f}",
            ha="center",
            va="bottom",
        )

    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(f"../Figures/{language.lower()}_llm_category_proportions.png")
    plt.close()


if __name__ == "__main__":
    category_llm_proportion_graph("Data/sampled_repo_python.json", "python")
    category_llm_proportion_graph("Data/sampled_repo_go.json", "go")
    category_llm_proportion_graph("Data/sampled_repo_java.json", "java")
