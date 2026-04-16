#!/usr/bin/env python3
"""
fetch_board.py — pull the TA-39 GitHub Projects board (project #4) and emit
a structured JSON snapshot on stdout.

Reads the PAT from ~/.secrets/github_pat (resolves glob patterns for Cowork
mounts).  Outputs JSON with `meta` (counts, retrieval time) and `items`
(per-feature records with bucket assignment).

Intentionally minimal dependencies: only the stdlib.
"""

from __future__ import annotations

import datetime as _dt
import glob as _glob
import json as _json
import os as _os
import sys as _sys
import urllib.request as _req
from typing import Any

GRAPHQL_URL = "https://api.github.com/graphql"
ORG = "TA-39"
PROJECT_NUMBER = 4

# Bucket mapping.  Kanban statuses → roadmap buckets used in TA39-Roadmap.md.
BUCKET_BY_STATUS: dict[str, str] = {
    # RELEASED
    "Testing in Production": "RELEASED",
    "In Production & Done": "RELEASED",
    # NOW
    "In progress": "NOW",
    "Development Complete": "NOW",
    "Ready for Testing (Staging)": "NOW",
    "Testing in Staging": "NOW",
    "Testing Pre-Production": "NOW",
    "Testing Result Discussion": "NOW",
    # NEXT
    "Ready for Development": "NEXT",
    # BLOCKED
    "Blocked / Information Needed": "BLOCKED",
    # LATER
    "Backlog": "LATER",
    # EXCLUDED
    "Archive": "ARCHIVED",
}


def _load_pat() -> str:
    """Find a PAT.  Order of precedence:
    1. GITHUB_PAT env var
    2. ~/.secrets/github_pat
    3. /sessions/*/mnt/.secrets/github_pat                  (Cowork mount root)
    4. /sessions/*/mnt/*/.secrets/github_pat                (one level deep)
    5. /sessions/*/mnt/**/.secrets/github_pat               (recursive, bounded)

    Cowork sessions each mount whatever folder the user selected, so the same
    skill may see `.secrets/` at the mount root OR inside a subfolder
    depending on what the user picked.  We check the common depths so users
    aren't forced to put the PAT in exactly one spot.
    """
    env = _os.environ.get("GITHUB_PAT", "").strip()
    if env:
        return env

    home = _os.path.expanduser("~/.secrets/github_pat")
    if _os.path.exists(home):
        return open(home).read().strip()

    # Cowork persists ~/.claude/ across every session on the user's Mac, so a
    # PAT placed here only needs to be set once and is found no matter which
    # folder the user selects for a given Cowork session.
    search_patterns = [
        "/sessions/*/mnt/.claude/ta39-secrets/github_pat",
        "/sessions/*/mnt/.secrets/github_pat",
        "/sessions/*/mnt/*/.secrets/github_pat",
        "/sessions/*/mnt/*/*/.secrets/github_pat",
    ]
    for pat in search_patterns:
        for cand in _glob.glob(pat):
            if _os.path.exists(cand):
                return open(cand).read().strip()

    raise SystemExit(
        "No GitHub PAT found. Place a classic PAT with `repo` and `project` "
        "scopes in a `.secrets/github_pat` file inside the folder you've "
        "selected for Cowork (or a subfolder of it), or set the GITHUB_PAT "
        "environment variable."
    )


