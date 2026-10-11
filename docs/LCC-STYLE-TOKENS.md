# LCC Style Tokens — Latinas Contra Cancer → Podrá Navega

Scout report, Oct 11, 2026; restyle applied Oct 11, 2026. Purpose: make
Podrá Navega's look and feel match the Latinas Contra Cancer website
(https://www.latinascontracancer.org/).

## 0. Verification status — read this first

**Opened and read in full (house rule: opened pages only):**
- Home — https://www.latinascontracancer.org/
- About Us — https://www.latinascontracancer.org/about-us
- Patient Navigation & Advocacy — https://www.latinascontracancer.org/patient-navigation

**Brand hexes — VERIFIED (closed Oct 11, 2026):** the three brand colors
below were taken from LCC's own inline SVG icon markup on the live site —
exact values as published by LCC itself, visually consistent with the
homepage (orange Donate CTA with white bold label; very dark footer with
white text and orange accents):

| Token | Value | Source |
|---|---|---|
| Brand orange | `#D16616` | LCC inline SVG markup (verified) |
| Brand navy | `#112F5B` | LCC inline SVG markup (verified) |
| Brand green | `#04723D` | LCC inline SVG markup (verified) |

**Still NOT verified — the font gap (honest, open):** LCC's exact theme
font families. The site is built on Wix; two extraction routes (text fetch
of opened pages — which strips all CSS — and a live-browser pass) could not
resolve the Wix CSS variable font names. **No font match has been invented.**
Podrá keeps its existing readable stack
(`"Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif`)
until a future pass can read the rendered font names from LCC's pages
directly. If that happens, drop the families into `.brand h1` / `.panel h2` /
`body` per §3 and update this section.

Also on record: a targeted search found **no published LCC brand guide**.
(Caution: that search returns brand guidelines for OTHER cancer orgs —
GIRLvsCANCER, Lymphoma Coalition, Cancer Nation. Their colors are not LCC's.
Do not use them.)

## 1. LCC identity — verified from the opened pages

**Overall feel (from the site's own voice and structure):**
warm · bold · justice-driven · community-rooted

- Tagline pair on About: **"Rooted in Community. Powered by Justice."**
- Homepage eyebrow kicker: "Health Justice Starts Here"; program promise:
  "Because no one should face cancer alone."
- What a cancer-community audience should feel: **seen, accompanied, and
  dignified** — never clinical, never pitied. The site speaks of dignity,
  solidarity, and collective power, in English and Spanish side by side
  (programming offered bilingually; a full Spanish section exists, /es/).
- Structure Podrá can mirror: small-caps eyebrow kicker → big statement
  headline → plain-language body; program cards with short titles; a real
  person's testimonial given prominent space; warm community photography
  (hands/heart, women together) instead of stock medical imagery.
- Headline style: short declarative statements, sentence case, emotionally
  direct ("Support for Every Stage of Care"). Eyebrow labels are small,
  uppercase-feeling, and frequent.

**Logo treatment:** the logo image itself is not exposed in the fetched page
text (only content photos are), so its colors/shape are **not described here
rather than guessed**. Per instructions we will not copy their logo file in
any case — Podrá keeps its own wordmark, restyled with LCC tokens.

## 2. Podrá Navega — current tokens (exact, from app/static/style.css, post-restyle Oct 11, 2026)

| Role | Value |
|---|---|
| Page background | `#faf5ee` (warm cream) |
| Panel surface | `#fffdf9` |
| Ink (body text) | `#33261e` (warm near-black brown) |
| Muted text | `#7d6c5e` |
| Hairline / borders | `#e9dccb` |
| Accent (primary brand) | `#d16616` — **LCC orange `#D16616` (verified)** |
| Accent dark | `#a35011` — derived (accent darkened ~22%) |
| Accent soft (fills) | `#faede3` — derived (accent tinted ~88% to white) |
| Navy (headings / footer) | `#112f5b` — **LCC navy `#112F5B` (verified)** |
| Sage (verified / sent / go) | `#04723d` — **LCC green `#04723D` (verified)**; soft `#e6f1ec` (derived tint), dark text `#034a28` (derived shade) |
| Gold (pending / attention) | `#c98f1b`, soft `#faf0d7`, dark text `#6d4c07` — unchanged |
| Crisis red | `#a91f16`, bg `#fdecea`, line `#e8a49e` — unchanged (hard rule) |
| Chat backdrop | `#eee6d8` |
| Patient bubble | `#dceec9` (soft green) |
| Navigator bubble | `#ffffff` |
| Panel radius | `16px`; buttons/bubbles `10–12px` |
| Buttons | 2px solid border, weight 700; primary (Approve) = **accent-orange fill**, white bold text, full width, 1.08rem (LCC CTA pattern) |
| Header | white panel, 3px accent bottom border; eyebrow kicker above a navy wordmark with orange second word |
| Navigator panel | 8px accent top border |
| Patient panel | 8px sage (LCC green) top border |
| Footer | navy `#112f5b` band, 4px orange top rule, white text |
| Font | `"Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif` — one stack for headings and body; 17px base, line-height 1.6. **LCC's own font families remain unverified (§0) — not invented.** |

## 3. Mapping guidance — LCC token → Podrá

**Status: APPLIED Oct 11, 2026** (see §5 for the change log). Podrá was
already directionally close to LCC's feel (warm cream ground, warm accent,
community tone — not clinical blue/white). The restyle was a **token swap,
not a redesign**: layout, radius, and weight system kept; values replaced
with LCC's verified brand values from §0.

| LCC token (to confirm) | Applies in Podrá (exact slot) |
|---|---|
| LCC primary brand color | `--accent` + topbar 3px bottom border + navigator panel 8px top border + "Navega" wordmark word |
| LCC primary dark/hover shade | `--accent-dark` (button text/border on light buttons) |
| LCC primary tint | `--accent-soft` (case header fill, button hover fill) |
| LCC secondary / support color | `--sage` family (patient panel top border, verified states) — keep sage semantics: green = verified/sent/approved |
| LCC highlight / warm neutral | `--gold` family stays for pending/attention ONLY (never for crisis) |
| LCC heading font | `.brand h1`, `.panel h2`, `section.block h3` — add as first font in stack, keep system fallbacks |
| LCC body font | `body` font-family (replace Segoe-first stack if LCC uses a distinct face) |
| LCC page background tone | `--bg` (stay warm/light; LCC's photography-led warmth argues against any dark or grey-blue ground) |
| LCC button style | `button` / `.btn-primary`: match LCC CTA fill color + radius feel; keep Podrá's 700 weight and full-width primary Approve |
| Eyebrow kicker pattern (verified LCC habit) | Add small uppercase eyebrow labels above panel headings, mirroring LCC's kickers ("Health Justice Starts Here") — cheapest high-signal match available without the CSS |
| Bilingual presentation (verified LCC habit) | Keep Podrá's ES-first / EN-gloss pattern — it already matches LCC's side-by-side bilingual voice |

**Hard rule — crisis stays crisis:** the crisis banner and escalation states
keep Podrá's red family (`--red: #a91f16`, `--red-bg: #fdecea`) at full
strength regardless of the brand palette. Never tint, soften, or rebrand the
crisis red toward terracotta or any LCC token — red must read as urgent and
unmistakable at a glance, in both languages.

## 4. Contrast summary

- **Shared ground:** warmth, cream/earth tones, plain language, bilingual
  voice, community-before-clinic framing. Podrá does not need a personality
  change.
- **Gaps to close:** (1) exact LCC hexes/fonts (pending §0 pass);
  (2) LCC's eyebrow-kicker + statement-headline rhythm (Podrá's headings are
  plainer); (3) LCC leads with people/testimony — Podrá's demo already leads
  with the navigator panel, so keep that and borrow the kicker rhythm only.
- **Do not import:** other cancer orgs' palettes found in search results;
  LCC's logo file; any pink-ribbon cliché styling (nothing on the opened LCC
  pages leans on it).

