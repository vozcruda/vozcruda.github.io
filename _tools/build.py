#!/usr/bin/env python3
"""Build Voz Cruda Insights pages.

Each post lives in _content/posts/<slug>.html:
  a JSON block inside <!--meta ... --> followed by the article body HTML.

Run from the repo root:  python3 _tools/build.py
Outputs: <slug>.html for every post, blog.html, sitemap.xml, llms.txt.
GitHub Pages (Jekyll) ignores folders starting with "_", so _content and _tools are not published.
"""
import html, json, math, re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://vozcruda.com"
SMALLOTZ = "https://smallotz.vozcruda.com/"
OG_IMAGE = f"{SITE}/assets/images/og-vozcruda.png"
ORG = {"@type": "Organization", "name": "Voz Cruda LLP", "url": SITE + "/",
       "logo": f"{SITE}/assets/images/og-vozcruda.png"}

EXTRA_POSTS = []

def esc(s):
    return html.escape(s, quote=True)

def slugify(s):
    s = re.sub(r"<[^>]+>", "", s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60].rstrip("-")

def load_posts():
    posts = []
    for f in sorted((ROOT / "_content" / "posts").glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta(.*?)-->(.*)", raw, re.S)
        if not m:
            raise SystemExit(f"{f.name}: missing <!--meta --> block")
        meta = json.loads(m.group(1))
        meta["slug"] = f.stem
        meta["body"] = m.group(2).strip()
        words = len(re.sub(r"<[^>]+>", " ", meta["body"]).split())
        words += sum(len((q["q"] + " " + q["a"]).split()) for q in meta.get("faq", []))
        meta["minutes"] = max(3, math.ceil(words / 220))
        meta.setdefault("updated", meta["date"])
        posts.append(meta)
    posts.sort(key=lambda p: (p.get("order", 99), p["slug"]))
    return posts

def add_heading_ids(body):
    toc = []
    def repl(m):
        attrs, inner = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        hid = idm.group(1) if idm else slugify(inner)
        toc.append((hid, re.sub(r"<[^>]+>", "", inner)))
        if not idm:
            attrs = f' id="{hid}"' + attrs
        return f"<h2{attrs}>{inner}</h2>"
    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", repl, body, flags=re.S)
    return body, toc

def fmt_date(d):
    return date.fromisoformat(d).strftime("%-d %B %Y")

HEAD_FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
              '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
              '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&family=Outfit:wght@400;500;600&family=Cormorant+Garamond:wght@600&family=JetBrains+Mono:wght@400;500&display=swap">\n'
              '<link rel="stylesheet" href="/assets/css/site.css">')

def head(title, desc, url, og_type="website", ld=(), extra=""):
    lds = "\n".join(f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, indent=1)}\n</script>' for x in ld)
    return f"""<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:site_name" content="Voz Cruda">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:locale" content="en_IN">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{OG_IMAGE}">
<meta name="theme-color" content="#0A0A0A">
{extra}{HEAD_FONTS}
{lds}
</head>"""

def header(active_blog=True):
    cur = ' aria-current="page"' if active_blog else ""
    return f"""<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="/" aria-label="Voz Cruda home">Voz <span>Cruda</span></a>
    <ul class="nav-links" id="navLinks">
      <li><a href="/#process">How it works</a></li>
      <li><a href="/#smallotz">Smallotz<span class="new">NEW</span></a></li>
      <li><a href="/#categories">What we source</a></li>
      <li><a href="/#who-we-help">Who we help</a></li>
      <li><a href="/#manufacturers">Manufacturers</a></li>
      <li><a href="https://shop.vozcruda.com/" target="_blank" rel="noopener">Shop ↗</a></li>
      <li><a href="/blog.html"{cur}>Insights</a></li>
    </ul>
    <a class="btn btn-primary nav-cta" href="/#contact">Start sourcing <span class="arr">→</span></a>
    <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false" aria-controls="navLinks">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h14M3 14h14"/></svg>
    </button>
  </div>
</header>"""

def footer(posts):
    top = "".join(f'<li><a href="/{p["slug"]}.html">{esc(p.get("short", p["title"]))}</a></li>' for p in posts[:4])
    return f"""<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="/">Voz <span>Cruda</span></a>
        <p>Apparel sourcing and low MOQ manufacturing for fashion brands in India. Bengaluru.</p>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="/#process">How it works</a></li>
          <li><a href="/#manufacturers">For manufacturers</a></li>
          <li><a href="/#contact">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Products</h4>
        <ul>
          <li><a href="{SMALLOTZ}" target="_blank" rel="noopener">Smallotz ↗</a></li>
          <li><a href="https://shop.vozcruda.com/" target="_blank" rel="noopener">Voz Cruda Store ↗</a></li>
          <li><a href="/#categories">What we source</a></li>
        </ul>
      </div>
      <div>
        <h4>Popular guides</h4>
        <ul>{top}</ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>© 2026 Voz Cruda LLP. All rights reserved.</span>
      <span><a href="mailto:sales@vozcruda.com" style="text-decoration:none">sales@vozcruda.com</a> · Bengaluru, India</span>
    </div>
  </div>
</footer>
<script>
(function(){{var b=document.getElementById('menuBtn'),l=document.getElementById('navLinks');
b.addEventListener('click',function(){{var o=l.classList.toggle('open');b.setAttribute('aria-expanded',o)}});
l.addEventListener('click',function(e){{if(e.target.tagName==='A'){{l.classList.remove('open');b.setAttribute('aria-expanded',false)}}}});}})();
</script>
</body>
</html>
"""

