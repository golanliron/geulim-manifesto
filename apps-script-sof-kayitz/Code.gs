/**
 * מסיבת סוף הקיץ של גאולים · 22.10 — קליטת אישורי הגעה לגיליון
 * ------------------------------------------------------------
 * POST (form-urlencoded)  → מוסיף שורה לגיליון
 * GET  ?mode=counts       → {ok, families, adults, children}
 *
 * הדף: https://www.geuli.co.il/sof-kayitz.html
 */

var SHEET_ID = '1XD9GmHoi0s6EUrJHfsgBLYnJaLIcFLrtO_opucZ8T-k';
var SHEET_NAME = 'אישורי הגעה';
var CLEAR_KEY = 'geuli-sof-kayitz-2026';

var HEADERS = [
  'תאריך רישום',
  'שם ההורה',
  'טלפון',
  'מבוגרים',
  'ילדים',
  'שמות הילדים',
  'מתנדב/ת לעזרה',
  'הערות'
];

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function sheet_() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.getSheets()[0];
    sh.setName(SHEET_NAME);
  }
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEADERS);
    sh.getRange(1, 1, 1, HEADERS.length)
      .setFontWeight('bold')
      .setBackground('#1F355E')
      .setFontColor('#FFFFFF');
    sh.setFrozenRows(1);
    sh.setRightToLeft(true);
    sh.setColumnWidth(1, 150);
    sh.setColumnWidth(2, 170);
    sh.setColumnWidth(3, 120);
    sh.setColumnWidth(6, 260);
    sh.setColumnWidth(8, 260);
  }
  return sh;
}

function doPost(e) {
  try {
    var p = (e && e.parameter) ? e.parameter : {};
    var parent = String(p.parent || '').trim();
    var phone = String(p.phone || '').trim();
    if (!parent || !phone) return json_({ ok: false, error: 'missing parent or phone' });

    var children = [];
    try { children = JSON.parse(p.childrenJson || '[]'); } catch (ignored) {}
    if (!Array.isArray(children)) children = [];

    var names = children.map(function (c) {
      var n = String((c && c.name) || '').trim();
      var cls = String((c && c.class) || '').trim();
      return cls ? (n + ' (' + cls + ')') : n;
    }).filter(String).join(', ');

    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      sheet_().appendRow([
        Utilities.formatDate(new Date(), 'Asia/Jerusalem', 'dd/MM/yyyy HH:mm'),
        parent,
        "'" + phone,
        Number(p.adults || 1),
        children.length,
        names,
        String(p.volunteer) === 'true' ? 'כן' : '',
        String(p.note || '').trim()
      ]);
    } finally {
      lock.releaseLock();
    }
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function counts_() {
  var sh = sheet_();
  var last = sh.getLastRow();
  if (last < 2) return { families: 0, adults: 0, children: 0 };
  var vals = sh.getRange(2, 4, last - 1, 2).getValues();
  var adults = 0, children = 0;
  vals.forEach(function (r) {
    adults += Number(r[0]) || 0;
    children += Number(r[1]) || 0;
  });
  return { families: last - 1, adults: adults, children: children };
}

function doGet(e) {
  var mode = (e && e.parameter) ? (e.parameter.mode || '') : '';
  if (mode === 'counts') {
    try {
      var c = counts_();
      return json_({ ok: true, families: c.families, adults: c.adults, children: c.children });
    } catch (err) {
      return json_({ ok: false, error: String(err) });
    }
  }
  if (mode === 'restore') {
    if ((e.parameter.key || '') !== CLEAR_KEY) return json_({ ok: false, error: 'bad key' });
    var rows;
    try { rows = JSON.parse(e.parameter.rows || '[]'); } catch (err) { return json_({ ok:false, error:'bad rows' }); }
    if (!rows.length) return json_({ ok:false, error:'no rows' });
    var sh = sheet_();
    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i];
        sh.appendRow([ r[0], r[1], "'" + r[2], Number(r[3]), Number(r[4]), r[5], r[6] || '', r[7] || '' ]);
      }
    } finally { lock.releaseLock(); }
    return json_({ ok: true, restored: rows.length });
  }
  return json_({ ok: true, service: 'geuli sof-kayitz' });
}
