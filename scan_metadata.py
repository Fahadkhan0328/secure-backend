from huggingface_hub import HfApi

print("🔍 Scanning inside the 'metadata' folder...")
api = HfApi()

files = api.list_repo_files(repo_id="DLSCA/ascad-v1-fk", repo_type="dataset")

for f in files:
    # Only print files that are inside the metadata folder
    if f.startswith("metadata/"):
        print(f" - {f}")