# RTFD Field

Hydrant tool for Rockaway Township Fire & Rescue. Single-file build — the whole
app is `index.html`. No build step, no folders.

## What's in it

All 582 hydrants from `Hyd_Test.xlsx` (Hydrants sheet) are baked into the file.
No import step, no connection needed to get the data.

- **Nearest** — GPS-sorted, distance in feet with a bearing arrow
- **Map** — every hydrant, colored by response zone
- **Filter chips** — All, the five zones, and Needs review
- **Detail** — edit number, zone, main size, owner, notes, out of service
- **Directions** — hands off to Google Maps

## Color

Chroma means response zone and nothing else:
Fleetwood blue · Low Erie orange · High Erie violet · Green Pond green ·
Supply red · unassigned grey.

The workbook has no flow-test data, so there is nothing to color by flow class
yet. When GPM numbers exist, that becomes the better color system and the zone
colors move to a second channel.

## Needs review

The workbook audit carried over into the app. Tap **Needs review** to see only
the records that need a decision:

- 1 hydrant with no number (701 Ford Rd)
- 8 records sharing 4 duplicate numbers (H-0434, H-0440, H-0455, H-0458)
- 16 records sitting at the same coordinates as another
- 46 records the geocoder placed outside the township

Each one explains itself at the top of the detail sheet. Fixing a number or zone
there and tapping Save clears it on the device and queues it for the sheet.

## Put it online

Upload `index.html` to the repo root, then Settings → Pages → Deploy from a
branch, `main`, `/ (root)`.

## Put it on a phone

- **Android:** open the link in Chrome, ⋮ → Add to Home screen
- **iPhone:** open in **Safari**, Share → Add to Home Screen

## Getting edits back out

**Setup → Copy all records** puts all 582 on the clipboard as JSON, edits
included. That is the backup and the way to feed changes back into the workbook.

**Reset to file** throws away device edits and reloads the original 582.

## Connect the Google Sheet (optional)

Without this, edits stay on whichever phone made them.

1. Sheet → Extensions → Apps Script, paste `Code.gs`, set `TAB` to your tab name
2. Deploy → New deployment → Web app, execute as **Me**, access **Anyone**
3. Copy the `/exec` URL into the app under Setup

After any change to `Code.gs`, deploy a **new version** — saving alone leaves the
old build live, which is what produces the `doGet not found` page.

Match the field names the app sends: `unit`, `zone`, `size`, `own`, `notes`,
`status`, `updated`, keyed on `id`.

## Known limits

Leaflet and the fonts load from a CDN, so the app needs a connection to start up
and to draw the map. Hydrant data and edits live on the device either way, and
queued edits send themselves when you reconnect. True offline needs a service
worker, which cannot live inside a single file.

`import_hydrants.py` is here for when the workbook changes — it converts a CSV
or xlsx export to JSON and handles ragged rows and cp1252 mojibake.
