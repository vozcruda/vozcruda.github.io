# Adding a blog post

1. Copy any file in `_content/posts/` and rename it to the URL you want, e.g. `kidswear-low-moq.html` becomes `vozcruda.com/kidswear-low-moq.html`.
2. Edit the JSON at the top: `title`, `seo_title` (under 60 characters), `description` (under 155), `dek`, `card`, `category`, `date`, `keywords`, `related` (file names without .html) and `faq`.
3. Write the article in HTML below it. `<h2>` headings become the table of contents. `{{SMALLOTZ_BOX}}` inserts the Smallotz call-out.
4. From the repo root run `python3 _tools/build.py`. It rebuilds every post, the pages in `_content/pages/` (the About page), `blog.html`, the sitemaps, `llms.txt` and `llms-full.txt`.
5. Commit and push. Then in Google Search Console and Bing Webmaster Tools, request indexing for the new URL.

Folders starting with `_` are not published by GitHub Pages.

# AI search (ChatGPT, Perplexity, Claude, Gemini, Google AI Overviews)

- Start every post with the `<div class="answer">` short answer box: a 2 to 4 sentence direct answer to the title's question. AI answers quote these.
- Give every post 4 to 6 `faq` entries phrased the way people ask. They become visible FAQs and FAQPage structured data.
- `llms.txt` (summary and index) and `llms-full.txt` (full text) are rebuilt automatically. Keep the facts in `build_llms` and `_content/pages/about.html` in sync with the homepage.
- After each push to main, the IndexNow workflow tells Bing and other engines about every URL in the sitemap. Do not delete the key file `78888b40451e82693e4b8c120581e4a4.txt` at the site root.

# Free tools and downloads

- Standalone pages live in `_content/pages/`. Set `"kind"` to `"tool"` (interactive, e.g. the cost calculator) or `"download"`; `build.py` adds the matching structured data, footer links and llms.txt entries. Wrap widgets and download cards in `<!--tool-->` … `<!--/tool-->` so they stay out of llms-full.txt.
- Tech pack downloads in `/downloads` are generated: `pip install openpyxl`, then `python3 _tools/techpack/make_techpack.py` and `node _tools/techpack/make_pdf.js` (needs Playwright).
