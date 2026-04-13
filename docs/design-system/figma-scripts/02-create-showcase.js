// ============================================================
// 02 – Token Showcase Frame
// Creates a page "01 Tokens" with visual documentation for
// all color, radius, and spacing design tokens.
// ------------------------------------------------------------
// Requires that Script 01 has been run first (variables exist).
// Paste into Figma Console: Plugins → Development → Console
// Safe to re-run: clears the page and rebuilds.
// ============================================================

// ── Color data (name, lightHex, lightR, lightG, lightB, darkHex, darkR, darkG, darkB) ──

var COLOR_TOKENS = [
  // Surfaces
  ["background",      "#F7F1E8",0.969,0.945,0.910,  "#120E0A",0.071,0.055,0.039],
  ["surface-base",    "#FFF9F2",1.000,0.976,0.949,  "#1A140F",0.102,0.078,0.059],
  ["surface-raised",  "#FCF6EE",0.988,0.965,0.933,  "#231B14",0.137,0.106,0.078],
  ["surface-sunken",  "#F6E6CA",0.965,0.902,0.792,  "#0F0B08",0.059,0.043,0.031],
  // Foregrounds
  ["foreground",            "#2B2116",0.169,0.129,0.086,  "#F8F1E7",0.973,0.945,0.906],
  ["muted-foreground",      "#78624B",0.471,0.384,0.294,  "#C7B69F",0.780,0.714,0.624],
  // Primary
  ["primary",               "#E6A23C",0.902,0.635,0.235,  "#F0B04A",0.941,0.690,0.290],
  ["primary-foreground",    "#2B2116",0.169,0.129,0.086,  "#2B2116",0.169,0.129,0.086],
  ["primary-hover",         "#D89432",0.847,0.580,0.196,  "#F4C97B",0.957,0.788,0.482],
  ["primary-active",        "#C98328",0.788,0.514,0.157,  "#D89432",0.847,0.580,0.196],
  // Secondary
  ["secondary",             "#FCF6EE",0.988,0.965,0.933,  "#231B14",0.137,0.106,0.078],
  ["secondary-foreground",  "#2B2116",0.169,0.129,0.086,  "#F8F1E7",0.973,0.945,0.906],
  // Card
  ["card",                  "#FFF9F2",1.000,0.976,0.949,  "#1A140F",0.102,0.078,0.059],
  ["card-foreground",       "#2B2116",0.169,0.129,0.086,  "#F8F1E7",0.973,0.945,0.906],
  // Muted
  ["muted",                 "#F0E8DA",0.941,0.910,0.855,  "#1A140F",0.102,0.078,0.059],
  // Accent
  ["accent",                "#F6E6CA",0.965,0.902,0.792,  "#31261C",0.192,0.149,0.110],
  ["accent-foreground",     "#2B2116",0.169,0.129,0.086,  "#F8F1E7",0.973,0.945,0.906],
  ["accent-muted",          "#F8EDD5",0.973,0.929,0.835,  "#29201A",0.161,0.125,0.102],
  // Destructive
  ["destructive",           "#C0392B",0.753,0.224,0.169,  "#E74C3C",0.906,0.298,0.235],
  ["destructive-foreground","#FFF9F2",1.000,0.976,0.949,  "#F8F1E7",0.973,0.945,0.906],
  // Border & Input
  ["border",                "#DCC7A7",0.863,0.780,0.655,  "#5A4630",0.353,0.275,0.188],
  ["input",                 "#DCC7A7",0.863,0.780,0.655,  "#5A4630",0.353,0.275,0.188],
  // Ring
  ["ring",                  "#E6A23C",0.902,0.635,0.235,  "#F0B04A",0.941,0.690,0.290],
  // Status
  ["status-success",        "#496D3E",0.286,0.427,0.243,  "#86B67A",0.525,0.714,0.478],
  ["status-success-bg",     "#EAF2E6",0.918,0.949,0.902,  "#1A2616",0.102,0.149,0.086],
  ["status-warning",        "#8A5A12",0.541,0.353,0.071,  "#D2BF8B",0.824,0.749,0.545],
  ["status-warning-bg",     "#FBF0D9",0.984,0.941,0.851,  "#29201A",0.161,0.125,0.102],
  ["status-error",          "#A2432B",0.635,0.263,0.169,  "#D88E74",0.847,0.557,0.455],
  ["status-error-bg",       "#F8E6E0",0.973,0.902,0.878,  "#261612",0.149,0.086,0.071],
  ["status-info",           "#586B7A",0.345,0.420,0.478,  "#9DB6C8",0.616,0.714,0.784],
  ["status-info-bg",        "#E8EDF2",0.910,0.929,0.949,  "#161C24",0.086,0.110,0.141],
];

