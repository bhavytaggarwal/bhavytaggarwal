# Setup

## 1. Create the repo

The repository must be named exactly after your account and be **public** —
that is what makes GitHub render its README on your profile page.

    https://github.com/new  ->  name it:  bhavytaggarwal

Public matters twice: the profile README only renders from a public repo, and
Actions minutes are free and unmetered on public repositories.

## 2. Push these files

    git init && git branch -M main
    git add -A && git commit -m "profile: initial"
    git remote add origin git@github.com:bhavytaggarwal/bhavytaggarwal.git
    git push -u origin main

The push triggers the workflow, which regenerates everything with real data and
commits anything that changed.

## 3. Edit config.json

It is the only file with content in it. Three things need your attention before
this goes live:

- `wordmark` — currently derived from the handle. Change it if the page should
  read something else.
- `links` — two entries say CHANGE-ME.
- `projects` — two real entries plus a commented template block.
  Copy the template for each one you add.

Then re-run:

    pip install -r requirements.txt
    python scripts/generate.py --demo     # no token needed

`--demo` uses synthetic contribution data so you can preview locally. Drop the
flag in CI, where the token is available.

## 4. Turn the stats on later

`config.json` has `stats.streak` and `stats.languages` set to `false`, because
right now they would print a zero streak and claim your stack is 65% HTML. The
workflow generates both files daily regardless, so the day the graph has
something in it, flip the flags and the graphics are already current.

## 5. Things worth doing that this repo cannot do for you

- Set a display name, bio, and website on your GitHub account. They are empty.
- Pin your best repos. A fork is currently sitting in the popular-repos slot.
- Push real public code. This toolchain is one repo; it needs company.

## Note on the 60-day rule

GitHub disables scheduled workflows in a repo with no activity for 60 days.
This one commits most days, which should keep it alive. If it ever trips you get
an email and re-enabling is one click.
