import json
import sys
import numpy as np
from scipy.stats import ttest_ind, anderson, mannwhitneyu

# -----------------------
# Load datasets
# -----------------------
with open("Data/sampled_repo_python.json") as f:
    python_data = json.load(f)
with open("Data/sampled_repo_java.json") as f:
    java_data = json.load(f)
with open("Data/sampled_repo_go.json") as f:
    go_data = json.load(f)

# Extract star counts
size_python = np.array([d.get("size", 0) for d in python_data])
size_java = np.array([d.get("size", 0) for d in java_data])
size_go = np.array([d.get("size", 0) for d in go_data])

if len(size_python) != 500 or len(size_java) != 500 or len(size_go) != 500:
    print("number of samples is not 500")
    sys.exit(0)

# Check if data is normally distributed with the Anderson-Darling test
print("===== Anderson-Darling test =====")
res_python = anderson(size_python)
res_java = anderson(size_java)
res_go = anderson(size_go)

print(
    f"Anderson-Darling test results (python): {res_python.statistic:.4f}, critical value for significance level of {res_python.significance_level[2]}% : {res_python.critical_values[2]:.6f}"
)
print(
    f"Anderson-Darling test results (java): {res_java.statistic:.4f}, critical value for significance level of {res_java.significance_level[2]}% : {res_java.critical_values[2]:.6f}"
)
print(
    f"Anderson-Darling test results (go): {res_go.statistic:.4f}, critical value for significance level of {res_go.significance_level[2]}% : {res_go.critical_values[2]:.6f}"
)

# -----------------------
# Mann–Whitney U tests (one-sided)
# -----------------------
# Python < Java  → alternative="less" means Python distribution is stochastically smaller
u_java, p_java = mannwhitneyu(size_python, size_java, alternative="less")

# Python < Go
u_go, p_go = mannwhitneyu(size_python, size_go, alternative="less")

# -----------------------
# Print results
# -----------------------
print("\n===== Sample Means =====")
print(
    f"Python mean size : {size_python.mean():.2f}, Python std size {size_python.std(ddof=1):.2f}"
)
print(
    f"Java mean size   : {size_java.mean():.2f}, Java std size {size_java.std(ddof=1):.2f}"
)
print(f"Go mean size     : {size_go.mean():.2f}, Go std size {size_go.std(ddof=1):.2f}")

print("\n===== Mann–Whitney U Tests =====")
print("Python vs Java:")
print(f"  U-statistic  : {u_java:.4f}")
print(f"  p-value (one-sided, Python < Java): {p_java:.6f}")

print("\nPython vs Go:")
print(f"  U-statistic  : {u_go:.4f}")
print(f"  p-value (one-sided, Python < Go): {p_go:.6f}")
