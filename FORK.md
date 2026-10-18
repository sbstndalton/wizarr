# sbstndalton's Wizarr fork

This is a community fork of **[wizarrrr/wizarr](https://github.com/wizarrrr/wizarr)**. Wizarr's authors retain credit for the original application. The original [MIT license](LICENSE.md), copyright notice, source history, and upstream documentation are preserved. This fork is independently maintained and is not an official Wizarr release.

## Changes

- Guest signup does not require email. The Jellyfin and hybrid signup screens omit the email field; a supplied email is still validated.
- Guest passwords can be 1–128 characters, without uppercase/number requirements. Password confirmation remains required. Guest reset paths use the same length rule. Administrator password requirements are unchanged. Other media backends may impose their own password rules.
- `/j/INVITECODE?username=Requested.Name` prefills an editable username. The name survives pre-invite wizard redirects and is normalized to the existing username format and length. It never replaces an applicant's posted username.
- Invitation validation, approval, server permissions, and account creation remain in their existing paths. A name in a URL does not grant access.
- Set `WIZARR_PUBLIC_URL=https://your-public-wizarr-host` to return complete invitation links in the API's existing `url` field on creation and listing. Without it, upstream's relative `/j/CODE` response is preserved. The `code` field remains the invitation identifier. A client copying only `code` must use `url` to share a complete link; this fork cannot change a closed-source client's copy button.

The companion [Jellyfin Wizarr Requests plugin](https://github.com/sbstndalton/jellyfin-plugin-wizarr-requests) can collect a name and note, require administrator approval, and create a single-use invitation. Enable its name prefill option when using this fork. Set the public Jellyfin address in Wizarr's media server settings; no server address is embedded in this source.

Omitting email also means that email-based account recovery cannot deliver a message for those accounts. A server administrator can handle recovery. Username query parameters can appear in browser history and proxy logs; do not include passwords or other secrets in them.

## Build and run

Build from this fork's source using its existing Dockerfile:

```sh
git clone https://github.com/sbstndalton/wizarr.git
cd wizarr
docker build --build-arg APP_VERSION=2026.10.1-sbstndalton.1 \
  --build-arg VCS_REF="$(git rev-parse HEAD)" -t wizarr-community:2026.10.1-sbstndalton.1 .
docker run -d --name wizarr -p 5690:5690 \
  -v /path/to/wizarr/database:/data/database \
  -e PUID=1000 -e PGID=1000 --restart unless-stopped \
  wizarr-community:2026.10.1-sbstndalton.1
```

Replace the database path and user/group IDs with your deployment values. For an existing installation, back up the database and configuration, then recreate its container using the fork image while preserving its environment, network, ports, and database mount. Do not run two writers against the same database. This source release does not publish a prebuilt container image.

## Keep the fork updated

The fork starts from upstream commit `e84918bf69f0fb75f1e49b9178ffae9db723b16e` (upstream application version `2026.10.1`). Its changes are separate commits so Git can merge future upstream changes.

```sh
git remote add upstream https://github.com/wizarrrr/wizarr.git
git fetch upstream --tags
git switch main
git pull --ff-only origin main
git switch -c update-upstream-YYYY-MM-DD
git merge upstream/main
# Resolve conflicts while retaining the changes described above.
docker build -t wizarr-fork-check .
docker run --rm --network none -e PYTHONPATH=/app \
  --entrypoint /app/.venv/bin/python \
  -v "$PWD/tests/fork_onboarding_smoke.py:/tmp/fork_onboarding_smoke.py:ro" \
  wizarr-fork-check /tmp/fork_onboarding_smoke.py
git push -u origin update-upstream-YYYY-MM-DD
```

If `upstream` already exists, skip the `remote add` command. Open a pull request into this fork's `main` and wait for the fork build/check workflow before merging. GitHub's **Sync fork** button can also merge upstream, but never use **Discard commits**: that removes the custom changes. Conflicts need manual resolution. Review upstream migrations/release notes, choose a new fork release tag, and back up before deploying the rebuilt image.

[Compare this fork with upstream](https://github.com/wizarrrr/wizarr/compare/main...sbstndalton:wizarr:main). Updates are mergeable; they are not automatically deployed to a live server.

The dedicated **Fork build and onboarding checks** workflow builds the full image and runs isolated synthetic checks. Upstream publishing/Discord/translation workflows remain in source for easier merges but are disabled in this fork's GitHub settings. Keep them disabled when syncing upstream. Agent folders and instruction files are excluded from the current fork source.
