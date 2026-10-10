# Adding a blog post

1. Copy any file in `_content/posts/` and rename it to the URL you want, e.g. `kidswear-low-moq.html` becomes `vozcruda.com/kidswear-low-moq.html`.
2. Edit the JSON at the top: `title`, `seo_title` (under 60 characters), `description` (under 155), `dek`, `card`, `category`, `date`, `keywords`, `related` (file names without .html) and `faq`.
3. Write the article in HTML below it. `<h2>` headings become the table of contents. `{{SMALLOTZ_BOX}}` inserts the Smallotz call-out.
4. From the repo root run `python3 _tools/build.py`. It rebuilds every post, `blog.html`, `sitemap.xml` and `llms.txt`.
5. Commit and push. Then in Google Search Console and Bing Webmaster Tools, request indexing for the new URL.

Folders starting with `_` are not published by GitHub Pages.