def card(p, feature=False):
    cls = "card feature" if feature else "card"
    return (f'<a class="{cls}" href="/{p["slug"]}.html"><div><span class="label">{esc(p["category"])} · {p["minutes"]} min read</span>'
            f'<h3>{esc(p["title"])}</h3><p>{esc(p["card"])}</p></div><span class="read">Read →</span></a>')

SZ_BOX = f"""<aside class="sz-box">
  <span class="label">Smallotz by Voz Cruda</span>
  <h3>Order what you need. No minimums.</h3>
  <p>Smallotz pools your order with other buyers making the same kind of product. Together you reach the factory MOQ, and each brand orders only the quantity it needs.</p>
  <a class="btn btn-primary" href="{SMALLOTZ}" target="_blank" rel="noopener">Open Smallotz ↗</a>
</aside>"""

def build_post(p, all_posts):
    url = f"{SITE}/{p['slug']}.html"
    body, toc = add_heading_ids(p["body"].replace("{{SMALLOTZ_BOX}}", SZ_BOX))
    faq = p.get("faq", [])
    if faq:
        toc.append(("faq", "Frequently asked questions"))
        items = "\n".join(f'<details><summary>{esc(q["q"])}</summary><p>{q["a"]}</p></details>' for q in faq)
        body += f'\n<h2 id="faq">Frequently asked questions</h2>\n<div class="faq">\n{items}\n</div>'
    toc_html = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)

    ld = [{
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": p["title"], "description": p["description"], "image": OG_IMAGE,
        "datePublished": p["date"], "dateModified": p["updated"],
        "author": ORG, "publisher": ORG, "inLanguage": "en-IN",
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "keywords": ", ".join(p.get("keywords", [])),
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Insights", "item": SITE + "/blog.html"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]
    }]
    if faq:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q["q"],
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", q["a"])}} for q in faq]})

    by_slug = {x["slug"]: x for x in all_posts}
    rel = [by_slug[s] for s in p.get("related", []) if s in by_slug][:3]
    rel_html = "".join(card(r) for r in rel)

    out = head(p["seo_title"], p["description"], url, "article", ld,
               extra=f'<meta property="article:published_time" content="{p["date"]}">\n'
                     f'<meta property="article:modified_time" content="{p["updated"]}">\n')
    out += f"""
<body>
{header()}
<main>
<article>
  <div class="post-hero">
    <div class="wrap"><div class="inner">
      <ol class="crumbs"><li><a href="/">Home</a></li><li><a href="/blog.html">Insights</a></li><li>{esc(p["category"])}</li></ol>
      <div class="meta-row"><span class="label dye">{esc(p["category"])}</span><span class="label">{p["minutes"]} min read</span><span class="label">Updated <time datetime="{p["updated"]}">{fmt_date(p["updated"])}</time></span></div>
      <h1>{esc(p["title"])}</h1>
      <p class="dek">{esc(p["dek"])}</p>
    </div></div>
  </div>
  <div class="post"><div class="wrap post-grid">
    <div class="prose">
      <nav class="toc-inline" aria-label="Contents"><span class="label">In this article</span><ol>{toc_html}</ol></nav>
{body}
      <div class="byline"><span>Written by <b>the Voz Cruda team</b>, apparel sourcing specialists in Bengaluru. Published <time datetime="{p["date"]}">{fmt_date(p["date"])}</time>.</span></div>
    </div>
    <aside class="toc-side" aria-label="Contents"><span class="label">In this article</span><ol>{toc_html}</ol></aside>
  </div></div>
</article>
<section class="related"><div class="wrap">
  <span class="label dye">Keep reading</span>
  <h2>More guides for small apparel brands</h2>
  <div class="card-grid">{rel_html}</div>
</div></section>
<section class="cta-band"><div class="wrap"><div class="cta-box">
  <span class="label dye">Start sourcing</span>
  <h2>Tell us what you want to make.</h2>
  <p>Share your product, quantity and timeline. We match you with suitable manufacturers, or pool your lot on Smallotz if you are ordering under a factory's minimum.</p>
  <div class="row"><a class="btn btn-primary" href="/#contact">Start your sourcing request <span class="arr">→</span></a><a class="btn btn-ghost" href="{SMALLOTZ}" target="_blank" rel="noopener">Order small runs on Smallotz ↗</a></div>
</div></div></section>
</main>
{footer(all_posts)}"""
    (ROOT / f"{p['slug']}.html").write_text(out, encoding="utf-8")

