# Kelley Griffin's website: instructions for Claude

This repository is **thegriffinteam.com**, the website of Kelley Griffin, REALTOR®, Broker Associate with Coldwell Banker Distinctive Properties in Grand Junction, Colorado. Netlify builds and hosts it. Every change merged into `main` goes live about a minute later.

You are usually working for **Kelley**. She is a busy real estate agent, not a developer. Talk to her in plain, warm, short sentences. Don't show her code, file names or commands unless she asks. Tell her what you changed in words she would use ("I added the Ouray Avenue sale to Recent Sales"), then give her the preview link.

## How every change goes live (always follow this)

1. **Work on a new branch.** Never commit straight to `main`.
2. Make the change, then run `python3 src/build.py`. It must finish with "built N pages" and no error. If it stops with a message, fix what it names.
3. **Open a pull request** into `main` with a one-line plain-English title ("Add blog post: Fall market update").
4. Netlify adds a **Deploy Preview** link to the pull request within a minute or two (look for the netlify bot comment or the "deploy/netlify" check, link like `https://deploy-preview-12--<site>.netlify.app`). Give Kelley that link and ask her to look, on her phone too.
5. **Only when Kelley says it looks good** ("publish", "go", "looks great"), merge the pull request. Then tell her it's live and give her the real address, such as `https://thegriffinteam.com/blog/fall-market-update`.
6. If she wants changes, keep working on the same branch; the preview updates itself.

**Bundle changes.** The free Netlify plan allows roughly 15 to 18 publishes a month. Previews are free. If Kelley has several small edits, make them together on one branch and publish once. If she asks for more than about three publishes in a week, mention it kindly and offer to batch.

## Where things live

| What | Where | Notes |
|---|---|---|
| Blog posts | `content/blog/YYYY-MM-DD-slug.md` (or `.html`) | One file per post. Address becomes `/blog/slug`. |
| Client testimonials | `content/testimonials.json` | Shown on Client words and the home page. |
| Recent sales | `content/recent-sales.json` | Shown on Recent sales, newest or priciest first. |
| Photos | `site/assets/` (blog photos in `site/assets/blog/`, sale photos in `site/assets/sold/`) | Always prepare with `tools/add_photo.py`. |
| Page words (home, Meet Kelley, guides, neighborhoods, contact) | `src/build.py` | Search for the sentence and edit it in place. |
| Phone, email, address, license, title | Top of `src/build.py` (`PHONE`, `EMAIL`, `ADDR1`...) | Change once, updates every page. |
| Old-address redirects, Netlify settings | `netlify.toml` | Don't change without Griffin. |
| Built pages | `site/*.html`, `site/blog/` | Generated on every deploy. Never edit by hand; they are not saved in git. |

## Recipes

### Write a blog post
Create `content/blog/2026-11-20-short-title-words.md`:

```
---
title: Fall Market Update for Fruita Buyers
date: 2026-11-20
slug: fall-market-update-fruita
description: One sentence, under 160 characters, that makes someone want to click from Google.
photo: blog/fall-market-update-fruita.jpg
photo_alt: Golden cottonwoods along the Colorado River near Fruita
---
Opening paragraph in Kelley's voice.

## A clear heading

More paragraphs. Use **bold** sparingly, - bullet lists, and [links](/contact).
```

- The slug is lowercase words joined by hyphens and must be new. Never rename or delete an old post's slug: Google and past emails link to them.
- If Kelley has no photo, leave `photo:` out and the Grand Junction valley photo is used, or pick a neighborhood photo: `nbhd-fruita.jpg`, `nbhd-grand-junction.jpg`, `nbhd-grand-mesa.jpg`, `nbhd-loma.jpg`, `nbhd-palisade.jpg`, `nbhd-redlands.jpg`.
- Add `draft: yes` to keep a post off the site while she thinks about it.
- Write like Kelley: first person, friendly, local and specific (street names, trails, seasons), short paragraphs. End with a soft invitation to reach out, linked to `/contact`. Check facts; cite numbers with their source and month.

