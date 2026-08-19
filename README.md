# RTFD Field

Field reference tool for Rockaway Township Fire & Rescue — water supply and
medevac landing zones. Single-file build — the
whole app is `index.html`. No build step, no folders.

## What's in it

878 records from `Hyd_App.xlsx` (Master List), baked into the file. No import
step and no connection needed to get the data.

- **Nearest** — GPS-sorted, distance in feet with a bearing arrow
- **Map** — every record, colored by zone
- **Filters** — All · In town · each zone · Mutual aid · Needs review
- **Detail** — edit number, zone, main size (or cistern capacity), owner, notes,
  out of service
- **Directions** — hands off to Google Maps

## Landing zones

20 medevac LZs from `LZ_App.xlsx`, on their own **LZ** tab. Separate from water
supply on purpose — a pad and a hydrant answer different questions and don't
belong in one list.

- Sorted by distance with a bearing arrow, same as the hydrant list
- Gold **H** markers on the map, which opens fitted to all 20 rather than to
  your position — they run from Dover up to Newfoundland
- Detail sheet leads with **large decimal coordinates**, sized to read over the
  radio, and tapping them copies to the clipboard
- Notes field for surface, wires, obstructions, gate access, best approach —
  all 20 arrived empty, so this is what fills in from the field

## Color

Chroma means zone. Our six get saturated color; the four mutual-aid systems
share one muted slate so "is this ours" reads at a glance:

Fleetwood blue · Low Erie orange · High Erie violet · Green Pond green ·
Supply red · Cistern teal · mutual aid slate

Landing zones own gold, and live on their own tab, so nothing competes with it.

Cisterns draw as **squares** on the map, not circles. Static water is not a
pressurized hydrant and shouldn't look like one. Their detail sheet swaps main
size for capacity in gallons.

## Counts

| | |
|---|---|
| Fleetwood | 319 |
| Low Erie | 122 |
| Green Pond | 87 |
| High Erie | 47 |
| Cistern | 19 |
| Supply | 4 |
| Rockaway Boro | 119 |
| Dover | 86 |
| Wharton | 65 |
| Denville | 10 |

598 in town, 280 mutual aid.

## Needs review

Tap the chip to filter to records needing a decision. Each explains itself at the
top of its detail sheet.

- 2 records share hydrant number H-0484
- 36 records sit at the same coordinates as another

**7 rows are not in the app** — they had no coordinates in the workbook and there
is nothing to place on a map:

| Record | Address |
|---|---|
| Out of Town - 014 | 100 Sammis Ave, Dover |
| Out of Town - 056 | 437 W. Clinton St, Dover |
| Out of Town - 057 | 437 W. Clinton St, Dover |
| Out of Town - 060 | 1 Commerce Center Dr, Dover |
| Out of Town - 061 | 2 Commerce Center Dr, Dover |
| Out of Town - 062 | 4 Commerce Center Dr, Dover |
| Out of Town - 129 | 325 US-15, Wharton |

Geocode those in the workbook and they come in on the next rebuild.

## Put it online

Upload `index.html` to the repo root, then Settings → Pages → Deploy from a
branch, `main`, `/ (root)`. Hard-refresh (Ctrl+Shift+R) or check in a private
window — your browser will cache the old version otherwise.

## Put it on a phone

- **Android:** open the link in Chrome, ⋮ → Add to Home screen
- **iPhone:** open in **Safari**, Share → Add to Home Screen

## Updating the data

When a new data file ships, the app replaces what's on the device with the new
records and **carries your edits across** — any record with an `updated` stamp
keeps its edited fields, and an edited record the new file dropped is kept too.

Setup shows which data file the device is on. If it says anything other than
current, **Reset to file** forces a reload.

## Getting edits back out

**Setup → Copy all records** puts all 878 water supply records plus the 20
landing zones on the clipboard as JSON, edits included. That is the backup and the way to feed changes back into the workbook.

**Reset to file** discards device edits and reloads the original 878.

## Connect the Google Sheet (optional)

Without this, edits stay on whichever phone made them.

1. Sheet → Extensions → Apps Script, paste `Code.gs`, set `TAB` to your tab name
2. Deploy → New deployment → Web app, execute as **Me**, access **Anyone**
3. Copy the `/exec` URL into the app under Setup

After any change to `Code.gs`, deploy a **new version**. Saving alone leaves the
old build live, which is what produces the `doGet not found` page.

Two modules sync: `hydrants` and `lz`, each posting with its own `module` name.

Hydrant fields, keyed on `id`: `unit`, `zone`, `size`, `cap`, `own`, `notes`,
`status`, `updated`. Landing zone fields: `notes`, `updated`.

## Known limits

Leaflet and the fonts load from a CDN, so the app needs a connection to start up
and to draw the map. Records and edits live on the device either way, and queued
edits send themselves when you reconnect. True offline needs a service worker,
which cannot live inside a single file.

No flow-test data exists yet. When GPM numbers arrive, NFPA 291 flow class
becomes the better thing to color by and zone moves to a second channel.
