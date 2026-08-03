"""Talk to the GitHub GraphQL API.

Runs with the workflow's default GITHUB_TOKEN, which sees public activity. If
you later want private contributions counted, swap in a classic PAT with
read:user and turn on "Include private contributions on my profile" in your
GitHub settings. Both are free.

Offline, --demo generates plausible-shaped synthetic data so the graphics can be
previewed without a token.
"""

import datetime as dt
import json
import os
import random
import urllib.error
import urllib.request

ENDPOINT = "https://api.github.com/graphql"

CONTRIB_QUERY = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    contributionsCollection(from:$from, to:$to) {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

REPO_QUERY = """
query($login:String!, $cursor:String) {
  user(login:$login) {
    repositories(first:100, after:$cursor, ownerAffiliations:OWNER,
                 isFork:false, privacy:PUBLIC) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        isArchived
        stargazerCount
        languages(first:10, orderBy:{field:SIZE, direction:DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def _post(query: str, variables: dict, token: str) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "profile-generator",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.load(resp)
    if "errors" in body:
        raise RuntimeError(f"GraphQL error: {body['errors']}")
    return body["data"]


def fetch_days(login: str, token: str) -> list[tuple[dt.date, int]]:
    """One (date, count) pair per day for the last 365 days."""
    to = dt.datetime.now(dt.timezone.utc)
    frm = to - dt.timedelta(days=364)
    data = _post(
        CONTRIB_QUERY,
        {
            "login": login,
            "from": frm.replace(microsecond=0).isoformat(),
            "to": to.replace(microsecond=0).isoformat(),
        },
        token,
    )
    cal = data["user"]["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in cal["weeks"]:
        for day in week["contributionDays"]:
            days.append((dt.date.fromisoformat(day["date"]), day["contributionCount"]))
    return sorted(days)


def fetch_languages(login: str, token: str) -> list[tuple[str, int, str]]:
    """(language, bytes, colour) across public non-fork repos, largest first."""
    totals: dict[str, list] = {}
    cursor = None
    while True:
        data = _post(REPO_QUERY, {"login": login, "cursor": cursor}, token)
        repos = data["user"]["repositories"]
        for repo in repos["nodes"]:
            if repo["isArchived"]:
                continue
            for edge in repo["languages"]["edges"]:
                name = edge["node"]["name"]
                entry = totals.setdefault(name, [0, edge["node"]["color"] or "#888"])
                entry[0] += edge["size"]
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]
    return sorted(
        ((k, v[0], v[1]) for k, v in totals.items()), key=lambda r: -r[1]
    )


def demo_days(seed: int = 7) -> list[tuple[dt.date, int]]:
    rng = random.Random(seed)
    today = dt.date.today()
    out = []
    for i in range(365):
        day = today - dt.timedelta(days=364 - i)
        weekday_bias = 0.25 if day.weekday() >= 5 else 0.72
        recency = 0.3 + 0.7 * (i / 365)
        n = 0
        if rng.random() < weekday_bias * recency:
            n = rng.choice([1, 1, 2, 2, 3, 4, 6, 9])
        out.append((day, n))
    return out


def demo_languages() -> list[tuple[str, int, str]]:
    return [
        ("Python", 812_000, "#3572A5"),
        ("TypeScript", 494_000, "#3178c6"),
        ("Go", 208_000, "#00ADD8"),
        ("HTML", 96_000, "#e34c26"),
        ("CSS", 41_000, "#563d7c"),
    ]


def token_from_env() -> str | None:
    return os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")


def streaks(days: list[tuple[dt.date, int]]) -> tuple[int, int, int]:
    """(current, longest, total). Today counts as neutral, not a break -
    otherwise the streak reads zero every morning until you commit."""
    total = sum(n for _, n in days)
    longest = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        longest = max(longest, run)

    current = 0
    for i, (day, n) in enumerate(reversed(days)):
        if n:
            current += 1
        elif i == 0:
            continue  # today is still in progress
        else:
            break
    return current, longest, total
