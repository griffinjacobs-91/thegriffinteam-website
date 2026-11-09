#!/usr/bin/env python3
"""Builds thegriffinteam.com, Kelley Griffin's website. Netlify runs this on every deploy.
Usage: python3 src/build.py   (SITE env sets the canonical host; default https://thegriffinteam.com)
Reads content/ (blog posts, client words, recent sales) and writes the finished pages into site/.
Internal links are written root-relative with clean URLs (/team, /blog/slug); Netlify serves them from team.html, blog/slug.html."""
import os, re, html, pathlib, json, datetime

def img_size(name):
    """Real pixel size of a photo in site/assets, so the browser reserves the right shape."""
    import struct
    b = (pathlib.Path(__file__).resolve().parent.parent / "site" / "assets" / name).read_bytes()
    if b[:8] == b"\x89PNG\r\n\x1a\n": return struct.unpack(">II", b[16:24])
    i = 2
    while i < len(b):
        if b[i] != 0xFF: i += 1; continue
        m = b[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", b[i + 5:i + 9]); return w, h
        i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    return 1600, 1067

SITE = os.environ.get("SITE", "https://thegriffinteam.com").rstrip("/")
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site"
OUT.mkdir(exist_ok=True)
YEAR = 2026

# ---------------------------------------------------------------- facts ----
NAME = "Kelley Griffin"
TEAM = "The Griffin Team"
BROKER = "Coldwell Banker Distinctive Properties"
TITLE_LINE = "Broker Associate"
PHONE = "(970) 589-6555"; PHONE_TEL = "+19705896555"
OFFICE = "(970) 243-0456"; OFFICE_TEL = "+19702430456"
EMAIL = "kelley@thegriffinteam.com"
# Contact form messages are relayed to EMAIL by FormSubmit (formsubmit.co); Netlify's own form emails only reach Netlify account members.
FORM_ENDPOINT = f"https://formsubmit.co/{EMAIL}"
FORM_ENDPOINT_AJAX = f"https://formsubmit.co/ajax/{EMAIL}"
ADDR1 = "131 N 6th St, Suite 200"; CITY = "Grand Junction, CO 81501"
LICENSE = "FA100069554"
CTA = "Talk to Kelley"

NAV = [("Meet Kelley", "team.html"), ("Buying", "buyers-guide.html"), ("Selling", "sellers-guide.html"),
       ("Neighborhoods", "neighborhoods.html"), ("Client words", "testimonials.html"), ("Recent sales", "sold.html"), ("Blog", "blog/index.html")]

PLACES = [
  dict(slug="loma", name="Loma", elev="4,518 ft", photo="nbhd-loma.jpg", cue="0 0.1 0 0.3", at="0",
       line="Wide-open spaces, quiet living, unlimited adventure.",
       blurb="Loma offers rural charm, big views, and room to breathe, all just minutes from Fruita. It is a favorite for those seeking space, privacy, and easy access to outdoor recreation.",
       alt="A boat launch ramp extends into a blue reservoir at Highline Lake, golden grassland behind it",
       rec=["Immediate access to the Kokopelli Trail system.", "Colorado River recreation nearby.", "Horseback riding, ATVing, and open desert exploring.", "Hunting and wildlife viewing opportunities."],
       amen=["Spacious properties with room for shops, RVs, and livestock.", "Quiet countryside living with quick access to I-70.", "Short drive to Fruita for shopping, dining, and schools."],
       attr=["Kokopelli Loops.", "Highline Lake State Park, just minutes away.", "McInnis Canyons National Conservation Area."],
       love=["Rural lifestyle with wide-open views.", "Lower density and peaceful surroundings.", "Outdoor recreation right out the front door.", "Close to Fruita and a quick hop to Grand Junction."]),
  dict(slug="fruita", name="Fruita", elev="4,514 ft", photo="nbhd-fruita.jpg", cue="0.04 0.28", at="0.06",
       line="Outdoor energy. Small-town charm. Big adventure.",
       blurb="Fruita is a vibrant Western Colorado community known for world-class outdoor recreation, a lively downtown, and a relaxed, friendly lifestyle. It is the perfect blend of adventure and small-town comfort.",
       alt="Red sandstone cliffs and desert hills at sunset with a mountain biker on the trail",
       rec=["Famous mountain biking at 18 Road, Kokopelli, and Lunch Loops.", "Scenic hiking and trail running in the Colorado National Monument.", "Kayaking, floating, and paddleboarding on the Colorado River.", "Camping, stargazing, and wide-open public lands."],
       amen=["Walkable downtown with shops, restaurants, breweries, and events.", "Beautiful parks, playgrounds, and paved paths.", "Strong schools and essential services.", "Easy access to Grand Junction amenities."],
       attr=["Colorado National Monument.", "Dinosaur Journey Museum.", "Fruita Farmers Market.", "Mike the Headless Chicken Festival.", "Fruita Fall Festival."],
       love=["Relaxed lifestyle and friendly community vibe.", "Year-round sunshine.", "Outdoors in every direction.", "Small-town living with big adventures nearby."]),
  dict(slug="redlands", name="The Redlands", elev="Under the Monument", photo="nbhd-redlands.jpg", cue="0.25 0.45", at="0.26",
       line="Scenic living between town and the Monument.",
       blurb="The Redlands is one of the Grand Valley's most popular residential areas, blending stunning scenery, quiet neighborhoods, and quick access to both Fruita and Grand Junction.",
       alt="A pond reflecting autumn trees and red rock mesas in the Redlands",
       rec=["Direct access to Colorado National Monument trails.", "Road cycling along the Rim Rock Loop and Redlands Parkway.", "Golfing at Redlands Mesa Golf Course.", "Nearby river trails and outdoor paths."],
       amen=["Well-established neighborhoods with mature landscaping.", "Local shops, cafés, and dining options.", "Close to schools, parks, and healthcare.", "Easy drive to Grand Junction and Fruita."],
       attr=["Colorado National Monument.", "Redlands Mesa Golf Course.", "Connected trail systems and viewpoints."],
       love=["Peaceful residential living.", "Red rock views in every direction.", "Quick access to outdoor recreation.", "Central location for both cities."]),
  dict(slug="grand-junction", name="Grand Junction", elev="4,583 ft", photo="nbhd-grand-junction.jpg", cue="0.46 0.66", at="0.47",
       line="The heart of the Grand Valley: adventure, culture, and convenience.",
       blurb="Grand Junction is the region's hub for outdoor recreation, arts, education, and everyday amenities. It offers the best of Colorado living without the big-city chaos.",
       alt="The Colorado River winding through green orchards and fields below sunlit desert mesas",
       rec=["Hiking and biking across the Colorado National Monument, Lunch Loops, and Bangs Canyon.", "River access for paddling, fishing, and floating.", "Quick drive to the Grand Mesa and Powderhorn Resort."],
       amen=["Walkable downtown filled with shops, restaurants, breweries, and public art.", "Major shopping centers, healthcare, and services.", "Colorado Mesa University and strong community programs.", "Parks, riverfront paths, and open spaces."],
       attr=["Colorado National Monument.", "Grand Mesa.", "Wine country in nearby Palisade.", "Botanical gardens, museums, and annual festivals."],
       love=["Four-season lifestyle with 300+ days of sunshine.", "A growing city with a welcoming, local feel.", "Culture, convenience, and outdoor access all in one place."]),
  dict(slug="palisade", name="Palisade", elev="4,728 ft", photo="nbhd-palisade.jpg", cue="0.66 0.86", at="0.67",
       line="Wine country charm. River views. Endless sunshine.",
       blurb="Palisade is known for its orchards, vineyards, farm-to-table culture, and relaxed small-town feel. It is the Grand Valley's most scenic agricultural hub, perfect for those who love fresh food, open space, and sunny days.",
       alt="Palisade landscape with a turquoise river below orange cliffs",
       rec=["Biking and walking along the Fruit and Wine Byway.", "Hiking Mt. Garfield and the Palisade Rim Trail.", "Paddleboarding, kayaking, and fishing on the Colorado River.", "Agritourism adventures at orchards, lavender farms, and wineries."],
       amen=["Charming downtown with tasting rooms, cafés, and local shops.", "Farmers markets, festivals, and community events.", "Close proximity to Grand Junction for additional services."],
       attr=["Dozens of vineyards and wineries.", "Peach and fruit orchards.", "Palisade Peach Festival.", "Colorado Riverfront trails."],
       love=["Relaxed wine-country lifestyle.", "Incredible agricultural views.", "Community-driven atmosphere.", "Mild climate and abundant sunshine."]),
  dict(slug="grand-mesa", name="The Grand Mesa", elev="10,000 ft and up", photo="nbhd-grand-mesa.jpg", cue="0.86 1 0.3 0.05", at="0.87",
       line="Lakes, forests, adventure at 10,000 feet.",
       blurb="The Grand Mesa, the world's largest flat-top mountain, is a four-season playground known for cool summers, snowy winters, and endless high-country beauty.",
       alt="Grand Mesa National Forest sign beside a snow-covered mountain road",
       rec=["300+ alpine lakes for fishing, paddling, and exploring.", "Hiking and mountain biking through lush forests.", "Snowmobiling, Nordic skiing, and snowshoeing in winter.", "Downhill skiing at Powderhorn Mountain Resort."],
       amen=["Lodge-style restaurants, cabins, and scenic byways.", "Campgrounds, picnic areas, and visitor centers.", "Quick access from Grand Junction, Palisade, and Delta."],
       attr=["Grand Mesa Scenic Byway.", "Land O' Lakes and Island Lake.", "Mesa Lakes Recreation Area.", "Powderhorn Resort."],
       love=["Cool summer temperatures.", "Endless water and forest recreation.", "Peaceful, quiet mountain atmosphere.", "Close to town but feels like another world."]),
]
VALLEY_X = {"loma": (60, 33), "fruita": (180, 31), "redlands": (330, 10), "grand-junction": (480, 31), "palisade": (660, 22), "grand-mesa": (900, 6)}
VALLEY_D = "M0,34 L60,33 C120,32 150,30 180,31 C240,30 270,12 330,10 C380,14 430,30 480,31 C560,31 600,24 660,22 C740,18 800,8 900,6 L1000,6"

# Client words and recent sales live in content/*.json so they can be edited without touching code.
CONTENT = ROOT / "content"
REVIEWS = [(r["name"], r["words"]) for r in json.loads((CONTENT / "testimonials.json").read_text(encoding="utf-8"))]

SOLD = [(r["price"], r["address"], r["details"], r["photo"]) for r in json.loads((CONTENT / "recent-sales.json").read_text(encoding="utf-8"))]

BUY_STEPS = [
 ("Research", "Do you already know where you want to buy? If you want a condo, townhome, or single-family home? Which features do you like and dislike? What’s available on the market now? If you answered no to any of these questions, now is the time to start researching. In addition to looking for homes that interest you, also take note of any changes in asking prices. This could give you valuable insight into housing trends in specific neighborhoods and help you when the time comes to make an offer."),
 ("Decide on your budget", "Notice we said to decide on your budget, not determine how much the mortgage company will give you. In many cases, a mortgage company will pre-approve you for more than you’re comfortable spending, which is why you need to determine the monthly payment you feel comfortable with before talking to a lender. This likely includes doing a full household budget and taking into consideration what changes other than a mortgage payment will occur once you move into your new home. If you’ve lived in an apartment or with roommates, you may overlook new expenses like garbage, water, or HOA fees that could easily blow your budget."),
 ("Get prequalified", "Just because you think you can afford a certain payment every month doesn’t mean the mortgage company will agree. Just as they may approve you for too large of an amount, they may also approve you for a lesser amount or deny you a mortgage altogether. Lack of time at a job, insufficient credit, past bankruptcies, or other financial issues can cause major problems when trying to secure a mortgage. Before you get your heart set on a home, talk to a mortgage professional to find out what amount you can qualify for. This will also be an advantage when you make an offer on a home, as some sellers won’t entertain offers from those who aren’t already prequalified for a loan."),
 ("Choose a real estate agent", "Can you shop for, look at, and ultimately make an offer on a home without a real estate agent? Technically yes, but why would you when it costs you nothing for agents like us to take much of the stress off your shoulders? Not only will we help identify properties you might be interested in, arrange showings, and ultimately handle the offer process, but we also have a knowledge of the market that you don’t possess. Finding the perfect home can be a daunting task, this is where our expertise and wealth of knowledge come into play. Let us show you around some homes that meet your dream home criteria so you can find the one that's right for you."),
 ("Find the right home", "This should be the most enjoyable step of the entire process (other than moving in!). We will arrange showings of homes you’re interested in that are within your price range. Take notes about what you like and don’t like, and make sure to pay attention to details. Turn light switches on and off, open and close doors, and run the faucets in various rooms. Don’t limit your inspection to the home itself. Make sure to take time to explore the neighborhood and keep an eye on traffic at certain times of the day, the parking situation, and how close it is to necessities like schools and grocery stores."),
 ("Make an offer", "Once you have selected the perfect home, work with your agent to craft a fair offer based on the value of comparable homes on the market. Depending on what the home is listed at and whether the current environment is a buyer’s or seller’s market, your offer may be below, at, or even above the asking price. We will be able to help you negotiate if you receive a counteroffer and reach an agreement. At this point, the house will go into escrow."),
 ("Have the home inspected", "In most cases, your offer will be contingent on having the home inspected to ensure there is no major structural damage or large repairs needed. We can help you arrange this, and you can schedule it within days of making an offer. If there are no major issues, the process goes to step eight. If there is, you can renegotiate your offer based on what needs to be fixed, or you can withdraw it."),
 ("Select your loan", "Now is the time to go back to the mortgage lender who pre-approved or pre-qualified you and choose your mortgage. You will be presented with various options based on your unique financial situation, including fixed-rate, variable-rate, 15-year, 30-year, or special programs such as VA loans or FHA loans. Work with your mortgage lender to select the option you feel the most comfortable with."),
 ("Get a home appraisal", "Your lender will have your new home appraised so they have their independent value of it. The appraisal is to ensure that all parties involved are paying a fair price for the house."),
 ("Finish paperwork", "No one looks forward to all the paperwork involved in buying a home, but it’s a necessary part of the process. Fortunately, everything will be arranged by your lender and title company and, when you’re finished, you’ll know you are the legal owner of your new home."),
]
SELL_STEPS = [
 ("Understand why you're selling", "What do you want to accomplish with the sale of your home? Do you want to make a certain amount of money that you can put toward a larger or nicer home? Do you need to sell it as soon as possible to facilitate a move to a new city or area? Once you understand your needs, you can better craft your offer. For example, if you need to sell quickly, you might want to price your home lower than if your goal is to make a certain profit margin. Make sure you convey these needs to your team of real estate agents once you choose one so they can adjust your selling price accordingly."),
 ("Determine selling price", "Knowing how to price your home is one of the most important parts of the selling process. When you set a fair price in the beginning, you’ll get the most interest from other real estate agents and prospective buyers. Overpricing your home could lead to reduced interest, and underpricing leads to receiving less than what your home is worth. Working with a team of real estate agents is the best way to determine the right selling price for your home. An experienced team can determine what other comparable homes are selling for, evaluate the current market, and may even suggest a home appraisal."),
 ("Start preparations", "If you’ve kept your home in showroom condition since you’ve lived in it, you’re in the minority of homeowners. Once you price your home, it’s time to start getting it ready to be shown to potential buyers. This includes getting rid of clutter, depersonalizing the space so that buyers can envision themselves in the space, making any small repairs, and doing a deep clean to make sure your home is in pristine condition."),
 ("Develop a marketing strategy", "We will develop a marketing strategy that is perfect for advertising your home. This involves listing the home and then driving the right people to that listing through social media campaigns, agent-to-agent referrals, traditional media, or SEO advertising. Our team creates a marketing campaign that aims to get the most possible traffic to your listing in the first three weeks after becoming a client."),
 ("Evaluate offers", "Receiving an offer is an exciting part of the process, but it doesn’t mean the journey is over. We will evaluate each offer and make sure the party making the offer is prequalified or pre-approved by a mortgage lender and that their offer is acceptable to you. If the offer is too low, you can make a counter-offer or offer other ways to bridge the gap, such as covering some or all of the closing costs, making repairs, adjusting the move-in date, or leaving some appliances or fixtures for the new buyer."),
 ("Accept an offer", "Once we deem the offer is acceptable, we will review the proposed contract to make sure it’s all in order and includes the necessary components such as deposit amount, down payment, financing, inspection rights and repair allowances, contingencies, settlement date, and a list of fees and who will pay them. When both parties have agreed to the terms, a final contract will be prepared by your team of real estate agents."),
 ("Get ready to close", "You have accepted an offer and are now very close to the end of your selling journey. But first, you and the buyer must make a list of what needs to be done before closing. In some cases, your home may need to be formally inspected, surveyed, and appraised. In other cases, major or minor repairs will need to be made before the house can close. We will head up efforts to develop and execute this list, get each action item paid for by the correct party, and make sure everything is in order by the closing date. A few days before the closing date, we will call the company closing the transaction to make sure everything is ready to go. If you haven’t done so already, you also need to make arrangements to move out of the home so the new buyer can take possession."),
 ("Close", "You’ve reached the last step in the seller’s process. When you close on a home you are selling, you are legally transferring ownership of the property to the new buyer. We will meet with the company closing the transaction to sign the final paperwork and go over any issues that have not yet been taken care of. During this time, you can also make plans with your team of real estate agents to handle final details such as canceling utilities, cable, and lawn or trash services, changing the name on accounts that the new owner is retaining and ensuring the new owner has instructions for all appliances that will remain in the home."),
]

# ------------------------------------------------------------ marks --------
def marks_row(light=False):
    sfx = "-light" if light else ""
    return (f'<div class="marks" aria-label="Affiliations"><img src="assets/logo-cb-mark{sfx}.png" alt="{BROKER}" width="740" height="468" loading="lazy">'
            f'<img src="assets/mark-realtor{sfx}.png" alt="REALTOR®" width="206" height="240" loading="lazy">'
            f'<img src="assets/mark-equal-housing{sfx}.png" alt="Equal Housing Opportunity" width="226" height="240" loading="lazy"></div>')

# -------------------------------------------------------------- helpers ----
NUMBER_WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve"}
def esc(s): return html.escape(s, quote=True)
def clean(path):
    """team.html -> /team, blog/index.html -> /blog, index.html -> /"""
    if path in ("index.html", ""): return "/"
    if path.endswith("/index.html"): return "/" + path[:-len("/index.html")]
    return "/" + (path[:-5] if path.endswith(".html") else path)
def canon(path): return SITE + clean(path)

_LOCAL = re.compile(r'((?:href|src|data-sc-src|data-sc-src-mobile|action)=")(?!https?:|//|/|#|mailto:|tel:|data:)([^"]*)"')
def absolutize(text):
    """Make every internal link root-relative and drop .html, so pages work at any depth (blog/...)."""
    def fix(m):
        url = m.group(2); frag = ""
        if "#" in url: url, frag = url.split("#", 1); frag = "#" + frag
        url = clean(url) if url.endswith(".html") else "/" + url
        return f'{m.group(1)}{url}{frag}"'
    return _LOCAL.sub(fix, text)

def head(title, desc, path, og="assets/kelley-headshot.jpg", extra=""):
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon(path)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/{og}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#012169">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23012169'/%3E%3Ctext x='16' y='22' text-anchor='middle' font-family='Georgia,serif' font-size='18' fill='%23CCB091'%3EKG%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+Display:ital,wght@0,400;0,500;1,400&family=Poppins:wght@300;400;500&display=swap">
<link rel="stylesheet" href="scrollcraft.css">
<link rel="stylesheet" href="griffin.css">
<noscript><link rel="stylesheet" href="no-script.css"></noscript>
{extra}"""

def bar():
    links = "".join(f'<a href="{h}">{esc(l)}</a>' for l, h in NAV)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="bar is-light">
  <a class="mark" href="index.html" aria-label="{NAME}, {TEAM}, {BROKER}, home"><img class="mark__navy" src="assets/logo-cb-mark.png" alt="" width="740" height="468"><img class="mark__light" src="assets/logo-cb-mark-light.png" alt="" width="740" height="468"><span class="mark__rule" aria-hidden="true"></span><span class="mark__text"><span class="mark__name">Kelley Griffin</span><span class="mark__team">The Griffin Team</span></span></a>
  <nav class="bar__links" aria-label="Primary">{links}</nav>
  <a class="cta" href="contact.html">{CTA}</a>
  <details class="mobile-nav">
    <summary>Menu</summary>
    <nav aria-label="Primary mobile">{links}<a class="cta cta--solid" href="contact.html">{CTA}</a></nav>
  </details>
</header>"""

def valley_rail(with_stops=True):
    stops = ""
    if with_stops:
        for p in PLACES:
            x, y = VALLEY_X[p["slug"]]
            stops += f'<g class="valley__stop" data-slug="{p["slug"]}" role="link" tabindex="0" aria-label="Jump to {esc(p["name"])} in Six places"><circle cx="{x}" cy="{y}" r="2.2"/><text x="{x}" y="{max(y-6, 7)}" text-anchor="middle">{esc(p["name"]).replace("The ", "")}</text></g>'
    return f"""<div class="valley" aria-hidden="{'false' if with_stops else 'true'}">
  <div class="valley__inner">
    <svg viewBox="0 0 1000 40" preserveAspectRatio="none" aria-label="The Grand Valley skyline, west to east: Loma, Fruita, the Redlands, Grand Junction, Palisade, the Grand Mesa" role="img">
      <defs><linearGradient id="vfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="currentColor" stop-opacity="0.22"/><stop offset="1" stop-color="currentColor" stop-opacity="0.02"/></linearGradient></defs>
      <path class="valley__ground" d="{VALLEY_D} L1000,40 L0,40 Z" fill="url(#vfill)"/>
      <path class="valley__profile" d="{VALLEY_D}"/>
      <path class="valley__drawn" d="{VALLEY_D}"/>
      {stops}
      <circle class="valley__sun" cx="0" cy="34" r="4"/>
      <circle class="valley__head" cx="0" cy="34" r="2.2"/>
    </svg>
  </div>
</div>"""

def foot_inner():
    links = "".join(f'<a href="{h}">{esc(l)}</a>' for l, h in NAV + [("Contact", "contact.html"), ("Privacy", "privacy.html")])
    return f"""<div class="foot__row">
    <img class="foot__logo" src="assets/logo-cb-griffin-team-light.png" alt="{BROKER} and {TEAM}" width="1920" height="498">
    <nav class="foot__nav" aria-label="Footer">{links}</nav>
  </div>
  <div class="foot__row">
    <p style="margin:0">{NAME}, REALTOR®, {TITLE_LINE} · {BROKER} · {ADDR1}, {CITY} · Mobile {PHONE} · Office {OFFICE} · {EMAIL}</p>
    {marks_row(light=True)}
  </div>
  <p class="foot__legal">© {YEAR} {NAME}, {TEAM}. Coldwell Banker and the Coldwell Banker logo are trademarks of Coldwell Banker Real Estate LLC. The Coldwell Banker® System is comprised of company owned offices which are owned by a subsidiary of Anywhere Advisors LLC and franchised offices which are independently owned and operated. Affiliated real estate agents are independent contractor sales associates, not employees. The Coldwell Banker System fully supports the principles of the Fair Housing Act and the Equal Opportunity Act. REALTOR® is a registered collective membership mark of the National Association of REALTORS®; Kelley Griffin is a member of the Grand Junction Area REALTOR® Association. Colorado license {LICENSE}.</p>"""

def site_foot():
    return f'<footer class="site-foot"><div class="sc-wrap"><div class="foot">{foot_inner()}</div></div></footer>'

SCRIPTS = """<script src="scrollcraft.js"></script>
<script>ScrollCraft.mount(document.body);</script>
<script src="griffin.js"></script>"""

def document(title, desc, path, body, extra_head="", valley=True, dark_first=False):
    return f"""<!doctype html>
<html lang="en">
<head>
{head(title, desc, path, extra=extra_head)}
</head>
<body>
{body}
{SCRIPTS}
</body>
</html>
"""

def write(path, html_text):
    out = OUT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(absolutize(html_text), encoding="utf-8")

# ---------------------------------------------------------------- home ----
def home_body():
    ways = [
      ("Buying", "First home or fifth, we sort the listings against your wants-and-needs list, set up the showings, and handle every contract and signature until the keys are yours. Need a lender? We know the ones past clients loved.", "buyers-guide.html", "Buyer's guide", "listing-353-belden.jpg", "A tan stucco home with a red tile roof, a green lawn and mature shade trees on Belden Avenue"),
      ("Selling", "A current market analysis at no cost, then a marketing plan that puts your home in front of the right buyers in its first three weeks on the market. Pricing, offers, inspections and closing, handled.", "sellers-guide.html", "Seller's guide", "listing-2229-canyon-rim.jpg", "A white home on open land in the Redlands, with the red cliffs of the Colorado National Monument behind it"),
      ("Building and land", "New construction, vacant lots and farmland are a specialty. Dane's years as a residential general contractor mean the questions about lots, builders and timelines get real answers.", "contact.html", "Ask about a lot", "listing-358-canyon-rim.jpg", "Aerial view of new homesites along a curving road in the Redlands, under the red cliffs of the Colorado National Monument"),
    ]
    rail = ""
    for i, (h, p, href, label, pic, alt) in enumerate(ways):
        rail += f"""
        <a class="help" href="{href}">
          <div class="help__pic"><img src="assets/{pic}" alt="{esc(alt)}" width="1600" height="900" loading="lazy"></div>
          <h3>{h}</h3>
          <p>{p}</p>
          <span class="link">{label}</span>
        </a>"""
    placecards = ""
    for p in PLACES:
        placecards += f"""
        <li><a class="placecard" id="place-{p['slug']}" href="neighborhood-{p['slug']}.html">
          <span class="placecard__name">{esc(p['name'])}</span><span class="placecard__line">{esc(p['line'])}</span><span class="placecard__elev">{esc(p['elev'])}</span><span class="placecard__go" aria-hidden="true">&rarr;</span>
        </a></li>"""
    big = REVIEWS[3][1]
    big_excerpt = "We probably walked through 50 homes with her, and not once did she show an ounce of frustration or impatience. Instead, she listened carefully, learned what really mattered to us, and ultimately found the perfect home for us."
    small = [(REVIEWS[0][0], REVIEWS[0][1]), (REVIEWS[1][0], REVIEWS[1][1]),
             (REVIEWS[2][0], "She spent countless hours walking houses with us, helped us navigate offers and stuck with us through a 3 month closing. Not to mention she helped save us when our original mortgage broker dropped us.")]
    smalls = "".join(f'<blockquote class="quote quote--small"><p>{esc(t)}</p><footer>{esc(n)}</footer></blockquote>' for n, t in small)
    ld = {
      "@context": "https://schema.org", "@type": "RealEstateAgent",
      "name": f"{NAME}, {TEAM}", "alternateName": TEAM, "url": f"{SITE}/",
      "image": f"{SITE}/assets/kelley-headshot.jpg", "telephone": PHONE_TEL, "email": EMAIL,
      "address": {"@type": "PostalAddress", "streetAddress": ADDR1, "addressLocality": "Grand Junction", "addressRegion": "CO", "postalCode": "81501", "addressCountry": "US"},
      "areaServed": ["Fruita, CO", "Loma, CO", "Redlands, Grand Junction, CO", "Grand Junction, CO", "Palisade, CO", "Grand Mesa, CO"],
      "memberOf": {"@type": "Organization", "name": BROKER},
      "employee": {"@type": "Person", "name": NAME, "jobTitle": f"{TITLE_LINE}, {BROKER}", "telephone": PHONE_TEL, "email": EMAIL, "url": canon("team.html")},
      "knowsAbout": ["New construction", "First-time home buyers", "Vacant land", "Residential real estate in the Grand Valley"],
    }
    return f"""{bar()}
<span data-sc-progress></span>
<main id="main" tabindex="-1">

  <!-- 1 · ARRIVAL: the valley from the air, playing quietly behind the headline. Normal scrolling. -->
  <section class="hero calm-hero ground--dark" data-ground="dark">
    <img class="calm-hero__media" src="assets/hero-orchard-aerial.jpg" alt="" width="1600" height="900" fetchpriority="high">
    <video class="calm-hero__media calm-hero__video" data-src="motion/hero-loop.mp4" data-src-mobile="motion/hero-loop-m.mp4" muted loop playsinline preload="none" aria-hidden="true"></video>
    <div class="calm-hero__scrim" aria-hidden="true"></div>
    <figure class="hero__card calm-hero__card">
      <img src="assets/kelley-headshot.jpg" alt="{NAME}, {TITLE_LINE}" width="1200" height="1200" fetchpriority="high">
      <figcaption><span>{NAME}</span><span>REALTOR® · {TITLE_LINE} · {BROKER}</span></figcaption>
    </figure>
    <div class="calm-hero__copy">
      <p class="hero__who">Fruita · Grand Junction · the Grand Valley</p>
      <h1 class="sc-display">Real estate for the valley we call home.</h1>
      <p class="hero__lede">Buying, selling, building and land, with a Colorado native who has lived here since 2008 and sold homes in every corner of it.</p>
      <div class="hero__actions"><a class="cta cta--solid" href="contact.html">{CTA}</a><a class="cta" href="team.html">Meet Kelley</a></div>
    </div>
  </section>

  <!-- 2 · THE PERSON -->
  <section class="meet sc-section" data-sc-act="flow">
    <div class="sc-wrap meet__grid">
      <div class="meet__copy" data-sc-in data-sc-stagger="110">
        <p class="meet__kicker">Meet Kelley</p>
        <p>A Colorado native who has called the <em>Grand Valley</em> home since 2008.</p>
        <p>More than ten years in real estate: <em>new construction</em>, first homes, cabins on the Mesa, historic downtown.</p>
        <p>Before that, marketing and public relations. It shows in <em>how a home gets sold.</em></p>
        <p>Three boys, one dog, and a husband who <em>builds houses.</em></p>
      </div>
      <div class="meet__pics">
        <figure class="meet__pic-a" data-sc-in><img src="assets/kelley-dane.jpg" alt="Kelley and Dane Griffin smiling together, dressed up for an evening out" width="1200" height="1600" loading="lazy"></figure>
        <figure class="meet__pic-b" data-sc-in><img src="assets/griffin-family-garden.jpg" alt="The Griffin family, five of them, in a garden among pink flowers" width="1600" height="1926" loading="lazy"></figure>
      </div>
    </div>
  </section>

  <!-- 3 · WHAT SETS US APART: her own words, and only real numbers -->
  <section class="apart sc-section" data-sc-act="flow">
    <div class="sc-wrap">
      <div class="apart__grid" data-sc-in data-sc-stagger="80">
        <h2 class="sc-display">What sets us apart?</h2>
        <div>
          <p class="sc-body">We’ve called the Grand Valley home since 2008, and we truly live the lifestyle we sell. From hiking and biking trails to hidden outdoor gems, we know this community inside and out. With Dane’s background as a residential general contractor, we bring a deep understanding of new construction and vacant land opportunities to every transaction. As a small, hands-on team, we’re with our clients from start to finish: no handoffs, no confusion, just clear communication and a seamless experience every step of the way.</p>
          <div class="apart__links"><a class="link" href="team.html">The whole story</a><a class="link" href="sold.html">Recent sales</a></div>
        </div>
      </div>
      <ul class="ledger" data-sc-in data-sc-stagger="90">
        <li><span class="ledger__n">2008</span><span class="ledger__l">the year the family moved to the Grand Valley from Fort Collins, and it has been home ever since</span></li>
        <li><span class="ledger__n">10<small>+</small></span><span class="ledger__l">years licensed, from new builds and farmland to cabins on the Mesa and historic downtown</span></li>
        <li><span class="ledger__n">1</span><span class="ledger__l">general contractor in the family, so questions about lots, builders and timelines get real answers</span></li>
      </ul>
    </div>
  </section>

  <!-- 4 · SIX PLACES: the valley, west to east -->
  <section class="places ground--dark" data-ground="dark" data-sc-act="flow">
    <div class="sc-wrap">
      <div class="places__head" data-sc-in>
        <h2 class="sc-display">Six places. One valley.</h2>
        <p>West to east, the places Kelley helps people buy and sell.</p>
      </div>
      <div class="places__grid">
        <figure class="places__pic" data-sc-in><img src="assets/valley-from-monument.jpg" alt="Independence Monument and the red canyons of the Colorado National Monument, with the Grand Valley spread out beyond" width="1600" height="1000" loading="lazy"></figure>
        <ol class="places__list" data-sc-in data-sc-stagger="70">{placecards}
        </ol>
      </div>
    </div>
  </section>

  <!-- 5 · HOW SHE HELPS -->
  <section class="helps sc-section" data-sc-act="flow">
    <div class="sc-wrap">
      <p class="meet__kicker" data-sc-in>Three ways Kelley helps</p>
      <div class="helps__grid" data-sc-in data-sc-stagger="90">{rail}
      </div>
    </div>
  </section>

  <!-- 6 · CLIENT WORDS -->
  <section class="words sc-section" data-sc-act="flow">
    <div class="sc-wrap">
      <div class="words__grid">
        <blockquote class="quote quote--big" data-sc-in>
          <p>{esc(big_excerpt)}</p>
          <footer>Ross B., first-time buyers, 2025</footer>
        </blockquote>
        <div class="words__side" data-sc-in data-sc-stagger="90">{smalls}</div>
      </div>
      <div class="words__more" data-sc-in><span class="sc-label">In their own words</span><a class="link" href="testimonials.html">All client words</a></div>
    </div>
  </section>

  <!-- 7 · THE CLOSE -->
  <section id="talk" class="close close--calm ground--dark" data-ground="dark" data-sc-act="flow">
    <div class="close__inner" data-sc-in data-sc-stagger="90">
      <h2 class="sc-display">Let’s talk about your next move.</h2>
      <div class="close__line">
        <span><strong>{NAME}</strong>, REALTOR®, {TITLE_LINE}, {BROKER}</span>
        <span>{ADDR1}, {CITY}</span>
        <span>Mobile <a href="tel:{PHONE_TEL}">{PHONE}</a> · Office <a href="tel:{OFFICE_TEL}">{OFFICE}</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></span>
      </div>
      <a class="cta cta--solid" href="contact.html">{CTA}</a>
    </div>
    <footer class="foot">{foot_inner()}</footer>
  </section>
</main>
{valley_rail(True)}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>"""

# ---------------------------------------------------------- inner pages ----
def page_shell(title, desc, path, hero_html, body_html, extra_head=""):
    photo = "page-hero--photo" in hero_html
    body = f"""{bar()}
<span data-sc-progress></span>
<main id="main" tabindex="-1" class="page{' page--photo' if photo else ''}">
{hero_html}
{body_html}
</main>
{site_foot()}
{extra_head}"""
    return document(title, desc, path, body)

def page_hero(label, h1, lede="", photo=None, alt=""):
    if photo:
        return f"""<section class="page-hero page-hero--photo ground--dark" data-ground="dark"><img class="bg" src="assets/{photo}" alt="{esc(alt)}" width="{img_size(photo)[0]}" height="{img_size(photo)[1]}" fetchpriority="high"><div class="scrim" aria-hidden="true"></div>
  <div class="sc-wrap"><p class="sc-label">{esc(label)}</p><h1 class="sc-display">{h1}</h1>{f'<p class="sc-lede">{lede}</p>' if lede else ''}</div></section>"""
    return f"""<section class="page-hero"><div class="sc-wrap"><p class="sc-label">{esc(label)}</p><h1 class="sc-display">{h1}</h1>{f'<p class="sc-lede">{lede}</p>' if lede else ''}</div></section>"""

def cta_band(h="Ready when you are.", p="Buying or selling is a big deal. Kelley guides you through every step with clarity, confidence, and communication you can count on."):
    return f"""<section class="band band--navy"><div class="sc-wrap split" style="align-items:center"><div data-sc-in><h2 class="sc-display sc-display--md">{h}</h2><p class="sc-body" style="margin-top:1rem">{p}</p></div><div style="display:flex;gap:1rem;flex-wrap:wrap;justify-content:flex-start" data-sc-in><a class="cta cta--solid" href="contact.html">{CTA}</a><a class="cta" href="tel:{PHONE_TEL}">{PHONE}</a></div></div></section>"""

def steps_html(steps):
    out = '<div class="steps">'
    for i, (h, p) in enumerate(steps, 1):
        out += f'<div class="step" data-sc-in><div class="step__n">{i:02d}</div><div><h3>{esc(h)}</h3><p>{esc(p)}</p></div></div>'
    return out + "</div>"

def build_team():
    ld = {"@context": "https://schema.org", "@type": "Person", "name": NAME, "jobTitle": f"{TITLE_LINE}, {BROKER}", "telephone": PHONE_TEL, "email": EMAIL,
          "image": f"{SITE}/assets/kelley-headshot.jpg", "url": canon("team.html"), "worksFor": {"@type": "Organization", "name": BROKER},
          "address": {"@type": "PostalAddress", "streetAddress": ADDR1, "addressLocality": "Grand Junction", "addressRegion": "CO", "postalCode": "81501"},
          "alumniOf": "Colorado State University", "knowsAbout": ["New construction", "First-time home buyers", "Vacant land", "Fruita, CO", "Grand Junction, CO"]}
    body = f"""
<section class="sc-section" style="padding-top:0"><div class="sc-wrap split split--sticky">
  <figure data-sc-in><img src="assets/kelley-headshot-navy.jpg" alt="Kelley Griffin in a navy blazer, smiling outdoors" width="1500" height="1500"></figure>
  <div class="prose" data-sc-in data-sc-stagger="60">
    <h2>Get to know me</h2>
    <p>Hello! We are so excited to meet you and help you through your next real estate transaction. We are locals who LOVE where we live. We love spending time outside, and when we are not working (or chasing kids) you'll find us on mountain bikes, skis, or hiking with our dog. We also have a passion for travel!</p>
    <p>We met while attending Colorado State University in Fort Collins. We married in 2008 and immediately moved to Grand Junction. We have since visited and lived in several countries, but the Grand Valley is definitely "home". We are parents to three boys (twins and a singleton) who make sure there is never a dull moment in our household!</p>
    <p>Dane has a background in Construction Management, and is the owner of Griffin Design and Construction, LLC. Along with building residential homes, he also has experience managing international aquarium projects in Russia, Korea and the UK.</p>
    <p>Kelley's background is in Public Relations, Event Planning and Marketing. She has done events and marketing for organizations in Fort Collins, Loveland, Grand Junction and Fruita. Since getting her real estate license, she has managed transactions for new construction, mobile homes, vacant farmland, cabins on the Mesa and historic downtown homes.</p>
    <h2>Why it works</h2>
    <p>For Kelley Griffin, real estate is about more than finding the right home. It's about helping people build a life they love. A Colorado native with more than 10 years of real estate experience, Kelley has built her business on trust, exceptional service, and deep local knowledge of the Grand Valley. She specializes in new construction, first-time homebuyers, and residential properties of all kinds, helping clients navigate every step of the buying and selling process with confidence.</p>
    <p>Before real estate, Kelley built a career in marketing, public relations, and event planning. Today, those skills allow her to strategically market homes, negotiate effectively, and deliver a seamless client experience from start to finish.</p>
    <h2>Contact details</h2>
    <ul class="facts-list">
      <li><span>Name</span><span>{NAME}, REALTOR®, {TITLE_LINE}</span></li>
      <li><span>Brokerage</span><span>{BROKER}</span></li>
      <li><span>Office</span><span>{ADDR1}<br>{CITY}</span></li>
      <li><span>Mobile</span><span><a href="tel:{PHONE_TEL}">{PHONE}</a></span></li>
      <li><span>Office line</span><span><a href="tel:{OFFICE_TEL}">{OFFICE}</a></span></li>
      <li><span>Email</span><span><a href="mailto:{EMAIL}">{EMAIL}</a></span></li>
      <li><span>License</span><span>Colorado {LICENSE}</span></li>
    </ul>
    <div style="margin-top:2rem">{marks_row()}</div>
  </div>
</div></section>
<section class="band"><div class="sc-wrap split" style="align-items:center">
  <figure data-sc-in style="box-shadow:none"><img src="assets/griffin-family-terrace.jpg" alt="The Griffin family of five on a stone terrace overlooking a historic city" width="1600" height="1200" loading="lazy"></figure>
  <div class="prose" data-sc-in><h2>The Griffin Team</h2><p>A small, hands-on team: Kelley on the real estate, Dane on the building side when a lot, a plan or a timeline needs a contractor's eye. With our clients from start to finish. No handoffs, no confusion, just clear communication and a seamless experience every step of the way.</p><a class="link" href="testimonials.html">What clients say</a></div>
</div></section>
<section class="sc-section"><div class="sc-wrap split dane" style="align-items:center">
  <div class="prose" data-sc-in><p class="sc-label">The building side</p><h2>Dane Griffin</h2><p>Dane owns Griffin Design and Construction, LLC and builds residential homes. When a client is weighing a lot, a floor plan or a builder's timeline, he is the contractor's eye on the team, so the questions about land, builders and schedules get real answers.</p><a class="link" href="contact.html">Ask about building</a></div>
  <figure class="dane__pic" data-sc-in><img src="assets/dane-headshot.jpg" alt="Dane Griffin, smiling outdoors beside a tree in a light button-down shirt" width="1200" height="1800" loading="lazy"></figure>
</div>
<div class="sc-wrap"><div class="photo-row photo-row--lead" data-sc-in>
  <figure style="--ar:1.333"><img src="assets/build-framing.jpg" alt="A two-story home under construction, wrapped in house wrap with its stucco half finished" width="1600" height="1200" loading="lazy"></figure>
  <figure style="--ar:0.75"><img src="assets/build-young-crew.jpg" alt="Two young boys in hoodies hammering nails into a new wood subfloor" width="1200" height="1600" loading="lazy"></figure>
  <figure style="--ar:0.75"><img src="assets/build-finished-interior.jpg" alt="A finished open living room and kitchen in a Griffin Design and Construction home, with dark cabinets, a linear fireplace and wood floors" width="1200" height="1600" loading="lazy"></figure>
</div><p class="photo-row__cap" data-sc-in>From framing to finish, with help from the youngest members of the crew.</p></div></section>
<section class="band"><div class="sc-wrap"><div class="prose" style="max-width:40rem;margin-inline:auto;text-align:center" data-sc-in><p class="sc-label">Off the clock</p><h2>Bikes, skis and a passport</h2></div>
<div class="photo-row photo-row--life" data-sc-in>
  <figure style="--ar:0.75"><img src="assets/kelley-biking-fruita.jpg" alt="Kelley Griffin in a bike helmet and sunglasses, smiling on a rocky ridge high above the Colorado River near Fruita" width="1200" height="1600" loading="lazy"></figure>
  <figure style="--ar:1.333"><img src="assets/powderhorn-ski-day.jpg" alt="Young skiers and snowboarders lined up by the trail map at Powderhorn among bare aspens" width="1600" height="1200" loading="lazy"></figure>
  <figure style="--ar:0.75"><img src="assets/kelley-dane-japan.jpg" alt="Kelley and Dane Griffin smiling in a selfie on a narrow lantern-lined street abroad" width="1200" height="1600" loading="lazy"></figure>
</div></div></section>
{cta_band()}"""
    write("team.html", page_shell(f"Meet Kelley Griffin | {TEAM}, {BROKER}", f"Kelley Griffin is a Broker Associate with {BROKER} in Grand Junction, Colorado: a Colorado native, in the Grand Valley since 2008, more than 10 years in real estate, specializing in new construction and first-time buyers.", "team.html",
        page_hero("Meet Kelley", f"{NAME}", f"REALTOR®, {TITLE_LINE}, {BROKER}. Fruita, Grand Junction and the Grand Valley."), body,
        extra_head=f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'))

def build_guides():
    bbody = f"""
<section class="sc-section" style="padding-top:0"><div class="sc-wrap split split--sticky">
  <figure data-sc-in><img src="assets/listing-2521-woody-creek.jpg" alt="Aerial view of a new-home neighborhood in Grand Junction, with an open homesite in front and the Book Cliffs on the horizon" width="1024" height="682" loading="lazy"></figure>
  <div class="prose" data-sc-in data-sc-stagger="60">
    <h2>Ready to buy?</h2>
    <p>Buying a home is exciting! But it can also be stressful and time consuming. We will use your "wants and needs" list to help you sort through available listings, set up and attend showings, and provide you with relevant information about the different properties. We will continue this process until you find "the one". At this point we will help with all of the contracts and paperwork necessary to complete the transaction.</p>
    <p>In today's fast-paced market, it is often important to be pre-approved by a lender prior to submitting an offer. If you are not sure where to start, give us a call and we can help! There are many fantastic lenders in town, and we can recommend a few that past clients have really loved. Knowing what your budget is will make you more comfortable and confident as you look at homes since you will know what to expect for a monthly mortgage.</p>
    <p>So are you ready to start looking? Please call us today and we will start searching!</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem"><a class="cta cta--solid" href="contact.html">{CTA}</a><a class="cta" href="sellers-guide.html">Seller's guide</a></div>
  </div>
</div></section>
<section class="band"><div class="sc-wrap"><div class="prose" style="max-width:52rem" data-sc-in><h2>A step-by-step first-time buyer's guide</h2><p>Buying a home is one of the most exciting milestones of your life. To prepare yourself for this moment, you need to know what to expect during the process. This step-by-step first time buyer’s guide created by our team will help reduce the stress of buying a home and help you enjoy the journey as much as possible.</p></div>
<div style="max-width:52rem;margin-top:3rem">{steps_html(BUY_STEPS)}</div>
<div class="prose" style="max-width:52rem;margin-top:3rem" data-sc-in><h3>Congratulations!</h3><p>After signing the final paperwork to complete the purchase, you are now the owner of a new house. It may take a few days for your loan to be funded once the paperwork has been returned to the lender, but once that check is delivered to the seller, you’ll be all set to move into the home of your dreams.</p></div></div></section>
{cta_band("Our goal is personalized service, designed to help you buy your dream home.", "Schedule a consultation and we will start the search together.")}"""
    write("buyers-guide.html", page_shell(f"Buyer's Guide to Buying a Home in the Grand Valley | {TEAM}", "A step-by-step buyer's guide from Kelley Griffin, Coldwell Banker Distinctive Properties: research, budget, pre-approval, showings, offers, inspection, loan, appraisal and closing in Fruita and Grand Junction.", "buyers-guide.html",
        page_hero("Buying", "Step-by-step buyer's guide", "From the wants-and-needs list to the keys in your hand.", photo="fruita-desert-aerial.jpg", alt="Aerial view of desert singletrack winding across the mesas outside Fruita"), bbody))
    sbody = f"""
<section class="sc-section" style="padding-top:0"><div class="sc-wrap split split--sticky">
  <figure data-sc-in><img src="assets/kelley-dane-selfie.jpg" alt="Kelley and Dane Griffin smiling in a selfie on a sunny mountain trail" width="1200" height="1600" loading="lazy"></figure>
  <div class="prose" data-sc-in data-sc-stagger="60">
    <h2>Ready to sell?</h2>
    <p>There are many reasons you may be considering selling your home. Maybe it is time to find a larger home, downsize as kids move away, or move for a new job. For many sellers, the decision to sell often comes down to what their home is worth. Values are constantly changing, but we can provide you with a current market analysis (CMA) so that you can see your home's value in today's market.</p>
    <p>We will get some basic information about your home and compare it to homes that have recently sold in your area to see what your home could potentially sell for. We are happy to offer this service at no cost.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem"><a class="cta cta--solid" href="contact.html">Ask for a home valuation</a><a class="cta" href="buyers-guide.html">Buyer's guide</a></div>
  </div>
</div></section>
<section class="band"><div class="sc-wrap"><div class="prose" style="max-width:52rem" data-sc-in><h2>A step-by-step seller's guide</h2><p>Putting your home on the market can be a stressful process, especially when you don’t know what to expect. Fortunately, with the help of an experienced team of real estate agents and this easy to follow guide, you can smoothly complete the process. Following these steps will help you prepare so you can get organized and sell your home for the best price possible.</p></div>
<div style="max-width:52rem;margin-top:3rem">{steps_html(SELL_STEPS)}</div>
<div class="prose" style="max-width:52rem;margin-top:3rem" data-sc-in><h3>Congratulations!</h3><p>Once you have sold your home, you’re free to take the next step on your journey. Whether this is relocating to a new city, moving into a larger home, or downsizing and enjoying your life as empty-nesters, knowing all your selling responsibilities have been taken care of will help you achieve peace of mind for your new path.</p></div></div></section>
{cta_band("Know what your home is worth.", "A current market analysis, at no cost, from someone who has sold homes in every corner of the valley.")}"""
    write("sellers-guide.html", page_shell(f"Seller's Guide to Selling Your Home | {TEAM}", "A step-by-step seller's guide from Kelley Griffin, Coldwell Banker Distinctive Properties: pricing, preparation, marketing, offers and closing, plus a free current market analysis for Grand Valley homes.", "sellers-guide.html",
        page_hero("Selling", "Comprehensive seller's guide", "Pricing, preparation, marketing and closing, with a free market analysis to start.", photo="mesa-fall-overlook.jpg", alt="Golden aspens and dark spruce on the Grand Mesa in fall, with a lake far below"), sbody))

def build_neighborhoods():
    cards = ""
    for i, p in enumerate(PLACES, 1):
        cards += f'<a class="card card--type" href="neighborhood-{p["slug"]}.html" data-sc-in><span class="card__n">{i:02d}</span><h3>{esc(p["name"])}</h3><p>{esc(p["blurb"])}</p><span class="sc-label">{esc(p["elev"])}</span><span class="link">Explore {esc(p["name"].replace("The ", "the "))}</span></a>'
    body = f"""<section class="sc-section" style="padding-top:0"><div class="sc-wrap"><div class="cards" data-sc-stagger="70" data-sc-in>{cards}</div></div></section>{cta_band("Which one is yours?", "Tell Kelley how you want to live and she will tell you where in the valley that happens.")}"""
    write("neighborhoods.html", page_shell(f"Grand Valley Neighborhoods: Fruita, Redlands, Grand Junction, Loma, Palisade, Grand Mesa | {TEAM}", "Kelley Griffin's lifestyle guides to the Grand Valley: Fruita, the Redlands, Grand Junction, Loma, Palisade and the Grand Mesa. Recreation, amenities, attractions and why people love each one.", "neighborhoods.html",
        page_hero("Neighborhoods", "Six places. One valley.", "West to east, the places Kelley helps people buy and sell.", photo="mesa-view-bookcliffs.jpg", alt="Looking down from the Grand Mesa across the valley to the Book Cliffs on a winter afternoon"), body))
    for i, p in enumerate(PLACES):
        prev_ = PLACES[i-1] if i > 0 else PLACES[-1]; next_ = PLACES[(i+1) % len(PLACES)]
        def ul(items): return "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul>"
        nm = p['name'].replace('The ', 'the ')
        facet = lambda h, items: f'<div class="facet"><h3>{h}</h3>{ul(items)}</div>'
        nav = "".join(f'<a class="nbnav" href="neighborhood-{q["slug"]}.html"><span class="nbnav__k">{k}</span><span class="nbnav__n">{esc(q["name"])}</span></a>' for k, q in (("Previous", prev_), ("Next", next_)))
        body = f"""
<section class="sc-section nb-intro"><div class="sc-wrap nb-intro__grid">
  <div data-sc-in><p class="sc-label">Welcome to {esc(nm)}</p><p class="nb-intro__lede">{esc(p['blurb'])}</p></div>
  <dl class="nb-facts" data-sc-in><div><dt>Elevation</dt><dd>{esc(p['elev'])}</dd></div><div><dt>Known for</dt><dd>{esc(p['line'])}</dd></div><div><dt>Ask Kelley</dt><dd><a href="contact.html">Homes and land in {esc(nm)}</a></dd></div></dl>
</div></section>
<section class="sc-section nb-facets"><div class="sc-wrap"><div class="facets" data-sc-in data-sc-stagger="80">
  {facet("Outdoor recreation", p['rec'])}{facet("Local attractions", p['attr'])}{facet("Amenities", p['amen'])}{facet(f"Why people love {esc(nm)}", p['love'])}
</div><div class="nbnavs" data-sc-in>{nav}</div></div></section>
{cta_band(f"Thinking about {esc(nm)}?", "Kelley knows the streets, the builders and the trailheads. Start with a conversation.")}"""
        write(f"neighborhood-{p['slug']}.html", page_shell(f"{p['name']}, CO Real Estate and Lifestyle Guide | {TEAM}", f"{p['blurb']} A neighborhood guide from Kelley Griffin, {BROKER}.", f"neighborhood-{p['slug']}.html",
            page_hero("Neighborhood guide", esc(p['name']), esc(p['line']), photo=p['photo'], alt=p['alt']), body))

def build_testimonials():
    items = "".join(f'<blockquote class="tcard" data-sc-in><p>{esc(t)}</p><footer>{esc(n)}</footer></blockquote>' for n, t in REVIEWS)
    body = f"""<section class="sc-section" style="padding-top:0"><div class="sc-wrap"><div class="tcards">{items}</div></div></section>{cta_band()}"""
    write("testimonials.html", page_shell(f"Client Testimonials | {NAME}, {TEAM}", "What clients say about working with Kelley Griffin, Coldwell Banker Distinctive Properties, in Fruita and Grand Junction, Colorado.", "testimonials.html",
        page_hero("Client words", "What our clients say", f"{NUMBER_WORDS.get(len(REVIEWS), len(REVIEWS))} of the people Kelley has helped, in their own words.", photo="mesa-lake-sunset.jpg", alt="A lake on the Grand Mesa reflecting a pink and gold sunset"), body))

def build_sold():
    items = "".join(f'<div class="sale" data-sc-in><div class="sale__pic"><img src="assets/{pic}" alt="{esc(addr)}" width="{img_size(pic)[0]}" height="{img_size(pic)[1]}" loading="lazy"></div><div class="sale__price">{price}</div><div class="sale__addr">{esc(addr)}</div><div class="sale__meta">Sold · {esc(meta)}</div></div>' for price, addr, meta, pic in SOLD)
    body = f"""<section class="sc-section" style="padding-top:0"><div class="sc-wrap"><div class="sales" data-sc-stagger="60" data-sc-in>{items}</div><p class="form__note" style="margin-top:3rem">A selection of past transactions. Property information is derived from county records and the Multiple Listing Service and may include approximations; verify independently.</p></div></section>{cta_band("Know what your home is worth.", "A current market analysis, at no cost.")}"""
    write("sold.html", page_shell(f"Recent Sales in Fruita and Grand Junction | {TEAM}", "A selection of homes and land Kelley Griffin has sold across Fruita and Grand Junction, Colorado.", "sold.html",
        page_hero("Recent sales", "Past transactions", "Homes, lots and a commercial building, across the valley.", photo="mesa-lake-evening.jpg", alt="Evening sun over a calm lake on the Grand Mesa, with people fishing from the shore"), body))

def build_contact():
    body = f"""
<section class="sc-section" style="padding-top:0"><div class="sc-wrap split">
  <form class="form" id="contact-form" method="POST" action="{FORM_ENDPOINT}" data-send="{FORM_ENDPOINT_AJAX}">
    <input type="hidden" name="_subject" value="New message from your website">
    <input type="hidden" name="_template" value="table">
    <input type="hidden" name="_captcha" value="false">
    <input type="hidden" name="_next" value="{SITE}/thank-you">
    <p class="form__hp" hidden><label>Leave this empty<input name="_honey" tabindex="-1" autocomplete="off"></label></p>
    <div class="form__fields" style="display:grid;gap:1.5rem">
      <div class="form__row"><label for="f-name">Full name (required)<input id="f-name" name="name" type="text" required autocomplete="name"></label><label for="f-phone">Phone (optional)<input id="f-phone" name="phone" type="tel" autocomplete="tel"></label></div>
      <label for="f-email">Email (required)<input id="f-email" name="email" type="email" required autocomplete="email"></label>
      <label for="f-interest">What are you interested in?<select id="f-interest" name="interest"><option>Buying</option><option>Selling</option><option>Building or land</option><option>A home valuation</option><option>Area information</option></select></label>
      <label for="f-msg">Message (optional)<textarea id="f-msg" name="message" rows="5"></textarea></label>
      <p class="form__note">Your message goes straight to Kelley. She uses your details only to reply. <a href="privacy.html">Privacy policy</a>.</p>
      <div><button class="cta cta--solid" type="submit">Send message</button></div>
    </div>
        <div class="form__done" role="status" tabindex="-1"></div>
  </form>
  <div class="prose" data-sc-in data-sc-stagger="60">
    <h2>Or just call.</h2>
    <ul class="facts-list">
      <li><span>Mobile</span><span><a href="tel:{PHONE_TEL}">{PHONE}</a></span></li>
      <li><span>Office</span><span><a href="tel:{OFFICE_TEL}">{OFFICE}</a></span></li>
      <li><span>Email</span><span><a href="mailto:{EMAIL}">{EMAIL}</a></span></li>
      <li><span>Address</span><span>{BROKER}<br>{ADDR1}<br>{CITY}</span></li>
    </ul>
    <div style="margin-top:2rem">{marks_row()}</div>
    <figure style="margin:2.5rem 0 0"><img src="assets/kelley-dane-mesa-lake.jpg" alt="Kelley and Dane Griffin on the rocky shore of a lake on the Grand Mesa" width="1200" height="1600" loading="lazy" style="width:100%;height:auto;display:block"></figure>
  </div>
</div></section>"""
    write("contact.html", page_shell(f"Contact Kelley Griffin | {TEAM}, {BROKER}", f"Reach Kelley Griffin, Broker Associate with {BROKER}, at {PHONE} or {EMAIL}. Office at {ADDR1}, {CITY}.", "contact.html",
        page_hero("Contact", "Let’s talk about your next move.", "Buying or selling is a big deal. Kelley guides you through every step with clarity, confidence, and communication you can count on."), body))

def build_privacy():
    body = f"""<section class="sc-section" style="padding-top:0"><div class="sc-wrap"><div class="prose" data-sc-in>
<p>This policy explains what happens to information you share on thegriffinteam.com, the website of {NAME}, {TEAM}, {BROKER}.</p>
<h2>What we collect</h2><p>When you send the contact form, we receive the name, email, phone number, interest and message you type. We collect nothing else about you on purpose. Like every website host, ours keeps short-lived technical logs (such as IP address and browser type) to keep the site running and secure.</p>
<h2>How we use it</h2><p>Only to answer you and help with your real estate question. Your message is emailed to Kelley. We never sell or rent your information, and we do not add you to a mailing list unless you ask.</p>
<h2>Who else sees it</h2><p>Our website host, Netlify, and our form provider, FormSubmit, process form messages on our behalf to deliver them to Kelley. If you go on to work with Kelley, your details are shared with {BROKER} as part of the transaction and handled under its privacy practices.</p>
<h2>Cookies and tracking</h2><p>This site sets no advertising or tracking cookies. Fonts load from Google Fonts, which receives your IP address when your browser requests them.</p>
<h2>Your choices</h2><p>You can ask us to see, correct or delete the information you sent us at any time. Email {EMAIL} or call {PHONE} and we will take care of it.</p>
<h2>Children</h2><p>This site is not meant for children under 13, and we do not knowingly collect their information.</p>
<h2>Changes</h2><p>If this policy changes, the new version will be posted here with a new date.</p>
<h2>Fair housing</h2><p>{NAME} is committed to the letter and spirit of U.S. fair housing law and the Equal Opportunity Act. Information on this site is believed reliable but not guaranteed.</p>
</div></div></section>"""
    write("privacy.html", page_shell(f"Privacy Policy | {TEAM}", "Privacy policy for thegriffinteam.com, the website of Kelley Griffin, Coldwell Banker Distinctive Properties.", "privacy.html", page_hero("Privacy", "Privacy policy", "Last updated November 2026."), body))

def build_thank_you():
    body = f"""<section class="sc-section" style="padding-top:0"><div class="sc-wrap"><div class="prose" data-sc-in>
<p>Kelley will be in touch soon, usually the same day. If it can’t wait, call her at <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
<p><a class="cta cta--solid" href="index.html">Back to the home page</a></p>
</div></div></section>"""
    write("thank-you.html", page_shell(f"Thank you | {TEAM}", "Your message to Kelley Griffin was sent.", "thank-you.html", page_hero("Message sent", "Thank you.", "Your message is on its way to Kelley."), body))

def build_404():
    body = f"""<section class="sc-section" style="padding-top:0"><div class="sc-wrap"><div class="prose"><p>That page is not here. The valley is, though.</p><div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem"><a class="cta cta--solid" href="index.html">Home</a><a class="cta" href="neighborhoods.html">Neighborhoods</a></div></div></div></section>"""
    doc = page_shell("Page not found | The Griffin Team", "Page not found.", "404.html", page_hero("404", "Not found"), body)
    doc = doc.replace('<link rel="canonical" href="' + canon("404.html") + '">', '<meta name="robots" content="noindex">')
    write("404.html", doc)

# ------------------------------------------------------------------ run ----
home = document(f"{NAME}, {TEAM} | {BROKER} | Fruita and Grand Junction Real Estate",
    f"Kelley Griffin, Broker Associate with {BROKER}: buying, selling, new construction and land across Fruita, Grand Junction and the Grand Valley. A Colorado native, in the valley since 2008, more than 10 years in real estate.", "index.html", home_body())
write("index.html", home)
# ------------------------------------------------------------------ blog ----
# Each post is one file in content/blog/, named YYYY-MM-DD-slug.html (or .md).
# It starts with a short header between --- lines, then the post itself:
#   title, date (YYYY-MM-DD), slug (the web address: /blog/slug), description (one sentence for Google),
#   photo (a file in site/assets/, e.g. blog/my-photo.jpg), photo_alt (what the photo shows).
# Optional: draft: yes  (keeps it off the site until removed).
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def nice_date(d): return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"

def md_to_html(text):
    """Small Markdown reader for new posts: ## headings, paragraphs, - lists, **bold**, *italic*, [links](url), ![alt](photo)."""
    def inline(t):
        t = esc(t)
        t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", lambda m: f'<img src="assets/{m.group(2)}" alt="{m.group(1)}" loading="lazy">', t)
        t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*", r"<em>\1</em>", t)
        return t
    out, para, items = [], [], []
    def flush():
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para.clear()
        if items: out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>"); items.clear()
    for line in text.splitlines():
        l = line.strip()
        if not l: flush(); continue
        h = re.match(r"(#{2,4})\s+(.*)", l)
        if h: flush(); n = len(h.group(1)); out.append(f"<h{n}>{inline(h.group(2))}</h{n}>"); continue
        li = re.match(r"[-*]\s+(.*)", l)
        if li:
            if para: flush()
            items.append(li.group(1)); continue
        if items: flush()
        para.append(l)
    flush()
    return "\n".join(out)

def load_posts():
    posts = []
    for f in sorted((CONTENT / "blog").glob("*.*")):
        if f.suffix not in (".html", ".md"): continue
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
        if not m: raise SystemExit(f"{f.name}: missing the --- header at the top")
        meta = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); meta[k.strip()] = v.strip()
        for k in ("title", "date", "slug", "description"):
            if not meta.get(k): raise SystemExit(f"{f.name}: the header needs a '{k}:' line")
        if meta.get("draft", "").lower() in ("yes", "true"): continue
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["slug"]): raise SystemExit(f"{f.name}: slug must be lowercase words joined by hyphens")
        meta["when"] = datetime.date.fromisoformat(meta["date"])
        photo = meta.get("photo") or None
        if photo and not (OUT / "assets" / photo).exists(): raise SystemExit(f"{f.name}: photo site/assets/{photo} not found")
        meta["photo"] = photo
        meta["body"] = m.group(2) if f.suffix == ".html" else md_to_html(m.group(2))
        posts.append(meta)
    slugs = [p["slug"] for p in posts]
    dupes = {x for x in slugs if slugs.count(x) > 1}
    if dupes: raise SystemExit(f"Two posts share the slug {', '.join(dupes)}")
    posts.sort(key=lambda p: (p["when"], p["slug"]), reverse=True)
    return posts

def build_blog(posts):
    for stale in (OUT / "blog").glob("*.html"): stale.unlink()  # a removed or renamed post must not linger
    for i, p in enumerate(posts):
        path = f"blog/{p['slug']}.html"
        others = [q for q in posts if q is not p][:3] if i < 3 else posts[:3]
        more = "".join(f'<li><a href="blog/{q["slug"]}.html">{esc(q["title"])}</a><span>{nice_date(q["when"])}</span></li>' for q in others)
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["description"],
              "datePublished": p["date"], "dateModified": p.get("updated", p["date"]), "url": canon(path), "image": f"{SITE}/assets/{p['photo'] or 'kelley-headshot.jpg'}",
              "author": {"@type": "Person", "name": NAME, "url": canon("team.html")},
              "publisher": {"@type": "Organization", "name": TEAM, "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/logo-cb-griffin-team.png"}}}
        body = f"""<section class="sc-section" style="padding-top:0"><div class="sc-wrap"><article class="prose post" data-sc-in>
<p class="post__meta">{nice_date(p['when'])} · {NAME}</p>
{p['body']}
</article>
<aside class="post__more" aria-label="More from the blog"><p class="sc-label">More from the blog</p><ul class="post-list post-list--short">{more}</ul><a class="link" href="blog/index.html">All posts</a></aside>
</div></section>{cta_band()}"""
        write(path, page_shell(f"{p['title']} | {TEAM}", p["description"], path,
            page_hero("Blog", esc(p["title"]), "", p["photo"], p.get("photo_alt", "")), body,
            extra_head=f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'))
    def pic(p):
        if not p["photo"]: return '<span class="pcard__rule" aria-hidden="true"></span>'
        w, h = img_size(p["photo"])
        return f'<span class="pcard__pic"><img src="assets/{p["photo"]}" alt="" width="{w}" height="{h}" loading="lazy"></span>'
    feat = "".join(f'<li><a class="pcard" href="blog/{p["slug"]}.html">{pic(p)}<span class="pcard__date">{nice_date(p["when"])}</span><span class="pcard__title">{esc(p["title"])}</span><span class="pcard__desc">{esc(p["description"])}</span></a></li>' for p in posts[:3])
    rows, year = "", None
    for p in posts[3:]:
        if p["when"].year != year:
            year = p["when"].year
            rows += f'</ul><h2 class="post-year">{year}</h2><ul class="post-list post-list--grid">'
        rows += f'<li><a href="blog/{p["slug"]}.html">{esc(p["title"])}</a><p>{esc(p["description"])}</p><span>{nice_date(p["when"])}</span></li>'
    rows = f'<p class="sc-label blog-index__k">Latest</p><ul class="pcards">{feat}</ul>' + rows[len("</ul>"):] + "</ul>"
    body = f"""<section class="sc-section" style="padding-top:0"><div class="sc-wrap"><div class="blog-index">{rows}</div></div></section>{cta_band()}"""
    write("blog/index.html", page_shell(f"Blog | {NAME}, {TEAM}", "Kelley Griffin on buying, selling and living in Fruita, Grand Junction, the Redlands and the Grand Mesa.", "blog/index.html",
        page_hero("Blog", "Notes from the valley", "Market updates, neighborhood guides and family stories from Fruita, Grand Junction, the Redlands and the Grand Mesa.", photo="kelley-biking.jpg", alt="Kelley Griffin mountain biking on rocky desert singletrack under a sandstone overhang"), body))
    return [f"blog/{p['slug']}.html" for p in posts]

# ------------------------------------------------------------------ run ----
build_team(); build_guides(); build_neighborhoods(); build_testimonials(); build_sold(); build_contact(); build_privacy(); build_thank_you(); build_404()
post_pages = build_blog(load_posts())

pages = ["index.html", "team.html", "buyers-guide.html", "sellers-guide.html", "neighborhoods.html"] + [f"neighborhood-{p['slug']}.html" for p in PLACES] + ["testimonials.html", "sold.html", "contact.html", "privacy.html", "blog/index.html"] + post_pages
today = datetime.date.today().isoformat()
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{canon(p)}</loc><lastmod>{today}</lastmod></url>\n" for p in pages) + "</urlset>\n"
(OUT / "sitemap.xml").write_text(sm)
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
print("built", len(pages), "pages (", len(post_pages), "blog posts ) ->", OUT, "| SITE =", SITE)
