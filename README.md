# dexmac221.github.io

Personal site of Gian Luca Bailo: projects, papers, articles and photography.
Plain HTML and CSS, no build step.

- `index.html`, `style.css`, `script.js`: the page.
- `photos/`: the photographs shown in the gallery.
- `data/articles.json` and `tools/update_articles.py`: the article list. Medium's feed only carries the
  latest 10 stories, so every story seen is kept in the JSON file and the list in `index.html` is rebuilt
  from it. The workflow in `.github/workflows/pages.yml` does this once a day and on every push.
