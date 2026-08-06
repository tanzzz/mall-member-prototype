import base64
import os
import requests
import json
import time

TOKEN = "YOUR_GITHUB_TOKEN_HERE"
REPO = "tanzzz/mall-member-prototype"
API = f"https://api.github.com/repos/{REPO}/contents"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def upload_file(filepath, repo_path, commit_msg):
    with open(filepath, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    
    data = {
        "message": commit_msg,
        "content": content,
        "branch": "main"
    }
    
    # Check if file exists (get sha)
    resp = requests.get(f"{API}/{repo_path}", headers=HEADERS)
    if resp.status_code == 200:
        data["sha"] = resp.json()["sha"]
    
    resp = requests.put(f"{API}/{repo_path}", headers=HEADERS, json=data)
    if resp.status_code in [200, 201]:
        print(f"  ✓ {repo_path}")
        return True
    else:
        print(f"  ✗ {repo_path}: {resp.status_code} {resp.text[:100]}")
        return False

# First, create an initial commit with a .gitattributes if repo is empty
print("Checking repo state...")
resp = requests.get(f"https://api.github.com/repos/{REPO}/git/refs/heads/main", headers=HEADERS)
if resp.status_code != 200:
    # Need to create initial commit
    print("Creating initial commit...")
    # Create a dummy file to initialize the repo
    upload_file_flag = False
else:
    print("Repo has existing commits, proceeding with upload...")

# Collect all files
files_to_upload = []
base_dir = os.path.dirname(os.path.abspath(__file__))

for root, dirs, filenames in os.walk(base_dir):
    # Skip .git directory and this script
    dirs[:] = [d for d in dirs if d != '.git']
    for fn in filenames:
        if fn == 'upload_to_github.py':
            continue
        full_path = os.path.join(root, fn)
        rel_path = os.path.relpath(full_path, base_dir).replace('\\', '/')
        files_to_upload.append((full_path, rel_path))

print(f"Uploading {len(files_to_upload)} files to {REPO}...")
success = 0
for full_path, rel_path in files_to_upload:
    if upload_file(full_path, rel_path, f"Add {rel_path}"):
        success += 1
    time.sleep(0.5)  # Rate limiting

print(f"\nDone! {success}/{len(files_to_upload)} files uploaded successfully.")
if success == len(files_to_upload):
    print(f"\nGitHub Pages URL: https://tanzzz.github.io/mall-member-prototype/")
    print(f"Remember to enable GitHub Pages in repo Settings > Pages > Source: Deploy from branch > main")