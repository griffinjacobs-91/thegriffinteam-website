# thegriffinteam.com

Kelley Griffin's website (Coldwell Banker Distinctive Properties, Grand Junction, CO).

- **Hosting:** Netlify, free plan. Every merge into `main` builds and publishes; every pull request gets a free Deploy Preview.
- **Build:** `python3 src/build.py` (Python standard library only) reads `content/` and writes the pages into `site/`.
- **Content:** blog posts in `content/blog/`, testimonials and recent sales in `content/*.json`, photos in `site/assets/`.
- **Contact form:** Netlify Forms (form name `contact`), notifications to kelley@thegriffinteam.com.
- **Old addresses:** the 44 Luxury Presence blog posts keep their `/blog/...` addresses; other old pages redirect in `netlify.toml`.
- **Kelley's Claude:** reads `CLAUDE.md` for how to make and publish changes safely.

Local preview: `python3 src/build.py`, then serve `site/` (clean URLs like `/team` map to `team.html` on Netlify).
