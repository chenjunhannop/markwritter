// ============================================================
// 01 – Create Design Token Variables
// Collection: "Liquid Crystal" with Light & Dark modes
// ------------------------------------------------------------
// Paste into Figma Console: Plugins → Development → Console
// Safe to re-run: finds or creates every element idempotently.
// ============================================================

(function () {

  // ── Helpers ──────────────────────────────────────────────

  function findCollection(name) {
    return figma.variables
      .getLocalVariableCollections()
      .find(function (c) { return c.name === name; });
  }

  function findVariable(name, collectionId) {
    return figma.variables
      .getLocalVariables()
      .find(function (v) {
        return v.name === name && v.variableCollectionId === collectionId;
      });
  }

  function ensureCollection(name) {
    var c = findCollection(name);
    if (c) return c;
    return figma.variables.createVariableCollection(name);
  }

  function ensureVariable(name, collectionId, resolvedType) {
    var v = findVariable(name, collectionId);
    if (v) return v;
    return figma.variables.createVariable(name, collectionId, resolvedType);
  }

  // ── Scope presets ────────────────────────────────────────

  var FILL  = ["FRAME_FILL", "SHAPE_FILL"];
  var TEXT  = ["TEXT_FILL"];
  var LINE  = ["STROKE"];
  var ALL   = ["FRAME_FILL", "SHAPE_FILL", "TEXT_FILL", "STROKE"];
  var RADIUS_SCOPE   = ["CORNER_RADIUS"];
  var SPACING_SCOPE  = ["GAP", "WIDTH_HEIGHT"];

  // ── 1. Create / resolve collection + modes ───────────────

  var collection = ensureCollection("Liquid Crystal");
  var modes      = collection.modes.slice();          // [{ modeId, name }]
  var lightId, darkId;

  // If the collection is brand-new it has one mode named "Mode 1"
  var isNew = modes.length === 1 && modes[0].name === "Mode 1";

  if (isNew) {
    lightId = modes[0].modeId;
    collection.renameMode(lightId, "Light");
    darkId = collection.addMode("Dark");
  } else {
    var lm = modes.find(function (m) { return m.name === "Light"; });
    var dm = modes.find(function (m) { return m.name === "Dark"; });
    lightId = lm ? lm.modeId : collection.addMode("Light");
    darkId  = dm ? dm.modeId : collection.addMode("Dark");
  }

  var cid = collection.id;

  // ── 2. Color tokens ─────────────────────────────────────
  // [name, scopeArray, lightR, lightG, lightB, darkR, darkG, darkB]

  var COLOR_TOKENS = [

    // ── Fill-only ────────────────────────────────────────
    ["background",        FILL, 0.969,0.945,0.910,  0.071,0.055,0.039],
    ["surface-base",      FILL, 1.000,0.976,0.949,  0.102,0.078,0.059],
    ["surface-raised",    FILL, 0.988,0.965,0.933,  0.137,0.106,0.078],
    ["surface-sunken",    FILL, 0.965,0.902,0.792,  0.059,0.043,0.031],
    ["card",              FILL, 1.000,0.976,0.949,  0.102,0.078,0.059],
    ["secondary",         FILL, 0.988,0.965,0.933,  0.137,0.106,0.078],
    ["muted",             FILL, 0.941,0.910,0.855,  0.102,0.078,0.059],
    ["accent",            FILL, 0.965,0.902,0.792,  0.192,0.149,0.110],
    ["accent-muted",      FILL, 0.973,0.929,0.835,  0.161,0.125,0.102],
    ["status-success-bg", FILL, 0.918,0.949,0.902,  0.102,0.149,0.086],
    ["status-warning-bg", FILL, 0.984,0.941,0.851,  0.161,0.125,0.102],
    ["status-error-bg",   FILL, 0.973,0.902,0.878,  0.149,0.086,0.071],
    ["status-info-bg",    FILL, 0.910,0.929,0.949,  0.086,0.110,0.141],

    // ── Text-only ────────────────────────────────────────
    ["foreground",             TEXT, 0.169,0.129,0.086,  0.973,0.945,0.906],
    ["primary-foreground",     TEXT, 0.169,0.129,0.086,  0.169,0.129,0.086],
    ["secondary-foreground",   TEXT, 0.169,0.129,0.086,  0.973,0.945,0.906],
    ["card-foreground",        TEXT, 0.169,0.129,0.086,  0.973,0.945,0.906],
    ["muted-foreground",       TEXT, 0.471,0.384,0.294,  0.780,0.714,0.624],
    ["accent-foreground",      TEXT, 0.169,0.129,0.086,  0.973,0.945,0.906],
    ["destructive-foreground", TEXT, 1.000,0.976,0.949,  0.973,0.945,0.906],

    // ── Stroke-only ──────────────────────────────────────
    ["border", LINE, 0.863,0.780,0.655,  0.353,0.275,0.188],
    ["input",  LINE, 0.863,0.780,0.655,  0.353,0.275,0.188],

    // ── Multi-scope (fill + text + stroke) ───────────────
    ["primary",        ALL, 0.902,0.635,0.235,  0.941,0.690,0.290],
    ["primary-hover",  ALL, 0.847,0.580,0.196,  0.957,0.788,0.482],
    ["primary-active", ALL, 0.788,0.514,0.157,  0.847,0.580,0.196],
    ["destructive",    ALL, 0.753,0.224,0.169,  0.906,0.298,0.235],
    ["ring",           ALL, 0.902,0.635,0.235,  0.941,0.690,0.290],
    ["status-success", ALL, 0.286,0.427,0.243,  0.525,0.714,0.478],
    ["status-warning", ALL, 0.541,0.353,0.071,  0.824,0.749,0.545],
    ["status-error",   ALL, 0.635,0.263,0.169,  0.847,0.557,0.455],
    ["status-info",    ALL, 0.345,0.420,0.478,  0.616,0.714,0.784],
  ];

  // ── 3. Radius tokens (FLOAT) ─────────────────────────────
  // [name, value]

  var RADIUS_TOKENS = [
    ["radius/xs",   4],
    ["radius/sm",  10],
    ["radius/md",  14],
    ["radius/lg",  18],
    ["radius/xl",  22],
    ["radius/full", 9999],
  ];

  // ── 4. Spacing tokens (FLOAT) ────────────────────────────
  // [name, value]

  var SPACING_TOKENS = [
    ["spacing/0",   0],
    ["spacing/1",   4],
    ["spacing/2",   8],
    ["spacing/3",  12],
    ["spacing/4",  16],
    ["spacing/5",  20],
    ["spacing/6",  24],
    ["spacing/8",  32],
    ["spacing/10", 40],
    ["spacing/12", 48],
  ];

  // ── 5. Create / update all variables ─────────────────────

  var created = 0;
  var updated = 0;

  function bump(isNew) { isNew ? created++ : updated++; }

  // -- Colors
  COLOR_TOKENS.forEach(function (t) {
    var name = t[0];
    var scopes = t[1];
    var isNew = !findVariable(name, cid);
    var v = ensureVariable(name, cid, "COLOR");

    v.setValueForMode(lightId, { r: t[2], g: t[3], b: t[4], a: 1 });
    v.setValueForMode(darkId,  { r: t[5], g: t[6], b: t[7], a: 1 });
    v.scopes = scopes;

    bump(isNew);
  });

  // -- Radius
  RADIUS_TOKENS.forEach(function (t) {
    var name = t[0];
    var value = t[1];
    var isNew = !findVariable(name, cid);
    var v = ensureVariable(name, cid, "FLOAT");

    v.setValueForMode(lightId, value);
    v.setValueForMode(darkId, value);
    v.scopes = RADIUS_SCOPE;

    bump(isNew);
  });

  // -- Spacing
  SPACING_TOKENS.forEach(function (t) {
    var name = t[0];
    var value = t[1];
    var isNew = !findVariable(name, cid);
    var v = ensureVariable(name, cid, "FLOAT");

    v.setValueForMode(lightId, value);
    v.setValueForMode(darkId, value);
    v.scopes = SPACING_SCOPE;

    bump(isNew);
  });

  // ── Done ─────────────────────────────────────────────────

  figma.notify(
    "✅ Liquid Crystal — " + created + " created, " + updated + " updated"
  );
  figma.closePlugin();

})();
