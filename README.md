# Observational Study on usage of LLMs in public github projects
Analyze how Large Language Models (LLMs) are used in real-world software projects. This project mines public GitHub repositories to detect which SDKs and models are employed, track adoption trends, and explore relationships with repository characteristics like size and activity.
This project's features:
- Identify popular LLMs and SDK–model combinations.
- Explore application domains and usage trends (2022–2025).
- Gain insights into repository attributes linked to LLM adoption.
- Empirical snapshot of LLM integration in open-source software.
Use this project to understand the evolving landscape of LLM adoption and inform development, tooling, and research decisions.

Order of execution:

keyword_search.py -> list_models.py -> library_model_search.py -> combine.py ->  attribute_search.py -> (graph scripts) -> (statistic scripts)


This project has been made for the Software Architecture Methodologies course of the Università degli Studi di Firenze.
Authors: Davide Zhang, Magrini Roberto.

