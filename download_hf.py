import os
import shutil
from huggingface_hub import hf_hub_download

# --- PUBLIC REPOSITORY DETAILS ---
REPO_ID = "DLSCA/ascad-v1-fk" 

# We will download the main metadata/traces file 
# Most researchers use 'ASCAD_data.h5' for v1-fk, let's grab that!
FILENAME = "ASCAD_data.h5" 
# ---------------------------------

print(f"⏳ Connecting to the official DLSCA repository...")
print(f"Downloading '{FILENAME}'... This is a large file, please wait.")

try:
    # 1. Download the public file (No token required!)
    downloaded_file_path = hf_hub_download(
        repo_id=REPO_ID, 
        filename=FILENAME, 
        repo_type="dataset"
    )

    # 2. Ensure our data folder exists
    os.makedirs("data", exist_ok=True)
    
    # 3. Copy it into our project
    # Note: I'm keeping the .h5 extension since that's what DLSCA uses
    destination = "data/ASCAD_data.h5"
    shutil.copy(downloaded_file_path, destination)

    print(f"✅ Success! Official dataset saved to: {destination}")
    print("Next: We will update our FastAPI server to read this .h5 format.")

except Exception as e:
    print(f"🚨 Error downloading: {e}")