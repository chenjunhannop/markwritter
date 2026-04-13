// ============================================================
// 03 – Create Button & Badge Component Sets
// Creates page "02 Components" with:
//   • Button — 6 variants × 4 sizes = 24 component instances
//   • Badge  — 8 variants              = 8  component instances
// ------------------------------------------------------------
// Paste into Figma Console: Plugins → Development → Console
// Safe to re-run: removes existing sets and recreates them.
// ============================================================

(function () {
  "use strict";

  // ═══════════════════════════════════════════════════════════
  //  COLOR TOKENS  (0–1 RGB, Light mode – matches Script 01)
  // ═══════════════════════════════════════════════════════════

  var C = {
    primary:           { r: 0.902, g: 0.635, b: 0.235 },
    primaryFg:         { r: 0.169, g: 0.129, b: 0.086 },
    primaryHover:      { r: 0.847, g: 0.580, b: 0.196 },
    destructive:       { r: 0.753, g: 0.224, b: 0.169 },
    destructiveFg:     { r: 1.000, g: 0.976, b: 0.949 },
    foreground:        { r: 0.169, g: 0.129, b: 0.086 },
    border:            { r: 0.863, g: 0.780, b: 0.655 },
    secondary:         { r: 0.988, g: 0.965, b: 0.933 },
    secondaryFg:       { r: 0.169, g: 0.129, b: 0.086 },
    accent:            { r: 0.965, g: 0.902, b: 0.792 },
    successBg:         { r: 0.918, g: 0.949, b: 0.902 },
    success:           { r: 0.286, g: 0.427, b: 0.243 },
    warningBg:         { r: 0.984, g: 0.941, b: 0.851 },
    warning:           { r: 0.541, g: 0.353, b: 0.071 },
    errorBg:           { r: 0.973, g: 0.902, b: 0.878 },
    error:             { r: 0.635, g: 0.263, b: 0.169 },
    infoBg:            { r: 0.910, g: 0.929, b: 0.949 },
    info:              { r: 0.345, g: 0.420, b: 0.478 },
  };

  // ═══════════════════════════════════════════════════════════
  //  HELPERS
  // ═══════════════════════════════════════════════════════════

  /** Create a solid Paint object from an {r,g,b} token. */
  function solid(color, opacity) {
    var p = { type: "SOLID", color: { r: color.r, g: color.g, b: color.b } };
    if (opacity !== undefined) { p.opacity = opacity; }
    return p;
  }

  /**
   * Load a font with graceful fallback:
   *   1. Exact match  → use it
   *   2. Same family  → first style
   *   3. Any font     → first available
   * Returns the resolved fontName object.
   */
  function loadFontSafe(desired) {
    return figma.loadFontAsync(desired)
      .then(function () { return desired; })
      .catch(function () {
        return figma.listAvailableFontsAsync().then(function (list) {
          var same = list.filter(function (f) {
            return f.fontName.family === desired.family;
          });
          if (same.length) {
            var pick = same[0].fontName;
            return figma.loadFontAsync(pick).then(function () { return pick; });
          }
          if (list.length) {
            return figma.loadFontAsync(list[0].fontName).then(function () {
              return list[0].fontName;
            });
          }
          return Promise.reject(new Error("No fonts available"));
        });
      });
  }

  // ═══════════════════════════════════════════════════════════
  //  PAGE SETUP & IDEMPOTENCY
  // ═══════════════════════════════════════════════════════════

  var page = figma.root.children.find(function (p) {
    return p.name === "02 Components";
  });
  if (!page) {
    page = figma.createPage();
    page.name = "02 Components";
  }
  figma.currentPage = page;

  // Remove existing Button / Badge component sets so re-runs are clean
  var toDelete = [];
  for (var i = 0; i < page.children.length; i++) {
    var child = page.children[i];
    if (
      child.type === "COMPONENT_SET" &&
      (child.name === "Button" || child.name === "Badge")
    ) {
      toDelete.push(child);
    }
  }
  toDelete.forEach(function (n) { n.remove(); });

  // ═══════════════════════════════════════════════════════════
  //  CONFIGURATION
  // ═══════════════════════════════════════════════════════════

  // ── Button variants (6) ────────────────────────────────────
  var BTN_VARIANTS = {
    default: {
      bg:   [solid(C.primary)],
      txt:  C.primaryFg,
      stk:  [],
      sw:   0,
    },
    destructive: {
      bg:   [solid(C.destructive)],
      txt:  C.destructiveFg,
      stk:  [],
      sw:   0,
    },
    outline: {
      bg:   [],
      txt:  C.foreground,
      stk:  [solid(C.border)],
      sw:   1,
    },
    secondary: {
      bg:   [solid(C.secondary)],
      txt:  C.secondaryFg,
      stk:  [solid(C.border)],
      sw:   1,
    },
    ghost: {
      bg:   [],
      txt:  C.foreground,
      stk:  [],
      sw:   0,
    },
    link: {
      bg:   [],
      txt:  C.primary,
      stk:  [],
      sw:   0,
    },
  };

  // ── Button sizes (4) ───────────────────────────────────────
  var BTN_SIZES = {
    sm:       { h: 32, px: 12, py: 4,  fs: 14, gap: 6,  r: 10 },
    "default": { h: 38, px: 16, py: 6,  fs: 15, gap: 8,  r: 10 },
    lg:       { h: 44, px: 24, py: 8,  fs: 15, gap: 8,  r: 10 },
    icon:     { h: 38, px: 0,  py: 0,  fs: 0,  gap: 0,  r: 10 },
  };

  var VARIANT_KEYS = ["default", "destructive", "outline", "secondary", "ghost", "link"];
  var SIZE_KEYS    = ["sm", "default", "lg", "icon"];

  // ── Badge variants (8) ─────────────────────────────────────
  var BDG_VARIANTS = {
    "default":   { bg: [solid(C.primary)],     txt: C.primaryFg,     stk: [],                sw: 0 },
    secondary:   { bg: [solid(C.secondary)],    txt: C.secondaryFg,   stk: [solid(C.border)], sw: 1 },
    destructive: { bg: [solid(C.destructive)],  txt: C.destructiveFg, stk: [],                sw: 0 },
    outline:     { bg: [],                       txt: C.foreground,    stk: [solid(C.border)], sw: 1 },
    success:     { bg: [solid(C.successBg)],     txt: C.success,       stk: [],                sw: 0 },
    warning:     { bg: [solid(C.warningBg)],     txt: C.warning,       stk: [],                sw: 0 },
    error:       { bg: [solid(C.errorBg)],       txt: C.error,         stk: [],                sw: 0 },
    info:        { bg: [solid(C.infoBg)],        txt: C.info,          stk: [],                sw: 0 },
  };

  var BADGE_KEYS = [
    "default", "secondary", "destructive", "outline",
    "success", "warning", "error", "info",
  ];

  // ═══════════════════════════════════════════════════════════
  //  FONT LOADING → BUILD
  // ═══════════════════════════════════════════════════════════

  var FONT_REG = { family: "Inter", style: "Regular" };
  var FONT_MED = { family: "Inter", style: "Medium" };
  var fonts    = { regular: FONT_REG, medium: FONT_MED };

  loadFontSafe(FONT_REG)
    .then(function (f) { fonts.regular = f; })
    .then(function () {
      return loadFontSafe(FONT_MED)
        .then(function (f) { fonts.medium = f; })
        .catch(function () { fonts.medium = fonts.regular; });
    })
    .then(function () {

      // ═════════════════════════════════════════════════════
      //  SECTION HEADER HELPER
      // ═════════════════════════════════════════════════════

      /** Create a small section label frame above a component set. */
      function sectionLabel(text) {
        var frame = figma.createFrame();
        frame.name = "Section: " + text;
        frame.layoutMode = "HORIZONTAL";
        frame.primaryAxisSizingMode = "AUTO";
        frame.counterAxisSizingMode = "AUTO";
        frame.itemSpacing = 0;
        frame.paddingLeft = 0;
        frame.paddingRight = 0;
        frame.paddingTop = 0;
        frame.paddingBottom = 0;
        frame.fills = [];

        var lbl = figma.createText();
        lbl.fontName = fonts.regular;
        lbl.fontSize = 13;
        lbl.characters = text;
        lbl.fills = [solid({ r: 0.471, g: 0.384, b: 0.294 })];
        frame.appendChild(lbl);
        return frame;
      }

      // ═════════════════════════════════════════════════════
      //  BUTTON COMPONENT SET  (6 variants × 4 sizes = 24)
      // ═════════════════════════════════════════════════════

      var btnComps = [];
      var btnMeta  = [];

      VARIANT_KEYS.forEach(function (vk) {
        SIZE_KEYS.forEach(function (sk) {
          var v = BTN_VARIANTS[vk];
          var s = BTN_SIZES[sk];

          var comp = figma.createComponent();
          comp.name = "variant=" + vk + ", size=" + sk;

          // ── Auto-layout (horizontal, center-aligned) ──
          comp.layoutMode = "HORIZONTAL";
          comp.primaryAxisAlignItems   = "CENTER";
          comp.counterAxisAlignItems   = "CENTER";
          comp.itemSpacing    = s.gap;
          comp.paddingLeft    = s.px;
          comp.paddingRight   = s.px;
          comp.paddingTop     = s.py;
          comp.paddingBottom  = s.py;
          comp.cornerRadius   = s.r;

          // ── Fills & strokes ──
          comp.fills = v.bg;
          if (v.stk.length) {
            comp.strokes     = v.stk;
            comp.strokeWeight = v.sw;
            comp.strokeAlign  = "INSIDE";
          } else {
            comp.strokes = [];
          }

          // ── Content child ──
          if (sk === "icon") {
            // Icon placeholder: 20×20 rounded rect
            var ico = figma.createRectangle();
            ico.resize(20, 20);
            ico.fills = [solid({ r: 0.6, g: 0.6, b: 0.6 }, 0.3)];
            ico.cornerRadius = 4;
            ico.name = "Icon";
            comp.appendChild(ico);
          } else {
            var lbl = figma.createText();
            lbl.fontName  = fonts.regular;
            lbl.fontSize  = s.fs;
            lbl.characters = "Button";
            lbl.name      = "Label";
            lbl.fills     = [solid(v.txt)];
            lbl.textAutoResize = "WIDTH_AND_HEIGHT";
            comp.appendChild(lbl);
          }

          // ── Fixed height (counter axis) ──
          comp.counterAxisSizingMode = "FIXED";
          comp.resize(comp.width, s.h);

          // ── Icon variant: also fix width → square ──
          if (sk === "icon") {
            try {
              comp.primaryAxisSizingMode = "FIXED";
            } catch (e) {
              // Fallback for older API: stretch icon to fill
              try { ico.resize(s.h, s.h); } catch (ignored) {}
            }
            comp.resize(s.h, s.h);
          }

          btnComps.push(comp);
          btnMeta.push({ comp: comp, variant: vk, size: sk });
        });
      });

      // Combine into ComponentSet
      var btnSet = figma.combineAsVariants(btnComps, page);
      btnSet.name = "Button";
      btnSet.x = 100;
      btnSet.y = 100;
      btnSet.itemSpacing = 16;

      // Set variant properties after combining (maximum compatibility)
      btnMeta.forEach(function (m) {
        m.comp.variantProperties = { variant: m.variant, size: m.size };
      });

      // Section label above Button set
      var btnLabel = sectionLabel("Button");
      btnLabel.x = 100;
      btnLabel.y = btnSet.y - 28;
      page.appendChild(btnLabel);

      // ═════════════════════════════════════════════════════
      //  BADGE COMPONENT SET  (8 variants)
      // ═════════════════════════════════════════════════════

      var bdgComps = [];
      var bdgMeta  = [];

      BADGE_KEYS.forEach(function (vk) {
        var v = BDG_VARIANTS[vk];

        var comp = figma.createComponent();
        comp.name = "variant=" + vk;

        // ── Auto-layout (horizontal, center-aligned) ──
        comp.layoutMode = "HORIZONTAL";
        comp.primaryAxisAlignItems   = "CENTER";
        comp.counterAxisAlignItems   = "CENTER";
        comp.itemSpacing    = 0;
        comp.paddingLeft    = 8;
        comp.paddingRight   = 8;
        comp.paddingTop     = 0;
        comp.paddingBottom  = 0;
        comp.cornerRadius   = 6;

        // ── Fills & strokes ──
        comp.fills = v.bg;
        if (v.stk.length) {
          comp.strokes      = v.stk;
          comp.strokeWeight = v.sw;
          comp.strokeAlign  = "INSIDE";
        } else {
          comp.strokes = [];
        }

        // ── Text child ──
        var lbl = figma.createText();
        lbl.fontName   = fonts.medium;
        lbl.fontSize   = 11;
        lbl.characters  = "Badge";
        lbl.name       = "Label";
        lbl.fills      = [solid(v.txt)];
        lbl.textAutoResize = "WIDTH_AND_HEIGHT";
        comp.appendChild(lbl);

        // ── Fixed height (counter axis) ──
        comp.counterAxisSizingMode = "FIXED";
        comp.resize(comp.width, 20);

        bdgComps.push(comp);
        bdgMeta.push({ comp: comp, variant: vk });
      });

      // Combine into ComponentSet
      var bdgSet = figma.combineAsVariants(bdgComps, page);
      bdgSet.name = "Badge";
      bdgSet.x = 100;
      bdgSet.y = btnSet.y + btnSet.height + 80;
      bdgSet.itemSpacing = 16;

      // Set variant properties after combining
      bdgMeta.forEach(function (m) {
        m.comp.variantProperties = { variant: m.variant };
      });

      // Section label above Badge set
      var bdgLabel = sectionLabel("Badge");
      bdgLabel.x = 100;
      bdgLabel.y = bdgSet.y - 28;
      page.appendChild(bdgLabel);

      // ═════════════════════════════════════════════════════
      //  DONE
      // ═════════════════════════════════════════════════════

      figma.viewport.scrollAndZoomIntoView([btnSet, bdgSet]);

      figma.notify(
        "✅ Created Button (24 variants) + Badge (8 variants) on \"02 Components\""
      );
      figma.closePlugin();
    })
    .catch(function (err) {
      figma.notify("❌ " + (err.message || String(err)), { timeout: 5000 });
      figma.closePlugin();
    });

})();