// Group definitions for visual sectioning
var COLOR_GROUPS = [
  { name: "Surfaces",   tokens: ["background","surface-base","surface-raised","surface-sunken"] },
  { name: "Foreground",  tokens: ["foreground","muted-foreground"] },
  { name: "Primary",     tokens: ["primary","primary-foreground","primary-hover","primary-active"] },
  { name: "Secondary",   tokens: ["secondary","secondary-foreground"] },
  { name: "Card",        tokens: ["card","card-foreground"] },
  { name: "Muted",       tokens: ["muted"] },
  { name: "Accent",      tokens: ["accent","accent-foreground","accent-muted"] },
  { name: "Destructive", tokens: ["destructive","destructive-foreground"] },
  { name: "Border",      tokens: ["border","input","ring"] },
  { name: "Status",      tokens: ["status-success","status-success-bg","status-warning","status-warning-bg","status-error","status-error-bg","status-info","status-info-bg"] },
];

var RADIUS_TOKENS = [
  ["radius/xs",   4],
  ["radius/sm",  10],
  ["radius/md",  14],
  ["radius/lg",  18],
  ["radius/xl",  22],
  ["radius/full", 9999],
];

var SPACING_TOKENS = [
  ["spacing/0",  0],
  ["spacing/1",  4],
  ["spacing/2",  8],
  ["spacing/3", 12],
  ["spacing/4", 16],
  ["spacing/5", 20],
  ["spacing/6", 24],
  ["spacing/8", 32],
  ["spacing/10",40],
  ["spacing/12",48],
];

// ── Build a lookup map for fast access ────────────────────

var colorMap = {};
COLOR_TOKENS.forEach(function (t) {
  colorMap[t[0]] = {
    lightHex: t[1], lightR: t[2], lightG: t[3], lightB: t[4],
    darkHex:  t[5], darkR:  t[6], darkG:  t[7], darkB:  t[8],
  };
});

// ── Find a usable font ────────────────────────────────────

function findAndLoadFont() {
  return figma.listAvailableFontsAsync().then(function (fonts) {
    // Prefer Inter → Roboto → first available
    var fontName = null;

    for (var i = 0; i < fonts.length; i++) {
      if (fonts[i].fontFamily === "Inter") {
        fontName = { family: "Inter", style: "Regular" };
        break;
      }
    }
    if (!fontName) {
      for (var j = 0; j < fonts.length; j++) {
        if (fonts[j].fontFamily === "Roboto") {
          fontName = { family: "Roboto", style: "Regular" };
          break;
        }
      }
    }
    if (!fontName && fonts.length > 0) {
      fontName = {
        family: fonts[0].fontFamily,
        style: fonts[0].fontStyles[0].name,
      };
    }

    if (!fontName) {
      throw new Error("No fonts available");
    }

    return figma.loadFontAsync(fontName).then(function () {
      return fontName;
    });
  });
}

// ── Node factory helpers ──────────────────────────────────