def _gql(query: str, variables: dict[str, Any], token: str) -> dict[str, Any]:
    body = _json.dumps({"query": query, "variables": variables}).encode()
    req = _req.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "ta39-roadmap-md/1.0",
        },
    )
    with _req.urlopen(req, timeout=60) as resp:
        payload = _json.loads(resp.read())
    if "errors" in payload:
        raise SystemExit(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


PROJECT_QUERY = """
query($org: String!, $num: Int!, $cursor: String) {
  organization(login: $org) {
    projectV2(number: $num) {
      items(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isArchived
          content {
            __typename
            ... on Issue {
              number
              title
              url
              state
              author { login }
              repository { name nameWithOwner }
              issueType { name }
              labels(first: 30) { nodes { name } }
            }
          }
          fieldValues(first: 30) {
            nodes {
              __typename
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2SingleSelectField { name } }
              }
              ... on ProjectV2ItemFieldIterationValue {
                title
                field { ... on ProjectV2IterationField { name } }
              }
            }
          }
        }
      }
    }
  }
}
"""


def _extract_fields(field_values_nodes: list[dict[str, Any]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for n in field_values_nodes:
        if not n:
            continue
        t = n.get("__typename")
        field = (n.get("field") or {}).get("name")
        if not field:
            continue
        if t == "ProjectV2ItemFieldSingleSelectValue":
            out[field] = n.get("name") or ""
        elif t == "ProjectV2ItemFieldIterationValue":
            out[field] = n.get("title") or ""
    return out


def fetch_all_items(token: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        data = _gql(
            PROJECT_QUERY,
            {"org": ORG, "num": PROJECT_NUMBER, "cursor": cursor},
            token,
        )
        proj = (data.get("organization") or {}).get("projectV2")
        if not proj:
            raise SystemExit(
                f"Project #{PROJECT_NUMBER} not found in org {ORG} "
                "(check PAT scopes: needs `read:project` + `repo`)."
            )
        page = proj["items"]
        items.extend(page["nodes"] or [])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return items


def shape(raw_items: list[dict[str, Any]]) -> dict[str, Any]:
    shaped: list[dict[str, Any]] = []
    counts: dict[str, int] = {
        k: 0 for k in ("RELEASED", "NOW", "NEXT", "BLOCKED", "LATER", "ARCHIVED")
    }

    for it in raw_items:
        content = it.get("content") or {}
        if content.get("__typename") != "Issue":
            continue  # skip draft issues, PRs, other types
        fields = _extract_fields((it.get("fieldValues") or {}).get("nodes") or [])

        issue_type = (content.get("issueType") or {}).get("name") or ""
        if issue_type != "Feature":
            continue

        status = fields.get("Status", "")
        bucket = BUCKET_BY_STATUS.get(status, "LATER")
        is_archived = bool(it.get("isArchived")) or bucket == "ARCHIVED"
        if is_archived:
            counts["ARCHIVED"] += 1
            continue

        labels = [l["name"] for l in (content.get("labels") or {}).get("nodes", [])]
        record = {
            "number": content.get("number"),
            "title": content.get("title"),
            "url": content.get("url"),
            "state": content.get("state"),
            "author": (content.get("author") or {}).get("login"),
            "repo": (content.get("repository") or {}).get("name"),
            "repo_full": (content.get("repository") or {}).get("nameWithOwner"),
            "issue_type": issue_type,
            "labels": labels,
            "has_competitive_parity_label": "Competitive Parity" in labels,
            "status": status,
            "priority": fields.get("Priority", ""),
            "size": fields.get("Size", ""),
            "iteration": fields.get("Iteration", ""),
            "bucket": bucket,
        }
        shaped.append(record)
        counts[bucket] += 1

    # Sort for deterministic output: bucket order first, then by number.
    bucket_order = {"NOW": 0, "NEXT": 1, "BLOCKED": 2, "LATER": 3, "RELEASED": 4}
    shaped.sort(key=lambda r: (bucket_order.get(r["bucket"], 9), r["number"] or 0))

    return {
        "meta": {
            "fetched_at": _dt.datetime.now(_dt.timezone.utc).isoformat(
                timespec="seconds"
            ),
            "org": ORG,
            "project_number": PROJECT_NUMBER,
            "counts": counts,
            "in_scope_total": sum(
                counts[k] for k in ("RELEASED", "NOW", "NEXT", "BLOCKED", "LATER")
            ),
        },
        "items": shaped,
        "competitive_parity": [
            {
                "number": r["number"],
                "title": r["title"],
                "url": r["url"],
                "bucket": r["bucket"],
                "repo": r["repo"],
            }
            for r in shaped
            if r["has_competitive_parity_label"]
        ],
    }


def main() -> None:
    token = _load_pat()
    raw = fetch_all_items(token)
    snapshot = shape(raw)
    _json.dump(snapshot, _sys.stdout, indent=2, ensure_ascii=False)
    _sys.stdout.write("\n")


if __name__ == "__main__":
    main()
