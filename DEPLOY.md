# Deploying adplaybook.app

Everything below is done except the DNS records, which need the registrar
login and are therefore yours to make.

## State as of 2026-08-10

- Repo pushed to `mattkerr09/adplaybook-site`, branch `main`.
- GitHub Pages enabled from `main` at `/`. Build status: **built**, no errors.
- `CNAME` in the repo root sets the custom domain to `adplaybook.app`.
- Release `v0.1.0` published with `AdPlaybook-0.1.0-arm64.dmg` (22,870,769 bytes),
  signed, notarised and stapled. The homepage download button points at it and
  the link returns 200.
- `adplaybook.app` currently resolves to **207.207.210.153-ish — a Porkbun
  parking page**. Until that changes, the site is not reachable at the domain.

Note that once a `CNAME` file exists, GitHub Pages serves the site **only** at
the custom domain — `mattkerr09.github.io/adplaybook-site/` will 404 or
redirect. That is expected, not a broken build.

## LIVE as of 2026-08-10

DNS moved. `adplaybook.app` resolves to the four GitHub Pages addresses, the
certificate is issued and **HTTPS is enforced**. All 18 pages return 200 over
https, the sitemap lists 18 URLs, and the download button serves real bytes —
a range request against the release asset returns 206 with 1,048,576 bytes of
a 22,870,769-byte DMG.

## Publishing a change

```sh
python _build/render.py --app-repo "../ad maker app"
python _build/check.py          # gate — must be clean
git add -A && git commit && git push
# wait for the Pages build to report the pushed commit, THEN:
python _build/submit.py
```

The order matters. `submit.py` refuses to run if the live site is not serving
the key file, because a rejected batch that looks like a success is worse than
not running — but it cannot tell the difference between "not deployed yet" and
"broken", so give the deploy time to finish first.

## Search engines

**Done automatically.** IndexNow covers Bing, Yandex, Seznam and Naver in one
POST. Both endpoints accepted all 18 URLs (HTTP 202 on first submission, 200 on
re-submission). Re-run `_build/submit.py` after every content change.

**Needs your Google account.** Google dropped its sitemap ping endpoint in 2023
and never joined IndexNow, so it is Search Console or nothing:

1. https://search.google.com/search-console → add `adplaybook.app` as a
   **domain** property (not a URL-prefix property — the domain property covers
   http, https and every subdomain).
2. Verify with the TXT record it gives you, at Porkbun, alongside the A records.
3. Submit `https://adplaybook.app/sitemap.xml`.
4. Use **URL Inspection → Request indexing** on `/specs/` and the two or three
   spec pages you most want ranked. Do the hub and the best pages by hand; let
   the rest come through the sitemap.

Bing Webmaster Tools can import the whole property from Search Console once
that exists, which is faster than verifying it separately.

## What to watch

The spec pages are the ones with a real shot, because the pages ranking above
them are wrong and undated. Track impressions on queries of the shape
"<platform> ad specs" and "<platform> ad character limits". If a page starts
ranking, re-verify its figures against the platform's own documentation before
it gets traffic — the whole claim of the site is that its numbers are current.
