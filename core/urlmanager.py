import json

class URLManager:
    def __init__(self):
        self.urls = []

        self.completed_urls = set()

        records = []
        with open("data/metadata.jsonl", "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                record = json.loads(line)
                for record in records:
                    if record["status"] == "success":
                        self.completed_urls.add(record["url"])
                        print(record["url"])
                        print(record["status"])


    def add(self, url, url_type, depth=0):

        if url in self.completed_urls:
            print("in the meta")
            return 
        self.urls.append({
            "url": url,
            "url_type": url_type,
            "status": "pending",
            "retries": 0,
            "depth": depth,
            "last_error": None,
            "html": None
        })

    def get_pending(self):
        return [u for u in self.urls if u["status"] == "pending"]
    
    def get_success(self):
        return [u for u in self.urls if u["status"] == "success"]
    
    def get_failed(self):
        return [u for u in self.urls if u["status"] == "failed"]

    def mark_success(self, url, html):
        for u in self.urls:
            if u["url"] == url:
                u["status"] = "success"
                u["html"] = html

    def mark_failed(self, url, error):
        for u in self.urls:
            if u["url"] == url:
                u["status"] = "failed"
                u["last_error"] = error
                u["retries"] += 1

    def save(self, path="urls_state.json"):
        with open(path, "a") as f:
            json.dump(self.urls, f, indent=2)

    def load(self, path="urls_state.json"):
        with open(path, "r") as f:
            self.urls = json.load(f)

