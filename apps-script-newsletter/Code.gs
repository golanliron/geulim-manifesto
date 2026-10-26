/**
 * ניוזלטר גאולים — קליטת מתעניינים לגיליון
 * ------------------------------------------
 * POST (form-urlencoded) → מוסיף שורה
 * GET  ?mode=count       → {ok, count}
 *
 * הדף: https://www.geuli.co.il/newsletter/
 */

var SHEET_ID = '1K1qeMNkeI6-xcFjzHQOSB-L-BUDugtNs0lCeTjqy7II';
var SHEET_NAME = 'מתעניינים';

var HEADERS = [
  'תאריך',
  'שם מלא',
  'טלפון',
  'אימייל',
  'כיתה לשנה הבאה',
  'שכונה',
  'שאלה או הערה'
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
    sh.setColumnWidth(2, 180);
    sh.setColumnWidth(3, 130);
    sh.setColumnWidth(4, 210);
    sh.setColumnWidth(5, 140);
    sh.setColumnWidth(6, 140);
    sh.setColumnWidth(7, 300);
  }
  return sh;
}

function doPost(e) {
  try {
    var p = (e && e.parameter) ? e.parameter : {};
    var name = String(p.name || '').trim();
    var phone = String(p.phone || '').trim();
    if (!name || !phone) return json_({ ok: false, error: 'missing name or phone' });

    var stamp = Utilities.formatDate(new Date(), 'Asia/Jerusalem', 'dd/MM/yyyy HH:mm');
    sheet_().appendRow([
      stamp,
      name,
      phone,
      String(p.email || '').trim(),
      String(p.grade || '').trim(),
      String(p.area || '').trim(),
      String(p.notes || '').trim()
    ]);
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function doGet(e) {
  var mode = (e && e.parameter && e.parameter.mode) || '';
  if (mode === 'count') {
    var sh = sheet_();
    return json_({ ok: true, count: Math.max(0, sh.getLastRow() - 1) });
  }
  return json_({ ok: true, service: 'geulim-newsletter-signup' });
}
