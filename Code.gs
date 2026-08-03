/**
 * RTFD Field — Apps Script backend for the "RTFD hydrants" spreadsheet.
 *
 * Setup
 *   1. Open the sheet > Extensions > Apps Script, paste this in.
 *   2. Set SHEET_ID and TAB below.
 *   3. Deploy > New deployment > type "Web app"
 *        Execute as: Me
 *        Who has access: Anyone
 *   4. Copy the /exec URL into the app under Setup > Apps Script web app URL.
 *
 * After ANY edit here you must Deploy > New deployment (or Manage deployments >
 * edit > New version). Saving alone leaves the old build live, which is what
 * produces the "doGet not found" page.
 *
 * The sheet needs a header row containing at least: id, unit, street, lat, lon.
 * An "updated" column is added automatically if it isn't there.
 */

var SHEET_ID = '';            // spreadsheet id from the URL, or '' when bound to the sheet
var TAB = 'Consolidated';     // tab holding the hydrant rows

function sheet_() {
  var ss = SHEET_ID ? SpreadsheetApp.openById(SHEET_ID) : SpreadsheetApp.getActive();
  var sh = ss.getSheetByName(TAB);
  if (!sh) throw new Error('Tab not found: ' + TAB);
  return sh;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function table_() {
  var sh = sheet_();
  var values = sh.getDataRange().getValues();
  var head = values.shift().map(function (h) { return String(h).trim().toLowerCase(); });
  return { sh: sh, head: head, values: values };
}

/* ---------- pull ---------- */

function doGet(e) {
  try {
    var since = (e && e.parameter && e.parameter.since) ? new Date(e.parameter.since) : null;
    var t = table_();
    var iU = t.head.indexOf('updated');
    var rows = [];

    t.values.forEach(function (r, i) {
      if (since && iU > -1 && r[iU]) {
        var u = new Date(r[iU]);
        if (!isNaN(u) && u <= since) return;
      }
      var o = {};
      t.head.forEach(function (h, c) { if (h) o[h] = r[c]; });
      if (!o.id) o.id = 'H-' + ('0000' + (i + 1)).slice(-4);
      o.lat = Number(o.lat); o.lon = Number(o.lon);
      if (!o.lat || !o.lon) return;
      rows.push(o);
    });

    return json_({ rows: rows, now: new Date().toISOString() });
  } catch (err) {
    return json_({ rows: [], error: String(err) });
  }
}

/* ---------- push ---------- */

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    var body = JSON.parse(e.postData.contents);
    var edits = body.edits || [];
    var t = table_();

    var iId = t.head.indexOf('id');
    if (iId < 0) throw new Error('Sheet needs an "id" column.');

    var iU = t.head.indexOf('updated');
    if (iU < 0) {
      iU = t.head.length;
      t.sh.getRange(1, iU + 1).setValue('updated');
      t.head.push('updated');
    }

    var rowOf = {};
    t.values.forEach(function (r, i) { rowOf[String(r[iId])] = i + 2; }); // +2: header + 1-index

    var applied = 0;
    edits.forEach(function (ed) {
      var row = rowOf[String(ed.id)];
      if (!row) return;
      Object.keys(ed.patch || {}).forEach(function (k) {
        var col = t.head.indexOf(String(k).toLowerCase());
        if (col > -1) t.sh.getRange(row, col + 1).setValue(ed.patch[k]);
      });
      t.sh.getRange(row, iU + 1).setValue(new Date().toISOString());
      applied++;
    });

    return json_({ ok: true, applied: applied });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (ignore) {}
  }
}
