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

## The one step left: point DNS at GitHub Pages

In the Porkbun DNS editor for `adplaybook.app`, delete the parking records and
add these four A records for the apex (host left blank or `@`):

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

Optionally the matching AAAA records for IPv6:

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

And a CNAME for `www` pointing at `mattkerr09.github.io`.

Then in the repo's **Settings → Pages**, tick **Enforce HTTPS** once GitHub has
issued the certificate. It cannot issue one until DNS resolves, so this is a
second visit rather than something to do now.

## Verify after DNS propagates

```sh
dig +short adplaybook.app A
curl -sI https://adplaybook.app/ | head -1
curl -s https://adplaybook.app/sitemap.xml | grep -o '<loc>' | wc -l   # expect 18
curl -sI https://adplaybook.app/specs/linkedin/ | head -1
```

## Then, and only then, submit to search

Do not submit before the domain resolves — a sitemap fetched from a parking
page teaches Google the wrong thing about the site.

1. Google Search Console → add `adplaybook.app` as a domain property, verify by
   DNS TXT, submit `https://adplaybook.app/sitemap.xml`.
2. Bing Webmaster Tools → import from Search Console.
3. Request indexing on `/specs/` and the two or three spec pages with the
   strongest query volume before the long tail.

## Rebuilding the site

```sh
python _build/render.py --app-repo "../ad maker app"
python _build/check.py     # must pass before pushing
git add -A && git commit && git push
```

`check.py` is a gate, not a linter. It fails the build on a missing canonical,
a page absent from the sitemap, or a sentence that asserts something about a
named competitor. Push only on a clean run.
