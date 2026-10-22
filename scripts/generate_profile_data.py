"""Fetch public GitHub metadata without storing display name or bio."""
from __future__ import annotations
import json, os, sys, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "generated" / "profile_data.json"
USERNAME = os.environ.get("GITHUB_USERNAME", "Ai-finder-for-api")
API = "https://api.github.com"

def get_json(url: str):
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-maintenance-toolkit",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)

def main() -> int:
    try:
        profile = get_json(f"{API}/users/{USERNAME}")
        repos = get_json(f"{API}/users/{USERNAME}/repos?per_page=100&sort=updated&type=owner")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        print(f"GitHub API request failed: {exc}", file=sys.stderr)
        return 1
    if not isinstance(repos, list) or not isinstance(profile, dict):
        print("Unexpected GitHub API response; output was not changed.", file=sys.stderr)
        return 1
    languages: dict[str, int] = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    snapshot = {
        "login": profile.get("login", USERNAME),
        "public_repos": profile.get("public_repos", 0),
        "followers": profile.get("followers", 0),
        "following": profile.get("following", 0),
        "public_gists": profile.get("public_gists", 0),
        "repositories_scanned": len(repos),
        "languages_by_repository_count": dict(sorted(languages.items(), key=lambda item: item[1], reverse=True)),
        "note": "Public metadata only. No display name, bio, email, or private repository data is stored."
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
            stable_previous = {k: v for k, v in previous.items() if k != "generated_at"}
            if stable_previous == snapshot:
                print("Public profile metadata is unchanged; leaving the snapshot untouched.")
                return 0
        except (OSError, json.JSONDecodeError):
            pass
    snapshot["generated_at"] = datetime.now(timezone.utc).isoformat()
    OUTPUT.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {OUTPUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
