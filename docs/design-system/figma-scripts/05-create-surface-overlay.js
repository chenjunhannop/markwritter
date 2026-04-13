// ============================================================
// 05 – Create Surface & Overlay Components
// Card, Dialog, Sheet, Popover, Tooltip, Tabs, Separator
// ------------------------------------------------------------
// Paste into Figma Console: Plugins → Development → Console
// Safe to re-run: removes existing sets and recreates them.
// Requires page "02 Components" (created by Script 03).
// ============================================================

(function () {
  "use strict";

  var C = {
    foreground:       { r: 0.169, g: 0.129, b: 0.086 },
    mutedFg:          { r: 0.471, g: 0.384, b: 0.294 },
    primary:          { r: 0.902, g: 0.635, b: 0.235 },
    border:           { r: 0.863, g: 0.780, b: 0.655 },
    surfaceBase:      { r: 1.000, g: 0.976, b: 0.949 },
    accent:           { r: 0.965, g: 0.902, b: 0.792 },
    accentDark:       { r: 0.192, g: 0.149, b: 0.110 },
    darkInk:          { r: 0.169, g: 0.129, b: 0.086 },
    warmWhite:        { r: 0.973, g: 0.945, b: 0.906 },
    white:            { r: 1.000, g: 1.000, b: 1.000 },
    black:            { r: 0.000, g: 0.000, b: 0.000 },
    statusInfo:       { r: 0.345, g: 0.420, b: 0.478 },
    statusSuccess:    { r: 0.286, g: 0.427, b: 0.243 },
    statusWarning:    { r: 0.541, g: 0.353, b: 0.071 },
    statusError:      { r: 0.635, g: 0.263, b: 0.169 },
  };

  function solid(color, opacity) {
    var p = { type: "SOLID", color: { r: color.r, g: color.g, b: color.b } };
    if (opacity !== undefined) p.opacity = opacity;
    return p;
  }

  function setFills(node, color, opacity) { node.fills = [solid(color, opacity)]; }
  function setStrokes(node, color, opacity, weight) {
    node.strokes = [solid(color, opacity)];
    node.strokeWeight = weight || 1;
  }

  function findPage(name) {
    return figma.root.children.find(function (p) { return p.name === name; });
  }

  function getRightmostX(page) {
    var maxX = 100;
    for (var i = 0; i < page.children.length; i++) {
      var child = page.children[i];
      if (child.x + child.width + 200 > maxX) maxX = child.x + child.width + 200;
    }
    return maxX;
  }

  function makeFrame(name, x, y, w, h) {
    var f = figma.createFrame();
    f.name = name;
    f.x = x;
    f.y = y;
    f.resize(w, h);
    return f;
  }

  function makeText(name, chars, fontSize, fontWeight, color) {
    var t = figma.createText();
    t.name = name;
    figma.loadFontAsync({ family: "Inter", style: fontWeight >= 600 ? "Semi Bold" : "Regular" })
      .then(function () {
        t.characters = chars;
        t.fontSize = fontSize;
        t.fontName = { family: "Inter", style: fontWeight >= 600 ? "Semi Bold" : "Regular" };
      })
      .catch(function () {
        figma.loadFontAsync({ family: "Roboto", style: fontWeight >= 600 ? "Bold" : "Regular" })
          .then(function () {
            t.characters = chars;
            t.fontSize = fontSize;
            t.fontName = { family: "Roboto", style: fontWeight >= 600 ? "Bold" : "Regular" };
          });
      });
    setFills(t, color);
    return t;
  }

  function autoLayout(node, dir, padH, padV, gap, primary, counter) {
    node.layoutMode = dir;
    node.primaryAxisSizingMode = primary || "AUTO";
    node.counterAxisSizingMode = counter || "AUTO";
    node.paddingLeft = padH;
    node.paddingRight = padH;
    node.paddingTop = padV;
    node.paddingBottom = padV;
    node.itemSpacing = gap || 0;
  }

  var page = findPage("02 Components");
  if (!page) {
    figma.notify("Page '02 Components' not found. Run Script 03 first.");
    return;
  }

  var startX = getRightmostX(page);
  var cx = startX;
  var cy = 100;
  var SET_W = 900;

  // ──────────────────────────────────────────────────────────
  // SECTION HEADER
  // ──────────────────────────────────────────────────────────
  var header = makeText("Section: Surface & Overlay", "SURFACE & OVERLAY", 20, 600, C.foreground);
  header.x = cx;
  header.y = cy;
  page.appendChild(header);
  cy += 50;

  // ──────────────────────────────────────────────────────────
  // 1. CARD (default + elevated)
  // ──────────────────────────────────────────────────────────
  var cardSet = makeFrame("Card", cx, cy, SET_W, 300);
  autoLayout(cardSet, "HORIZONTAL", 0, 0, 40, "FIXED", "AUTO");
  page.appendChild(cardSet);

  ["default", "elevated"].forEach(function (variant) {
    var isElevated = variant === "elevated";
    var card = makeFrame("Card/" + variant, 0, 0, 280, 0);
    autoLayout(card, "VERTICAL", 0, 0, 0, "FIXED", "AUTO");
    card.cornerRadius = 14;
    card.overflow = "HIDDEN";

    var bgOpacity = isElevated ? 0.65 : 0.55;
    setFills(card, C.white, bgOpacity);
    setStrokes(card, C.white, isElevated ? 0.40 : 0.35, 1);

    if (isElevated) {
      card.effects = [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.08 }, offset: { x: 0, y: 4 }, radius: 12, spread: 0, visible: true }];
    } else {
      card.effects = [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.06 }, offset: { x: 0, y: 1 }, radius: 3, spread: 0, visible: true }];
    }

    var cardHeader = makeFrame("CardHeader", 0, 0, 280, 0);
    autoLayout(cardHeader, "VERTICAL", 24, 24, 8, "FIXED", "AUTO");
    var title = makeText("CardTitle", "Card Title", 18, 600, C.foreground);
    var desc = makeText("CardDescription", "Card description text.", 14, 400, C.mutedFg);
    cardHeader.appendChild(title);
    cardHeader.appendChild(desc);
    card.appendChild(cardHeader);

    var content = makeFrame("CardContent", 0, 0, 280, 0);
    autoLayout(content, "VERTICAL", 24, 0, 0, "FIXED", "AUTO");
    var contentText = makeText("Content", "Card content goes here with some additional text to show spacing.", 14, 400, C.foreground);
    content.appendChild(contentText);
    card.appendChild(content);

    var footer = makeFrame("CardFooter", 0, 0, 280, 0);
    autoLayout(footer, "HORIZONTAL", 24, 24, 8, "FIXED", "AUTO");
    var btn1 = makeFrame("Button/outline", 0, 0, 0, 32);
    autoLayout(btn1, "HORIZONTAL", 12, 6, 0, "AUTO", "FIXED");
    setFills(btn1, C.border);
    btn1.cornerRadius = 8;
    var btn1Text = makeText("Label", "Cancel", 13, 500, C.foreground);
    btn1.appendChild(btn1Text);
    footer.appendChild(btn1);

    var btn2 = makeFrame("Button/default", 0, 0, 0, 32);
    autoLayout(btn2, "HORIZONTAL", 12, 6, 0, "AUTO", "FIXED");
    setFills(btn2, C.primary);
    btn2.cornerRadius = 8;
    var btn2Text = makeText("Label", "Confirm", 13, 500, C.darkInk);
    btn2.appendChild(btn2Text);
    footer.appendChild(btn2);
    card.appendChild(footer);

    cardSet.appendChild(card);
  });

  // Label
  var cardLabel = makeText("Card Label", "Card", 14, 600, C.mutedFg);
  cardLabel.x = cx;
  cardLabel.y = cy - 20;
  page.appendChild(cardLabel);
  cy += 340;

  // ──────────────────────────────────────────────────────────
  // 2. DIALOG
  // ──────────────────────────────────────────────────────────
  var dialogSet = makeFrame("Dialog", cx, cy, SET_W, 400);
  autoLayout(dialogSet, "HORIZONTAL", 0, 0, 40, "FIXED", "AUTO");
  page.appendChild(dialogSet);

  // Overlay
  var overlay = makeFrame("DialogOverlay", 0, 0, 160, 120);
  setFills(overlay, C.black, 0.40);
  overlay.cornerRadius = 8;
  dialogSet.appendChild(overlay);

  // Content
  var dialogContent = makeFrame("DialogContent", 0, 0, 320, 0);
  autoLayout(dialogContent, "VERTICAL", 0, 0, 0, "FIXED", "AUTO");
  dialogContent.cornerRadius = 22;
  dialogContent.overflow = "HIDDEN";
  setFills(dialogContent, C.white, 0.78);
  setStrokes(dialogContent, C.white, 0.45, 1);
  dialogContent.effects = [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.12 }, offset: { x: 0, y: 12 }, radius: 40, spread: 0, visible: true }];

  var dialogHeader = makeFrame("DialogHeader", 0, 0, 320, 0);
  autoLayout(dialogHeader, "VERTICAL", 24, 24, 8, "FIXED", "AUTO");
  var dialogTitle = makeText("DialogTitle", "Dialog Title", 22, 600, C.foreground);
  var dialogDesc = makeText("DialogDescription", "Dialog description text.", 14, 400, C.mutedFg);
  dialogHeader.appendChild(dialogTitle);
  dialogHeader.appendChild(dialogDesc);
  dialogContent.appendChild(dialogHeader);

  var dialogBody = makeFrame("Content", 0, 0, 320, 60);
  autoLayout(dialogBody, "VERTICAL", 24, 0, 0, "FIXED", "FIXED");
  var dialogBodyText = makeText("Text", "Dialog body content goes here.", 14, 400, C.foreground);
  dialogBody.appendChild(dialogBodyText);
  dialogContent.appendChild(dialogBody);

  var dialogFooter = makeFrame("DialogFooter", 0, 0, 320, 0);
  autoLayout(dialogFooter, "HORIZONTAL", 24, 24, 8, "FIXED", "AUTO");
  dialogFooter.primaryAxisAlignItems = "MAX";
  var dlgBtn1 = makeFrame("Btn/cancel", 0, 0, 0, 32);
  autoLayout(dlgBtn1, "HORIZONTAL", 12, 6, 0, "AUTO", "FIXED");
  setFills(dlgBtn1, C.border);
  dlgBtn1.cornerRadius = 8;
  var dlgBtn1T = makeText("Label", "Cancel", 13, 500, C.foreground);
  dlgBtn1.appendChild(dlgBtn1T);
  dialogFooter.appendChild(dlgBtn1);

  var dlgBtn2 = makeFrame("Btn/confirm", 0, 0, 0, 32);
  autoLayout(dlgBtn2, "HORIZONTAL", 12, 6, 0, "AUTO", "FIXED");
  setFills(dlgBtn2, C.primary);
  dlgBtn2.cornerRadius = 8;
  var dlgBtn2T = makeText("Label", "Confirm", 13, 500, C.darkInk);
  dlgBtn2.appendChild(dlgBtn2T);
  dialogFooter.appendChild(dlgBtn2);
  dialogContent.appendChild(dialogFooter);

  // Close button
  var closeBtn = makeFrame("Close", 0, 0, 28, 28);
  setFills(closeBtn, { r: 0, g: 0, b: 0 }, 0);
  closeBtn.cornerRadius = 6;
  var closeX = makeText("X", "✕", 14, 400, C.mutedFg);
  closeX.x = 7;
  closeX.y = 5;
  closeBtn.appendChild(closeX);
  closeBtn.x = 320 - 44;
  closeBtn.y = 16;
  dialogContent.appendChild(closeBtn);

  dialogSet.appendChild(dialogContent);

  var dialogLabel = makeText("Dialog Label", "Dialog", 14, 600, C.mutedFg);
  dialogLabel.x = cx;
  dialogLabel.y = cy - 20;
  page.appendChild(dialogLabel);
  cy += 440;

  // ──────────────────────────────────────────────────────────
  // 3. SHEET (4 sides)
  // ──────────────────────────────────────────────────────────
  var sheetSet = makeFrame("Sheet", cx, cy, SET_W, 300);
  autoLayout(sheetSet, "HORIZONTAL", 0, 0, 24, "FIXED", "AUTO");
  page.appendChild(sheetSet);

  ["right", "left", "bottom", "top"].forEach(function (side) {
    var isHorizontal = side === "top" || side === "bottom";
    var w = isHorizontal ? 200 : 160;
    var h = isHorizontal ? 140 : 220;

    var sheet = makeFrame("Sheet/" + side, 0, 0, w, h);
    autoLayout(sheet, "VERTICAL", 0, 0, 0, "FIXED", "FIXED");
    setFills(sheet, C.white, 0.65);
    setStrokes(sheet, C.white, 0.40, 1);
    sheet.effects = [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.12 }, offset: { x: 0, y: 12 }, radius: 40, spread: 0, visible: true }];

    if (side === "right") { sheet.cornerRadius = { topLeft: 18, topRight: 0, bottomLeft: 18, bottomRight: 0 }; }
    else if (side === "left") { sheet.cornerRadius = { topLeft: 0, topRight: 18, bottomLeft: 0, bottomRight: 18 }; }
    else if (side === "top") { sheet.cornerRadius = { topLeft: 0, topRight: 0, bottomLeft: 18, bottomRight: 18 }; }
    else { sheet.cornerRadius = { topLeft: 18, topRight: 18, bottomLeft: 0, bottomRight: 0 }; }

    var sheetHeader = makeFrame("SheetHeader", 0, 0, w, 0);
    autoLayout(sheetHeader, "VERTICAL", 24, 24, 4, "FIXED", "AUTO");
    var sheetTitle = makeText("Title", "Sheet Title", 22, 600, C.foreground);
    sheetHeader.appendChild(sheetTitle);
    sheet.appendChild(sheetHeader);

    var sheetBody = makeFrame("Body", 0, 0, w, 0);
    autoLayout(sheetBody, "VERTICAL", 24, 0, 4, "FIXED", "AUTO");
    var sheetBodyT = makeText("Text", "Sheet content area.", 14, 400, C.foreground);
    sheetBody.appendChild(sheetBodyT);
    sheet.appendChild(sheetBody);

    sheetSet.appendChild(sheet);
  });

  var sheetLabel = makeText("Sheet Label", "Sheet (4 sides)", 14, 600, C.mutedFg);
  sheetLabel.x = cx;
  sheetLabel.y = cy - 20;
  page.appendChild(sheetLabel);
  cy += 340;

  // ──────────────────────────────────────────────────────────
  // 4. POPOVER
  // ──────────────────────────────────────────────────────────
  var popSet = makeFrame("Popover", cx, cy, SET_W, 200);
  autoLayout(popSet, "HORIZONTAL", 0, 0, 40, "FIXED", "AUTO");
  page.appendChild(popSet);

  [false, true].forEach(function (hasArrow) {
    var pop = makeFrame("Popover" + (hasArrow ? "/arrow" : ""), 0, 0, 200, 0);
    autoLayout(pop, "VERTICAL", 4, 4, 0, "FIXED", "AUTO");
    pop.cornerRadius = 14;
    setFills(pop, C.white, 0.55);
    setStrokes(pop, C.white, 0.35, 1);
    pop.effects = [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.08 }, offset: { x: 0, y: 4 }, radius: 12, spread: 0, visible: true }];

    ["Menu Item 1", "Menu Item 2", "Menu Item 3"].forEach(function (label, idx) {
      var item = makeFrame("Item" + idx, 0, 0, 192, 32);
      autoLayout(item, "HORIZONTAL", 12, 8, 0, "FIXED", "FIXED");
      item.cornerRadius = 8;
      if (idx === 0) { setFills(item, C.accent); }
      var itemText = makeText("Label", label, 14, 400, idx === 0 ? C.foreground : C.foreground);
      item.appendChild(itemText);
      pop.appendChild(item);
    });

    if (hasArrow) {
      var arrow = makeFrame("Arrow", 0, 0, 8, 8);
      setFills(arrow, C.white, 0.55);
      pop.appendChild(arrow);
    }

    popSet.appendChild(pop);
  });

  var popLabel = makeText("Popover Label", "Popover", 14, 600, C.mutedFg);
  popLabel.x = cx;
  popLabel.y = cy - 20;
  page.appendChild(popLabel);
  cy += 240;

  // ──────────────────────────────────────────────────────────
  // 5. TOOLTIP (inverted solid)
  // ──────────────────────────────────────────────────────────
  var tipSet = makeFrame("Tooltip", cx, cy, SET_W, 100);
  autoLayout(tipSet, "HORIZONTAL", 0, 0, 40, "FIXED", "AUTO");
  page.appendChild(tipSet);

  ["light", "dark"].forEach(function (mode) {
    var isLight = mode === "light";
    var tip = makeFrame("Tooltip/" + mode, 0, 0, 0, 28);
    autoLayout(tip, "HORIZONTAL", 10, 6, 0, "AUTO", "FIXED");
    tip.cornerRadius = 4;
    tip.effects = [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.06 }, offset: { x: 0, y: 1 }, radius: 3, spread: 0, visible: true }];

    if (isLight) {
      setFills(tip, C.darkInk);
      var tipText = makeText("Label", "Tooltip text", 12, 400, C.warmWhite);
    } else {
      setFills(tip, C.warmWhite);
      var tipText = makeText("Label", "Tooltip text", 12, 400, C.darkInk);
    }
    tip.appendChild(tipText);
    tipSet.appendChild(tip);
  });

  var tipLabel = makeText("Tooltip Label", "Tooltip (inverted solid)", 14, 600, C.mutedFg);
  tipLabel.x = cx;
  tipLabel.y = cy - 20;
  page.appendChild(tipLabel);
  cy += 140;

  // ──────────────────────────────────────────────────────────
  // 6. TABS (2/3/4-tab with active indicator)
  // ──────────────────────────────────────────────────────────
  var tabsSet = makeFrame("Tabs", cx, cy, SET_W, 200);
  autoLayout(tabsSet, "HORIZONTAL", 0, 0, 24, "FIXED", "AUTO");
  page.appendChild(tabsSet);

  [2, 3, 4].forEach(function (tabCount) {
    var tabLabels = ["Tab 1", "Tab 2", "Tab 3", "Tab 4"].slice(0, tabCount);
    var tabW = tabCount * 80 + 6;

    tabLabels.forEach(function (_, activeIdx) {
      var tabs = makeFrame("Tabs/" + tabCount + "/active" + activeIdx, 0, 0, tabW, 38);
      autoLayout(tabs, "HORIZONTAL", 3, 3, 2, "FIXED", "FIXED");
      tabs.cornerRadius = 10;
      setFills(tabs, C.white, 0.45);
      setStrokes(tabs, C.white, 0.35, 1);

      tabLabels.forEach(function (label, idx) {
        var isActive = idx === activeIdx;
        var trigger = makeFrame("Trigger/" + idx, 0, 0, 76, 32);
        autoLayout(trigger, "HORIZONTAL", 0, 0, 0, "FIXED", "FIXED");
        trigger.cornerRadius = 4;

        if (isActive) {
          setFills(trigger, C.surfaceBase);
          trigger.effects = [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.06 }, offset: { x: 0, y: 1 }, radius: 3, spread: 0, visible: true }];
        } else {
          setFills(trigger, { r: 0, g: 0, b: 0 }, 0);
        }

        trigger.primaryAxisAlignItems = "CENTER";
        trigger.counterAxisAlignItems = "CENTER";
        var triggerText = makeText("Label", label, 13, 500, isActive ? C.foreground : C.mutedFg);
        trigger.appendChild(triggerText);
        tabs.appendChild(trigger);
      });

      tabsSet.appendChild(tabs);
    });
  });

  var tabsLabel = makeText("Tabs Label", "Tabs (sliding indicator)", 14, 600, C.mutedFg);
  tabsLabel.x = cx;
  tabsLabel.y = cy - 20;
  page.appendChild(tabsLabel);
  cy += 240;

  // ──────────────────────────────────────────────────────────
  // 7. SEPARATOR
  // ──────────────────────────────────────────────────────────
  var sepSet = makeFrame("Separator", cx, cy, SET_W, 80);
  autoLayout(sepSet, "VERTICAL", 0, 0, 12, "FIXED", "AUTO");
  page.appendChild(sepSet);

  ["horizontal", "vertical"].forEach(function (orient) {
    if (orient === "horizontal") {
      var sep = makeFrame("Separator/h", 0, 0, 300, 1);
      setFills(sep, C.border);
      sepSet.appendChild(sep);

      var sepGlass = makeFrame("Separator/h-glass", 0, 0, 300, 1);
      setFills(sepGlass, C.white, 0.10);
      sepSet.appendChild(sepGlass);
    } else {
      var vSepRow = makeFrame("v-sep-row", 0, 0, 300, 40);
      autoLayout(vSepRow, "HORIZONTAL", 0, 0, 40, "FIXED", "FIXED");
      vSepRow.primaryAxisAlignItems = "CENTER";
      vSepRow.counterAxisAlignItems = "CENTER";

      var vSep = makeFrame("Separator/v", 0, 0, 1, 40);
      setFills(vSep, C.border);
      vSepRow.appendChild(vSep);

      var vSepGlass = makeFrame("Separator/v-glass", 0, 0, 1, 40);
      setFills(vSepGlass, C.white, 0.10);
      vSepRow.appendChild(vSepGlass);

      sepSet.appendChild(vSepRow);
    }
  });

  var sepLabel = makeText("Separator Label", "Separator", 14, 600, C.mutedFg);
  sepLabel.x = cx;
  sepLabel.y = cy - 20;
  page.appendChild(sepLabel);

  figma.notify("05 Surface & Overlay components created!");
})();
