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
var NOTIFY_EMAIL = 'golanliron1@gmail.com';

var HEADERS = [
  'תאריך',
  'שם מלא',
  'טלפון',
  'אימייל',
  'כיתה לשנה הבאה',
  'שכונה',
  'שאלה או הערה'
];

/**
 * ⬅️ הפונקציה הזו קיימת רק כדי לאשר הרשאות.
 *    בחרי אותה למעלה ולחצי Run. זה כל מה שצריך.
 */
function אישור_הרשאות() {
  SpreadsheetApp.openById(SHEET_ID).getName();          // הרשאת גיליון
  MailApp.sendEmail({
    to: NOTIFY_EMAIL,
    subject: 'ההרשאות אושרו · ניוזלטר גאולים',
    htmlBody: '<div dir="rtl" style="font-family:Arial;font-size:15px;">' +
      'מעולה. מעכשיו תקבלי מייל על כל מי שמשאיר פרטים במגזין.</div>',
    name: 'ניוזלטר גאולים'
  });                                                    // הרשאת מייל
}

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

function notify_(row) {
  try {
    var esc = function (v) {
      return String(v == null ? '' : v)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    };
    var line = function (label, value) {
      if (!value) return '';
      return '<tr>' +
        '<td style="padding:8px 14px;background:#F4EDDC;color:#1F355E;font-weight:700;' +
        'white-space:nowrap;border-bottom:1px solid #fff;">' + esc(label) + '</td>' +
        '<td style="padding:8px 14px;color:#1F355E;border-bottom:1px solid #F4EDDC;">' +
        esc(value) + '</td></tr>';
    };

    var html =
      '<div dir="rtl" style="font-family:Arial,Helvetica,sans-serif;background:#EDE8DE;padding:22px;">' +
        '<div style="max-width:560px;margin:0 auto;background:#FBF9F4;border-radius:14px;overflow:hidden;">' +
          '<div style="background:#1F355E;padding:18px 22px;">' +
            '<div style="color:#fff;font-size:18px;font-weight:700;">מתעניין חדש בבית ספר גאולים</div>' +
            '<div style="color:#D8C7A0;font-size:13px;margin-top:4px;">נשלח מהניוזלטר באתר</div>' +
          '</div>' +
          '<div style="height:5px;background:#8A9746;"></div>' +
          '<table style="width:100%;border-collapse:collapse;font-size:14px;">' +
            line('שם מלא', row.name) +
            line('טלפון', row.phone) +
            line('אימייל', row.email) +
            line('כיתה לשנה הבאה', row.grade) +
            line('שכונה', row.area) +
            line('שאלה או הערה', row.notes) +
            line('התקבל בתאריך', row.stamp) +
          '</table>' +
          '<div style="padding:16px 22px;">' +
            '<a href="https://docs.google.com/spreadsheets/d/' + SHEET_ID + '/edit" ' +
            'style="display:inline-block;background:#D8C7A0;color:#14243F;text-decoration:none;' +
            'font-weight:700;padding:10px 22px;border-radius:999px;font-size:14px;">פתיחת הגיליון</a>' +
          '</div>' +
        '</div>' +
      '</div>';

    MailApp.sendEmail({
      to: NOTIFY_EMAIL,
      subject: 'מתעניין חדש בגאולים: ' + row.name,
      htmlBody: html,
      replyTo: row.email || undefined,
      name: 'ניוזלטר גאולים'
    });
  } catch (err) {
    // כישלון במייל לא יפיל את שמירת השורה
  }
}

function doPost(e) {
  try {
    var p = (e && e.parameter) ? e.parameter : {};
    var name = String(p.name || '').trim();
    var phone = String(p.phone || '').trim();
    if (!name || !phone) return json_({ ok: false, error: 'missing name or phone' });

    var stamp = Utilities.formatDate(new Date(), 'Asia/Jerusalem', 'dd/MM/yyyy HH:mm');
    var row = {
      stamp: stamp,
      name: name,
      phone: phone,
      email: String(p.email || '').trim(),
      grade: String(p.grade || '').trim(),
      area: String(p.area || '').trim(),
      notes: String(p.notes || '').trim()
    };
    sheet_().appendRow([
      row.stamp, row.name, row.phone, row.email, row.grade, row.area, row.notes
    ]);
    notify_(row);
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function doGet(e) {
  var mode = (e && e.parameter && e.parameter.mode) || '';
  if (mode === 'clear' && e.parameter.key === 'geulim-newsletter-2026') {
    var sh2 = sheet_();
    if (sh2.getLastRow() > 1) sh2.deleteRows(2, sh2.getLastRow() - 1);
    return json_({ ok: true, cleared: true });
  }
  if (mode === 'mailtest') {
    try {
      MailApp.sendEmail({ to: NOTIFY_EMAIL, subject: 'בדיקת הרשאות מייל גאולים',
        htmlBody: '<div dir="rtl">אם הגיע, שליחת המיילים עובדת.</div>', name: 'ניוזלטר גאולים' });
      return json_({ ok: true, mail: 'sent', left: MailApp.getRemainingDailyQuota() });
    } catch (err) {
      return json_({ ok: false, mail: 'failed', error: String(err) });
    }
  }
  if (mode === 'count') {
    var sh = sheet_();
    return json_({ ok: true, count: Math.max(0, sh.getLastRow() - 1) });
  }
  return json_({ ok: true, service: 'geulim-newsletter-signup' });
}