### Add a new listing
There is no listings page (Kelley's MLS search isn't connected). Post it as a blog post titled "Just listed: 123 Main Street, Fruita", with price, beds, baths, square feet, three or four honest highlights and the best photo. Include "Listed by Kelley Griffin, Coldwell Banker Distinctive Properties." When it sells, add it to Recent sales and add one line at the top of the post: "Update: this home has sold."

### Move a home to Recent sales
Add an entry to the top of `content/recent-sales.json`:

```json
{ "price": "$612,500", "address": "123 Main Street, Fruita, CO 81521", "details": "3 beds · 2 baths · 1,850 sq ft", "photo": "sold/123-main-st.jpg" }
```

Prepare the photo with `tools/add_photo.py inbox/<file> 123-main-st sold`. Use the closed price only if Kelley gives it. Keep the list to the best 9 to 12 sales; ask her before removing one.

### Add a client testimonial
Add `{ "name": "First name and last initial", "words": "Their exact words." }` to `content/testimonials.json`. Use the client's words exactly, fixing only obvious typos. Never invent or polish praise. Drop any sentence that names another brokerage. Ask Kelley before adding if the client hasn't said it can be shared.

### Change words on a page
Find the sentence in `src/build.py` (search for a few distinctive words) and edit it there. Keep the HTML around it unchanged.

### Swap or add a photo
1. Kelley uploads photos to the `inbox/` folder on GitHub (she has a bookmark for the upload page), or attaches them in the chat if your session can save attachments.
2. Run `pip install pillow pillow-heif` once, then `python3 tools/add_photo.py inbox/<file> <short-name> [folder]`. It saves a large copy for big screens and a 1200 px copy for phones (the site picks the right one), fixes rotation, compresses, and strips GPS and camera data. It prints the width and height. Always start from the full-size original; a small photo looks soft as a banner.
3. Point the page at the new file, write true alt text (what the photo shows, in a sentence), and delete the original from `inbox/`.

## Rules that always apply

- **Facts:** Kelley Griffin, REALTOR®, Broker Associate, Coldwell Banker Distinctive Properties, 131 N 6th St, Suite 200, Grand Junction, CO 81501. Mobile (970) 589-6555, office (970) 243-0456, kelley@thegriffinteam.com, Colorado license FA100069554. In the Grand Valley **since 2008** (never "16 years"). More than 10 years in real estate. Husband Dane, Griffin Design and Construction, LLC.
- **Never mention Chesnick Realty** (her former brokerage) anywhere.
- **Photos:** real photos only. No AI-generated or stock images of people or homes. Never use the file called "Kelley Headshot.png" (it is AI-generated). Her real headshots are `kelley-headshot.jpg` and `kelley-portrait.jpg`. Professional photos for spots where people meet her; her own phone photos for blog posts and neighborhoods.
- **Fair housing:** describe homes and places, not people. Don't say a neighborhood is "safe", "family-friendly", "exclusive" or suited to any group. Talk about features: trails, schools by name, lot size, commute.
- **Accuracy:** no "#1", "top producer", guarantees or claims Kelley can't back up. Keep the legal footer, the Equal Housing Opportunity and REALTOR® marks, and the sold-data disclaimer.
- **Brand:** Coldwell Banker navy `#012169`, sand gold `#CCB091`, Noto Serif Display headings, Poppins text. Don't restyle the site; add content in the existing patterns. The full brand guide is in Kelley's Google Drive (The Griffin Team Website, 4 Claude website helper, Brand).
- **Never touch** the domain, DNS, email settings, Netlify account settings, the contact form's setup, or `netlify.toml`. If Kelley asks for any of those, or anything breaks, say so plainly and suggest she contact Griffin Jacobs (griffin@griffinjacobs.com).
- **Contact form** messages are emailed to kelley@thegriffinteam.com by FormSubmit (formsubmit.co). If she stops getting them, that's a Griffin question.

## Quick checks before you open the pull request

- `python3 src/build.py` finished without errors.
- The new or changed page reads correctly start to finish, with no typos, and has a title and description.
- Every link you added works. Phone numbers and email match the facts above.
- Photos have alt text and came through `tools/add_photo.py`.