def build_index(posts, listing):
    url = SITE + "/blog.html"
    ld = [{"@context": "https://schema.org", "@type": "Blog", "name": "Voz Cruda Insights", "url": url,
           "description": "Guides on low MOQ clothing manufacturing, apparel sourcing and starting a fashion brand in India.",
           "publisher": ORG,
           "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/{p['slug']}.html",
                         "datePublished": p["date"]} for p in listing]}]
    first, rest = listing[0], listing[1:]
    cats = sorted({p["category"] for p in listing})
    out = head("Low MOQ Clothing &amp; Sourcing Guides | Voz Cruda Insights",
               "Practical guides on low MOQ clothing manufacturing, order pooling, private label and apparel sourcing in India, for fashion founders and retailers.",
               url, "website", ld)
    out += f"""
<body>
{header()}
<main>
<section class="index-hero"><div class="wrap">
  <span class="label dye">Voz Cruda Insights</span>
  <h1>Guides for building an apparel brand in India.</h1>
  <p>Low MOQ manufacturing, order pooling, supplier vetting, private label and India's apparel hubs, written for founders, boutiques and D2C sellers.</p>
</div></section>
<section style="padding-top:0"><div class="wrap">
  <div class="filters">{"".join(f"<span>{esc(c)}</span>" for c in cats)}</div>
  <div class="card-grid">{card(first, True)}{"".join(card(p) for p in rest)}</div>
</div></section>
<section class="cta-band"><div class="wrap"><div class="cta-box">
  <span class="label dye">Smallotz by Voz Cruda</span>
  <h2>Order what you need. No minimums.</h2>
  <p>Pool your order with other buyers to reach the factory MOQ. Factory access without factory volumes.</p>
  <div class="row"><a class="btn btn-primary" href="{SMALLOTZ}" target="_blank" rel="noopener">Open Smallotz ↗</a><a class="btn btn-ghost" href="/#contact">Talk to us first</a></div>
</div></div></section>
</main>
{footer(posts)}"""
    (ROOT / "blog.html").write_text(out, encoding="utf-8")

def build_sitemap(listing):
    today = date.today().isoformat()
    urls = [(SITE + "/", today, "1.0"), (SITE + "/blog.html", today, "0.8")]
    urls += [(f"{SITE}/{p['slug']}.html", p["updated"], "0.7") for p in listing]
    body = "\n".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>" for u, d, pr in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n',
        encoding="utf-8")

def build_llms(listing):
    lines = "\n".join(f"- [{p['title']}]({SITE}/{p['slug']}.html): {p['card']}" for p in listing)
    (ROOT / "llms.txt").write_text(f"""# Voz Cruda

> Voz Cruda LLP is an apparel sourcing company in Bengaluru, India. It matches fashion brands, boutiques, D2C and private label businesses with suitable clothing manufacturers, and coordinates production. Its product Smallotz lets small buyers order low MOQ clothing with no minimums by pooling orders with other buyers until the factory's minimum order quantity (MOQ) is reached.

Key facts:
- Services: supplier matching, MOQ aggregation (order pooling), production coordination, private label sourcing.
- Smallotz by Voz Cruda: order what you need, no minimums. Buyers add their quantity to a pooled lot; when the lot reaches the factory MOQ, production goes ahead. App: {SMALLOTZ}
- Categories: t-shirts and tops, shirts, bottomwear, dresses, ethnic wear, outerwear and hoodies, private label, custom.
- Manufacturing hubs covered: Tiruppur (knitwear), Surat (synthetics and wovens), Jaipur (ethnic wear), Delhi NCR (fashion and private label), Bengaluru (contemporary apparel).
- Best for: emerging fashion brands, Instagram and D2C sellers, boutiques, and private label businesses ordering under 300 pieces per style.
- Contact: sales@vozcruda.com. Registered office: Voz Cruda LLP, Ejipura, Bengaluru, Karnataka, India.

## Pages
- [Home]({SITE}/): apparel sourcing and Smallotz overview
- [Insights]({SITE}/blog.html): all guides

## Guides
{lines}
""", encoding="utf-8")

def main():
    posts = load_posts()
    for p in posts:
        build_post(p, posts)
    listing = posts + EXTRA_POSTS
    build_index(posts, listing)
    build_sitemap(listing)
    build_llms(listing)
    print(f"Built {len(posts)} posts, blog.html, sitemap.xml, llms.txt")

if __name__ == "__main__":
    main()