## 5. Restyle applied — Oct 11, 2026

**Changed:**
- `--accent` `#b34724` (terracotta) → `#d16616` (LCC orange, verified).
  `--accent-dark` → `#a35011` and `--accent-soft` → `#faede3` (derived
  shades of the verified orange, computed by darkening/tinting it — no
  other hue introduced). Everything slotted to accent follows: topbar 3px
  bottom border, navigator-panel 8px top border, "Navega" wordmark word,
  secondary-button borders/text/hover, case-header fill, switch accent.
- **New token `--navy: #112f5b`** (LCC navy, verified) → `.brand h1`,
  `.panel h2`, `section.block h3`; panel shadow re-based to navy
  (`rgba(17,47,91,0.12)`).
- `--sage` `#56724c` → `#04723d` (LCC green, verified); `--sage-soft` →
  `#e6f1ec` (derived tint); hardcoded dark-green text `#33482c` →
  new `--sage-dark: #034a28` (derived shade) in the three verified-state
  slots. Patient-panel top border and all verified/approved states follow.
- **Approve button (`.btn-primary`)**: sage fill → **LCC CTA pattern**
  (accent-orange fill, white bold label, modest radius), hover =
  accent-dark. It stays full-width and larger than every secondary button,
  and the approve-reason banner keeps its gold-blocked / green-ready
  semantics — so the commit action remains unmistakable.
- **Eyebrow kicker added** above the title (LCC's verified rhythm):
  "Latinas Contra Cancer — Navegación de pacientes / Patient navigation",
  uppercase, letter-spaced, accent-dark. (Generic descriptive phrase —
  LCC's exact slogans were not copied verbatim.)
- **Footer band added**: navy `#112f5b`, 4px orange top rule, white text —
  "Podrá Navega — una herramienta para Latinas Contra Cancer / a tool for
  Latinas Contra Cancer" + the fictional-patients / no-medical-advice note.
- `app/static/README-frontend.md` palette line updated to match.

**Deliberately NOT changed, and why:**
- **Crisis red family** (`--red #a91f16`, `--red-bg #fdecea`,
  `--red-line #e8a49e`) — untouched, per the hard rule in §3. Red stays
  urgent and unmistakable, never tinted toward brand orange.
- **Gold family** — pending/attention semantics unchanged (badges, barrier
  flags, blocked-approve banner). Gold never signals crisis and never
  signals approval.
- **Font stack** — LCC's theme font families are still unverified (§0);
  rather than invent a "match," Podrá keeps its existing readable stack.
  This is the one open item in the brand match.
- **Cream page ground, ink, chat backdrop, patient/navigator bubble
  colors** — kept. Warm light ground matches LCC's photography-led warmth;
  the soft-green patient bubble stays clearly distinct from the white
  navigator bubble and now sits in the same green family as the verified
  brand green.
- **Layout, radius, type scale** — untouched. Token swap only.

**Verification:** pytest 14/14 after the swap; demo mode behavior
unchanged. Screenshot: `screenshots/07-restyle-main-1280x800.png`
(visually checked: kicker + two-tone navy/orange wordmark render cleanly,
orange reads warm not garish, no overlapping text; footer band checked
separately — navy field, orange rule, white bilingual text).
