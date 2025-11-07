import json
from mine import repo


def combine(
    library_data_path: str,
    model_data_path: str,
    output_path: str,
    model_library_map: dict[str, list[str]],
):

    repos_with_llm_library_dict = {
        repo_lib["full_name"]: repo.from_dict(repo_lib)
        for repo_lib in json.load(open(library_data_path, "r", encoding="utf-8"))
    }
    repos_with_llm_model_dict = {
        repo_mod["full_name"]: repo.from_dict(repo_mod)
        for repo_mod in json.load(open(model_data_path, "r", encoding="utf-8"))
    }

    repos_with_llm_library_set = set(repos_with_llm_library_dict.keys())
    repos_with_llm_model_set = set(repos_with_llm_model_dict.keys())

    possible_repos_with_library_and_model_set = repos_with_llm_library_set.intersection(
        repos_with_llm_model_set
    )
    repos_with_library_but_no_model_set = repos_with_llm_library_set.difference(
        repos_with_llm_model_set
    )
    repos_with_model_but_no_library_set = repos_with_llm_model_set.difference(
        repos_with_llm_library_set
    )

    combined_repos = []
    for repo_name in possible_repos_with_library_and_model_set:
        repo_lib_side = repos_with_llm_library_dict[repo_name]
        repo_mod_side = repos_with_llm_model_dict[repo_name]
        combined_repo = {
            "fullname": repo_name,
            "html_url": repo_lib_side.html_url,
            "tags": [],
        }

        for model, model_files in repo_mod_side.labels.items():

            if model not in model_library_map:
                continue
            possible_libraries = model_library_map[model]
            if not isinstance(possible_libraries, list):
                raise ValueError(
                    f"model_library_map[{model}] should be a list, got {type(possible_libraries)}"
                )

            for lib in possible_libraries:
                if lib in repo_lib_side.labels:
                    if model_files.intersection(repo_lib_side.labels[lib]):
                        combined_repo["tags"].append(f"{lib}_{model}")
                        print(
                            f"Added repo {repo_name} with lib-model pair: {lib}-{model}"
                        )
                        break

        if combined_repo["tags"]:
            combined_repos.append(combined_repo)
        else:
            combined_repo["tags"] = [
                f"{lib}" for lib in repo_lib_side.labels.keys()
            ] + [f"{model}" for model in repo_mod_side.labels.keys()]
            combined_repos.append(combined_repo)
            print(f"Added repo with lib and model in different files: {repo_name}")

    for repo_name in repos_with_library_but_no_model_set:
        repo_lib_side = repos_with_llm_library_dict[repo_name]
        combined_repo = {
            "fullname": repo_name,
            "html_url": repo_lib_side.html_url,
            "tags": [],
        }
        combined_repo["tags"] += [
            f"{lib}_unknown_model" for lib in repo_lib_side.labels.keys()
        ]
        combined_repos.append(combined_repo)
        print(f"Added repo with lib but no model: {repo_name}")

    for repo_name in repos_with_model_but_no_library_set:
        repo_model_side = repos_with_llm_model_dict[repo_name]
        combined_repo = {
            "fullname": repo_name,
            "html_url": repo_model_side.html_url,
            "tags": [],
        }
        combined_repo["tags"] += [
            f"unknown_lib_{model}" for model in repo_model_side.labels.keys()
        ]
        combined_repos.append(combined_repo)
        print(f"Added repo with model but no lib: {repo_name}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined_repos, f, indent=2)


if __name__ == "__main__":
    with open("model_provider_dict.json", "r") as f:
        model_library_map = json.load(f)
        combine(
            library_data_path="Data/collected_repos_java_library.json",
            model_data_path="Data/collected_repos_java_model.json",
            output_path="Data/collected_repos_java.json",
            model_library_map=model_library_map,
        )
        combine(
            library_data_path="Data/collected_repos_go_library.json",
            model_data_path="Data/collected_repos_go_model.json",
            output_path="Data/collected_repos_go.json",
            model_library_map=model_library_map,
        )