function makeFrame(name, layout, gap, pad) {
  var f = figma.createFrame();
  f.name = name;
  f.layoutMode = layout;                       // "HORIZONTAL" | "VERTICAL"
  f.primaryAxisSizingMode   = "AUTO";
  f.counterAxisSizingMode   = "AUTO";
  f.itemSpacing   = gap || 0;
  f.paddingLeft   = pad || 0;
  f.paddingRight  = pad || 0;
  f.paddingTop    = pad || 0;
  f.paddingBottom = pad || 0;
  f.clipsContent  = false;
  return f;
}

function makeText(font, chars, size, color) {
  var t = figma.createText();
  t.fontName = font;
  t.fontSize = size || 11;
  t.characters = chars;
  t.fills = [{ type: "SOLID", color: color || { r: 0.17, g: 0.13, b: 0.09 } }];
  t.textAutoResize = "WIDTH_AND_HEIGHT";
  return t;
}

function makeSwatch(w, h, r, g, b, radius) {
  var rect = figma.createRectangle();
  rect.resize(w, h);
  rect.cornerRadius = radius || 8;
  rect.fills = [{ type: "SOLID", color: { r: r, g: g, b: b } }];
  return rect;
}

// ── Main builder ──────────────────────────────────────────

function buildShowcase(font) {

  // -- Page ------------------------------------------------
  var page = figma.root.children.find(function (p) {
    return p.name === "01 Tokens";
  });
  if (!page) {
    page = figma.createPage();
    page.name = "01 Tokens";
  }
  // Clear previous content
  var children = page.children.slice();
  children.forEach(function (c) { c.remove(); });
  figma.currentPage = page;

  // -- Root frame ------------------------------------------
  var root = makeFrame("Design Tokens Showcase", "VERTICAL", 48, 48);
  root.fills = [{ type: "SOLID", color: { r: 0.969, g: 0.945, b: 0.910 } }];
  root.counterAxisAlignItems = "MIN";
  page.appendChild(root);

  // -- Title -----------------------------------------------
  var title = makeText(font, "Liquid Crystal — Design Tokens", 24, { r: 0.169, g: 0.129, b: 0.086 });
  root.appendChild(title);

  // ═══════════════════════════════════════════════════════
  //  COLOR SECTION
  // ═══════════════════════════════════════════════════════

  var colorSection = makeFrame("Colors", "VERTICAL", 24, 0);
  root.appendChild(colorSection);

  var colorTitle = makeText(font, "Color Tokens", 16, { r: 0.169, g: 0.129, b: 0.086 });
  colorSection.appendChild(colorTitle);

  // -- Column header
  var header = makeFrame("Header", "HORIZONTAL", 12, 0);
  colorSection.appendChild(header);
  // Spacer to align with swatches
  var hSp = makeFrame("spacer", "HORIZONTAL", 0, 0);
  hSp.resize(108, 1);
  header.appendChild(hSp);
  header.appendChild(makeText(font, "Light", 10, { r: 0.471, g: 0.384, b: 0.294 }));
  var hSp2 = makeFrame("spacer", "HORIZONTAL", 0, 0);
  hSp2.resize(20, 1);
  header.appendChild(hSp2);
  header.appendChild(makeText(font, "Dark", 10, { r: 0.471, g: 0.384, b: 0.294 }));

  // -- Groups
  COLOR_GROUPS.forEach(function (group) {
    var groupFrame = makeFrame(group.name, "VERTICAL", 8, 0);
    colorSection.appendChild(groupFrame);

    var groupLabel = makeText(font, group.name, 12, { r: 0.471, g: 0.384, b: 0.294 });
    groupFrame.appendChild(groupLabel);

    group.tokens.forEach(function (tokenName) {
      var d = colorMap[tokenName];
      if (!d) return;

      var row = makeFrame(tokenName, "HORIZONTAL", 12, 0);
      row.counterAxisAlignItems = "CENTER";
      groupFrame.appendChild(row);

      // Light swatch
      row.appendChild(makeSwatch(48, 28, d.lightR, d.lightG, d.lightB, 6));
      // Dark swatch
      row.appendChild(makeSwatch(48, 28, d.darkR, d.darkG, d.darkB, 6));
      // Token name + hex
      var nameFrame = makeFrame("name", "VERTICAL", 2, 0);
      row.appendChild(nameFrame);
      nameFrame.appendChild(makeText(font, tokenName, 11, { r: 0.169, g: 0.129, b: 0.086 }));
      nameFrame.appendChild(makeText(font, d.lightHex + " / " + d.darkHex, 9, { r: 0.471, g: 0.384, b: 0.294 }));
    });
  });

  // ═══════════════════════════════════════════════════════
  //  RADIUS SECTION
  // ═══════════════════════════════════════════════════════

  var radiusSection = makeFrame("Radius", "VERTICAL", 16, 0);
  root.appendChild(radiusSection);

  var radiusTitle = makeText(font, "Radius Tokens", 16, { r: 0.169, g: 0.129, b: 0.086 });
  radiusSection.appendChild(radiusTitle);

  var radiusRow = makeFrame("radius swatches", "HORIZONTAL", 16, 0);
  radiusRow.counterAxisAlignItems = "MIN";
  radiusSection.appendChild(radiusRow);

  RADIUS_TOKENS.forEach(function (t) {
    var cell = makeFrame(t[0], "VERTICAL", 8, 0);
    cell.counterAxisAlignItems = "CENTER";
    radiusRow.appendChild(cell);

    var rect = figma.createRectangle();
    rect.resize(56, 56);
    rect.cornerRadius = Math.min(t[1], 28);   // cap visual radius
    rect.fills = [{ type: "SOLID", color: { r: 0.902, g: 0.635, b: 0.235 } }];
    rect.strokes = [{ type: "SOLID", color: { r: 0.863, g: 0.780, b: 0.655 } }];
    rect.strokeWeight = 1;
    cell.appendChild(rect);

    cell.appendChild(makeText(font, t[0], 10, { r: 0.169, g: 0.129, b: 0.086 }));
    cell.appendChild(makeText(font, String(t[1]) + " px", 9, { r: 0.471, g: 0.384, b: 0.294 }));
  });

  // ═══════════════════════════════════════════════════════
  //  SPACING SECTION
  // ═══════════════════════════════════════════════════════

  var spacingSection = makeFrame("Spacing", "VERTICAL", 16, 0);
  root.appendChild(spacingSection);

  var spacingTitle = makeText(font, "Spacing Tokens", 16, { r: 0.169, g: 0.129, b: 0.086 });
  spacingSection.appendChild(spacingTitle);

  var spacingRow = makeFrame("spacing swatches", "HORIZONTAL", 24, 0);
  spacingRow.counterAxisAlignItems = "MIN";
  spacingSection.appendChild(spacingRow);

  SPACING_TOKENS.forEach(function (t) {
    var cell = makeFrame(t[0], "VERTICAL", 6, 0);
    cell.counterAxisAlignItems = "CENTER";
    spacingRow.appendChild(cell);

    // Visual bar — width proportional to value (capped for display)
    var barW = Math.max(t[1], 2);              // minimum 2 px visible
    var bar = figma.createRectangle();
    bar.resize(barW, 24);
    bar.cornerRadius = 4;
    bar.fills = [{ type: "SOLID", color: { r: 0.902, g: 0.635, b: 0.235 } }];
    cell.appendChild(bar);

    cell.appendChild(makeText(font, t[0], 10, { r: 0.169, g: 0.129, b: 0.086 }));
    cell.appendChild(makeText(font, t[1] + " px", 9, { r: 0.471, g: 0.384, b: 0.294 }));
  });

  // -- Final viewport --------------------------------------
  figma.viewport.scrollAndZoomIntoView([root]);

  figma.notify("✅ Token showcase created on page \"01 Tokens\"");
  figma.closePlugin();
}

// ── Entry point ───────────────────────────────────────────

findAndLoadFont()
  .then(function (font) {
    buildShowcase(font);
  })
  .catch(function (err) {
    figma.notify("❌ " + (err.message || err));
    figma.closePlugin();
  });
