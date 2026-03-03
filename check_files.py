from huggingface_hub import HfApi

print("🔍 Scanning the DLSCA/ascad-v1-fk repository...")
api = HfApi()

# We ask the API to list every single file sitting in this repository
files = api.list_repo_files(repo_id="DLSCA/ascad-v1-fk", repo_type="dataset")

print("\n📂 Here are the exact files inside this dataset:")
for f in files:
    print(f" - {f}")