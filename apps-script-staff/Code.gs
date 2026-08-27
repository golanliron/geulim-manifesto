/**
 * "בונים יחד את הכפר" — הצוות החינוכי · גאולי
 * ------------------------------------------------------------
 * גרסת אחסון ב-Script Properties (בלי הרשאות OAuth בכלל),
 * כדי שה-Web App ירוץ אנונימית גם בפריסה דרך clasp.
 *
 * POST                → שומר תשובה (q1..q4 מערכים)
 * GET ?mode=screen    → צבירה למסך ההקרנה {q1:{},q2:{},q3:{},q4:{},total}
 * GET ?mode=export    → כל התשובות הגולמיות (להעברה לגיליון)
 * GET ?mode=reset&key=geuli-staff-2026 → מאפס את כל התשובות
 *
 * להעברה לגיליון "תשובות הצוות" בהמשך: syncToSheet בגרסה הבאה,
 * דורש אישור חד-פעמי בעורך (הרשאת גיליונות).
 */

var RESET_KEY = 'geuli-staff-2026';

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var row = {
      t: new Date().toISOString(),
      q1: body.q1 || [],
      q2: body.q2 || [],
      q3: body.q3 || [],
      q4: body.q4 || []
    };
    var lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      var p = PropertiesService.getScriptProperties();
      var n = Number(p.getProperty('count') || 0) + 1;
      p.setProperty('r' + ('000000' + n).slice(-6), JSON.stringify(row));
      p.setProperty('count', String(n));
    } finally {
      lock.releaseLock();
    }
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function readRows_() {
  var all = PropertiesService.getScriptProperties().getProperties();
  var rows = [];
  Object.keys(all).forEach(function (k) {
    if (k.charAt(0) !== 'r') return;
    try { rows.push(JSON.parse(all[k])); } catch (ignored) {}
  });
  rows.sort(function (a, b) { return a.t < b.t ? -1 : 1; });
  return rows;
}

function doGet(e) {
  var mode = e && e.parameter ? e.parameter.mode : '';

  if (mode === 'reset') {
    if ((e.parameter.key || '') !== RESET_KEY) return json_({ ok: false, error: 'bad key' });
    var lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      var p = PropertiesService.getScriptProperties();
      Object.keys(p.getProperties()).forEach(function (k) {
        if (k.charAt(0) === 'r' || k === 'count') p.deleteProperty(k);
      });
    } finally {
      lock.releaseLock();
    }
    return json_({ ok: true, reset: true });
  }

  if (mode === 'export') {
    return json_({ ok: true, rows: readRows_() });
  }

  if (mode !== 'screen') {
    return json_({ ok: true, hint: 'use ?mode=screen' });
  }

  var out = { q1: {}, q2: {}, q3: {}, q4: {}, total: 0 };
  readRows_().forEach(function (row) {
    var hasAny = false;
    for (var q = 1; q <= 4; q++) {
      (row['q' + q] || []).forEach(function (raw) {
        var v = String(raw).trim();
        if (!v) return;
        hasAny = true;
        out['q' + q][v] = (out['q' + q][v] || 0) + 1;
      });
    }
    if (hasAny) out.total++;
  });
  return json_(out);
}
