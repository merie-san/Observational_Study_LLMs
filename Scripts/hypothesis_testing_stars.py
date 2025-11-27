import json
import numpy as np
from scipy.stats import boxcox, ttest_ind, boxcox_normmax, shapiro

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
stars_python = np.array([d.get("stargazers_count", 0) for d in python_data])
stars_java = np.array([d.get("stargazers_count", 0) for d in java_data])
stars_go = np.array([d.get("stargazers_count", 0) for d in go_data])

# Check if data is normally distributed with the Shapiro-Wilk test
print("===== Shapiro-Wills test =====")
res_python = shapiro(stars_python)
res_java = shapiro(stars_java)
res_go = shapiro(stars_go)

print(f"Shapiro-Wilk test results (python): {res_python.statistic:.4f}, p-value: {res_python.pvalue:.4f}")
print(f"Shapiro-Wilk test results (java): {res_java.statistic:.4f}, p-value: {res_java.pvalue:.4f}")
print(f"Shapiro-Wilk test results (go): {res_go.statistic:.4f}, p-value: {res_go.pvalue:.4f}")

# -----------------------
# Shift by 1 to handle zeros
# -----------------------
stars_python_shifted = stars_python + 1
stars_java_shifted = stars_java + 1
stars_go_shifted = stars_go + 1

# Box-Cox transform
boxcox_python, _ = boxcox(stars_python_shifted)  # type: ignore
boxcox_java, _ = boxcox(stars_java_shifted)  # type: ignore
boxcox_go, _ = boxcox(stars_go_shifted)  # type: ignore

# Compute lambda for reporting
lambda_python = boxcox_normmax(stars_python_shifted)
lambda_java = boxcox_normmax(stars_java_shifted)
lambda_go = boxcox_normmax(stars_go_shifted)

# -----------------------
# Welch two-sample t-tests (one-sided)
# -----------------------
# Python < Java
t_java, p_java = ttest_ind(
    boxcox_python, boxcox_java, equal_var=False, alternative="less"
)
# Python < Go
t_go, p_go = ttest_ind(boxcox_python, boxcox_go, equal_var=False, alternative="less")

# -----------------------
# Print results
# -----------------------
print("\n===== Sample Means (Raw) =====")
print(
    f"Python mean stars : {stars_python.mean():.2f}, Python std stars {stars_python.std(ddof=1):.2f}"
)
print(
    f"Java mean stars   : {stars_java.mean():.2f}, Java std stars {stars_java.std(ddof=1):.2f}"
)
print(f"Go mean stars     : {stars_go.mean():.2f}, Go std stars {stars_go.std(ddof=1):.2f}")
print("\n===== Box-Cox Transformation =====")
print(f"Python lambda    : {lambda_python:.4f}, mean: {boxcox_python.mean():.3f}, std: {boxcox_python.std(ddof=1):.3f}")  # type: ignore
print(f"Java lambda      : {lambda_java:.4f}, mean: {boxcox_java.mean():.3f}, std: {boxcox_java.std(ddof=1):.3f}")  # type: ignore
print(f"Go lambda        : {lambda_go:.4f}, mean: {boxcox_go.mean():.3f}, std: {boxcox_go.std(ddof=1):.3f}")  # type: ignore

print("\n===== Welch Two-Sample Tests =====")
print("Python vs Java:")
print(f"  t-statistic  : {t_java:.4f}")
print(f"  p-value (one-sided, Python < Java): {p_java:.6f}")

print("\nPython vs Go:")
print(f"  t-statistic  : {t_go:.4f}")
print(f"  p-value (one-sided, Python < Go): {p_go:.6f}")
