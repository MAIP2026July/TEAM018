"""
Collect merged MR history from GitLab for the shadow pilot (see 05_Data_Model_Evaluation.md).

For each merged MR it records basic features (files, size, test changes, paths) and a
"problem" label if a later MR reverted it or a hotfix MR referenced it.

Usage:
    export GITLAB_TOKEN=...            # read_api scope is enough
    python3 collect_mr_history.py --project group/repo --since 2026-01-01 --out mr_history.csv

Only the Python standard library is used. Nothing is sent anywhere except the GitLab API.
The label is noisy: problems that were fixed without referencing the original MR are missed.
"""
import argparse
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request

TEST_RX = re.compile(r"(^|/)(tests?|__tests__|spec)/|\.test\.|\.spec\.|_test\.|(^|/)test_", re.I)
REF_RX = re.compile(r"!(\d+)")


def api(base, token, path, params=None):
    url = f"{base}/api/v4{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"PRIVATE-TOKEN": token})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp), resp.headers.get("X-Next-Page")


def merged_mrs(base, token, project, since):
    page = "1"
    while page:
        items, page = api(base, token, f"/projects/{project}/merge_requests",
                          {"state": "merged", "updated_after": since, "per_page": 100, "page": page})
        yield from items


def features(base, token, project, iid):
    data, _ = api(base, token, f"/projects/{project}/merge_requests/{iid}/changes")
    paths, added, removed, tests = [], 0, 0, 0
    for ch in data.get("changes", []):
        paths.append(ch["new_path"])
        for line in ch.get("diff", "").splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1
        if TEST_RX.search(ch["new_path"]):
            tests += 1
    return paths, added, removed, tests


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="numeric id or group/repo")
    ap.add_argument("--since", required=True, help="YYYY-MM-DD")
    ap.add_argument("--out", default="mr_history.csv")
    ap.add_argument("--gitlab", default=os.environ.get("GITLAB_URL", "https://gitlab.com"))
    args = ap.parse_args()

    token = os.environ.get("GITLAB_TOKEN", "").strip()
    if not token:
        sys.exit("Set GITLAB_TOKEN first.")
    project = urllib.parse.quote(args.project, safe="")

    mrs = list(merged_mrs(args.gitlab, token, project, args.since))
    print(f"{len(mrs)} merged MRs found")

    # Label pass: which MRs were later reverted or referenced by a hotfix?
    problem = {}
    for mr in mrs:
        title, desc = mr["title"] or "", mr["description"] or ""
        branch = mr.get("source_branch") or ""
        if title.lower().startswith("revert"):
            source = "revert"
        elif "hotfix" in title.lower() or "hotfix" in branch.lower():
            source = "hotfix"
        else:
            continue
        for ref in REF_RX.findall(desc):
            problem.setdefault(int(ref), source)

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["iid", "title", "merged_at", "files", "added", "removed", "test_files",
                    "paths", "problem", "label_source"])
        for i, mr in enumerate(mrs, 1):
            paths, added, removed, tests = features(args.gitlab, token, project, mr["iid"])
            src = problem.get(mr["iid"], "")
            w.writerow([mr["iid"], mr["title"], mr["merged_at"], len(paths), added, removed, tests,
                        ";".join(paths), int(bool(src)), src])
            if i % 25 == 0:
                print(f"  {i}/{len(mrs)}")

    print(f"Wrote {args.out}. Problem MRs labelled: {len(problem)}")
    # Author fields are intentionally not exported (see 07_Ethics_Governance_Risk.md).


if __name__ == "__main__":
    main()
