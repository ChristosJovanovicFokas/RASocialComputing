import os 
import json
import hashlib

def save(content, filename, base_path="data/", subfolder=None, overwrite=True):
    
    if subfolder:
        base_path = os.path.join(base_path, subfolder)
    
    os.makedirs(base_path, exist_ok=True)
    path = os.path.join(base_path, filename)

    #To prevent accidental overwrite of files
    if not overwrite and os.path.exists(path):
        return path
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return path

def append_jsonl(record, path="data/metadata.jsonl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")

    
def make_filename(url, ext = None):
    if ext:
        return hashlib.md5(url.encode()).hexdigest() + str(ext)
    else:
        return hashlib.md5(url.encode()).hexdigest()
