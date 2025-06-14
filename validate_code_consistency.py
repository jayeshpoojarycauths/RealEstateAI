from pathlib import Path
import re

# Define search paths
search_dirs = ["frontend", "app"]

# Define checks
deprecated_roles = ["CUSTOMER"]
old_api_prefix = r"/api/v1/"
hardcoded_base_urls = [r"http://localhost:8000", r"https://.*\.example\.com"]
removed_paths = ["app/api/v1/"]

# File extensions to include
include_exts = [".ts", ".tsx", ".js", ".py", ".env", ".env.example"]

# Compile regex patterns
patterns = {
    "Deprecated Role": [re.compile(rf"\b{role}\b", re.IGNORECASE) for role in deprecated_roles],
    "Old API Endpoint": [re.compile(old_api_prefix)],
    "Hardcoded Base URL": [re.compile(p) for p in hardcoded_base_urls],
    "Removed Path Reference": [re.compile(re.escape(path)) for path in removed_paths],
}

# Gather results
results = []

for search_dir in search_dirs:
    base_path = Path.cwd()  # or use environment variable
    root = base_path / search_dir
    if not root.exists():
        continue
    for file_path in root.rglob("*"):
        if file_path.suffix not in include_exts:
            continue
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            continue
        for category, checks in patterns.items():
            for pattern in checks:
                for match in pattern.finditer(text):
                    results.append({
        "file": str(file_path.relative_to(base_path)),
                        "category": category,
                        "line": text.count('\n', 0, match.start()) + 1,
                        "snippet": text[match.start():match.end()]
                    })

import pandas as pd
df_results = pd.DataFrame(results)
print("\nCode Consistency Issues:")
print(df_results.to_string())
