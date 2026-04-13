// ============================================================
// 04 – Create Form Input Components
// Input, Textarea, Checkbox, Select, SegmentedControl, Switch
// ------------------------------------------------------------
// Paste into Figma Console: Plugins → Development → Console
// Safe to re-run: removes existing sets and recreates them.
// Requires page "02 Components" (created by Script 03).
// ============================================================

(function () {
  "use strict";

  var C = {
    primary:       { r: 0.902, g: 0.635, b: 0.235 },
    primaryFg:     { r: 0.169, g: 0.129, b: 0.086 },
    foreground:    { r: 0.169, g: 0.129, b: 0.086 },
    muted:         { r: 0.471, g: 0.384, b: 0.294 },
    border:        { r: 0.863, g: 0.780, b: 0.655 },
    surfaceBase:   { r: 1.000, g: 0.976, b: 0.949 },
    surfaceSunken: { r: 0.965, g: 0.902, b: 0.792 },
    destructive:   { r: 0.753, g: 0.224, b: 0.169 },
    white:         { r: 1.000, g: 1.000, b: 1.000 },
  };

  function solid(color, opacity) {
    var p = { type: "SOLID", color: { r: color.r, g: color.g, b: color.b } };
    if (opacity !== undefined) p.opacity = opacity;
    return p;
  }

  function stroke(color, opacity) {
    return { type: "SOLID", color: { r: color.r, g: color.g, b: color.b }, opacity: opacity !== undefined ? opacity : 1 };
  }

  function setFills(node, color, opacity) { node.fills = [solid(color, opacity)]; }
  function setStrokes(node, color, weight) { node.strokes = [stroke(color)]; node.strokeWeight = weight || 1; }
  function clearStrokes(node) { node.strokes = []; }

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

  function getBottomY(page) {
    var maxY = 100;
    for (var i = 0; i < page.children.length; i++) {
      var child = page.children[i];
      if (child.y + child.height + 80 > maxY) maxY = child.y + child.height + 80;
    }
    return maxY;
  }

  function removeIfExists(page, name) {
    var existing = page.children.filter(function (c) { return c.name === name; });
    for (var i = 0; i < existing.length; i++) existing[i].remove();
  }

  function loadFont() {
    return figma.loadFontAsync({ family: "Inter", style: "Regular" })
      .catch(function () {
        return figma.loadFontAsync({ family: "Inter", style: "Medium" });
      })
      .catch(function () {
        return figma.listAvailableFontsAsync().then(function (fonts) {
          if (fonts.length > 0) return figma.loadFontAsync(fonts[0].fontName);
        });
      });
  }

  function createLabel(page, text, x, y) {
    var label = figma.createText();
    label.characters = text;
    label.fontSize = 18;
    label.fills = [solid(C.foreground)];
    label.fontName = { family: "Inter", style: "Regular" };
    label.x = x;
    label.y = y - 30;
    page.appendChild(label);
    return label;
  }

  // ── Main ──

  var page = findPage("02 Components");
  if (!page) {
    page = figma.createPage();
    page.name = "02 Components";
  }
  figma.currentPage = page;

  var startX = 100;
  var startY = getBottomY(page);

  removeIfExists(page, "Input");
  removeIfExists(page, "Textarea");
  removeIfExists(page, "Checkbox");
  removeIfExists(page, "Select");
  removeIfExists(page, "SegmentedControl");
  removeIfExists(page, "Switch");

  loadFont().then(function () {

    // ═══════════════════════════════════════════════════════════
    //  INPUT
    // ═══════════════════════════════════════════════════════════

    var inputSet = figma.createComponentSet();
    inputSet.name = "Input";
    inputSet.x = startX;
    inputSet.y = startY;
    page.appendChild(inputSet);

    var states = ["default", "focus", "disabled", "error"];
    var sizes = [
      { name: "sm", h: 32, fs: 14, px: 12 },
      { name: "default", h: 38, fs: 15, px: 12 },
      { name: "lg", h: 44, fs: 15, px: 12 }
    ];

    var col = 0;
    for (var si = 0; si < sizes.length; si++) {
      for (var sti = 0; sti < states.length; sti++) {
        var s = sizes[si];
        var st = states[sti];
        var comp = figma.createComponent();
        comp.name = "state=" + st + ", size=" + s.name;
        comp.layoutMode = "HORIZONTAL";
        comp.itemSpacing = 8;
        comp.paddingLeft = s.px;
        comp.paddingRight = s.px;
        comp.paddingTop = 0;
        comp.paddingBottom = 0;
        comp.cornerRadius = 10;
        comp.counterAxisSizingMode = "FIXED";
        comp.resize(200, s.h);
        comp.x = col * 220;

        if (st === "disabled") {
          comp.opacity = 0.5;
          setFills(comp, C.surfaceBase);
          setStrokes(comp, C.border, 1);
        } else if (st === "focus") {
          setFills(comp, C.surfaceBase);
          setStrokes(comp, C.primary, 2);
          comp.effects = [{ type: "DROP_SHADOW", color: { r: 0.902, g: 0.635, b: 0.235, a: 0.2 }, offset: { x: 0, y: 0 }, radius: 3, spread: 0, visible: true }];
        } else if (st === "error") {
          setFills(comp, C.surfaceBase);
          setStrokes(comp, C.destructive, 1);
        } else {
          setFills(comp, C.white, 0);
          setStrokes(comp, C.border, 1);
        }

        var txt = figma.createText();
        txt.characters = "Placeholder";
        txt.fontSize = s.fs;
        txt.fills = [solid(C.muted)];
        comp.appendChild(txt);
        inputSet.appendChild(comp);
        col++;
      }
    }
    createLabel(page, "Input", startX, startY);

    // ═══════════════════════════════════════════════════════════
    //  TEXTAREA
    // ═══════════════════════════════════════════════════════════

    var ta = figma.createComponent();
    ta.name = "Textarea";
    ta.layoutMode = "VERTICAL";
    ta.itemSpacing = 0;
    ta.paddingLeft = 12;
    ta.paddingRight = 12;
    ta.paddingTop = 12;
    ta.paddingBottom = 12;
    ta.cornerRadius = 10;
    ta.resize(280, 80);
    ta.x = startX;
    ta.y = startY + inputSet.height + 80;
    setFills(ta, C.white, 0);
    setStrokes(ta, C.border, 1);
    page.appendChild(ta);

    var taTxt = figma.createText();
    taTxt.characters = "Enter text here...";
    taTxt.fontSize = 15;
    taTxt.fills = [solid(C.muted)];
    ta.appendChild(taTxt);
    createLabel(page, "Textarea", startX, ta.y);

    var nextY = ta.y + ta.height + 120;

    // ═══════════════════════════════════════════════════════════
    //  CHECKBOX
    // ═══════════════════════════════════════════════════════════

    var cbSet = figma.createComponentSet();
    cbSet.name = "Checkbox";
    cbSet.x = startX;
    cbSet.y = nextY;
    page.appendChild(cbSet);

    var cbStates = ["unchecked", "checked", "indeterminate", "disabled"];
    for (var ci = 0; ci < cbStates.length; ci++) {
      var cst = cbStates[ci];
      var cb = figma.createComponent();
      cb.name = "state=" + cst;
      cb.counterAxisSizingMode = "FIXED";
      cb.resize(18, 18);
      cb.cornerRadius = 4;
      cb.x = ci * 40;

      if (cst === "unchecked") {
        setFills(cb, C.white, 0);
        setStrokes(cb, C.border, 1.5);
      } else if (cst === "checked") {
        setFills(cb, C.primary);
        clearStrokes(cb);
        var check1 = figma.createRectangle();
        check1.resizeWithoutConstraints(8, 2);
        check1.cornerRadius = 1;
        check1.fills = [solid(C.white)];
        check1.rotation = 45;
        check1.x = 3;
        check1.y = 9;
        cb.appendChild(check1);
        var check2 = figma.createRectangle();
        check2.resizeWithoutConstraints(12, 2);
        check2.cornerRadius = 1;
        check2.fills = [solid(C.white)];
        check2.rotation = -45;
        check2.x = 6;
        check2.y = 7;
        cb.appendChild(check2);
      } else if (cst === "indeterminate") {
        setFills(cb, C.primary);
        clearStrokes(cb);
        var line = figma.createRectangle();
        line.resizeWithoutConstraints(8, 2);
        line.cornerRadius = 1;
        line.fills = [solid(C.white)];
        line.x = 5;
        line.y = 8;
        cb.appendChild(line);
      } else {
        cb.opacity = 0.5;
        setFills(cb, C.white, 0);
        setStrokes(cb, C.border, 1.5);
      }
      cbSet.appendChild(cb);
    }
    createLabel(page, "Checkbox", startX, nextY);

    // ═══════════════════════════════════════════════════════════
    //  SELECT
    // ═══════════════════════════════════════════════════════════

    var selSet = figma.createComponentSet();
    selSet.name = "Select";
    selSet.x = startX + 400;
    selSet.y = startY;
    page.appendChild(selSet);

    var selStates = ["default", "open", "disabled"];
    for (var sli = 0; sli < selStates.length; sli++) {
      var sst = selStates[sli];
      var selComp = figma.createComponent();
      selComp.name = "state=" + sst;
      selComp.layoutMode = "HORIZONTAL";
      selComp.itemSpacing = 8;
      selComp.paddingLeft = 12;
      selComp.paddingRight = 12;
      selComp.paddingTop = 0;
      selComp.paddingBottom = 0;
      selComp.cornerRadius = 10;
      selComp.counterAxisSizingMode = "FIXED";
      selComp.resize(200, 38);
      selComp.x = sli * 220;

      if (sst === "disabled") {
        selComp.opacity = 0.5;
        setFills(selComp, C.surfaceBase);
        setStrokes(selComp, C.border, 1);
      } else {
        setFills(selComp, C.surfaceBase);
        setStrokes(selComp, C.border, 1);
      }

      var selTxt = figma.createText();
      selTxt.characters = "Select option...";
      selTxt.fontSize = 15;
      selTxt.fills = [solid(C.muted)];
      selTxt.layoutGrow = 1;
      selComp.appendChild(selTxt);

      var chevron = figma.createRectangle();
      chevron.resizeWithoutConstraints(6, 6);
      chevron.cornerRadius = 0;
      chevron.fills = [];
      chevron.strokes = [stroke(C.muted)];
      chevron.strokeWeight = 1.5;
      chevron.rotation = 45;
      chevron.x = 0;
      chevron.y = 0;
      selComp.appendChild(chevron);

      selSet.appendChild(selComp);

      if (sst === "open") {
        var dropdown = figma.createFrame();
        dropdown.name = "Dropdown";
        dropdown.layoutMode = "VERTICAL";
        dropdown.itemSpacing = 0;
        dropdown.paddingLeft = 0;
        dropdown.paddingRight = 0;
        dropdown.paddingTop = 4;
        dropdown.paddingBottom = 4;
        dropdown.cornerRadius = 14;
        dropdown.resize(200, 100);
        dropdown.x = 0;
        dropdown.y = 46;
        setFills(dropdown, C.surfaceBase);
        dropdown.effects = [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.08 }, offset: { x: 0, y: 4 }, radius: 12, spread: 0, visible: true }];

        var options = ["Option 1", "Option 2", "Option 3"];
        for (var oi = 0; oi < options.length; oi++) {
          var optFrame = figma.createFrame();
          optFrame.layoutMode = "HORIZONTAL";
          optFrame.paddingLeft = 12;
          optFrame.paddingRight = 12;
          optFrame.paddingTop = 8;
          optFrame.paddingBottom = 8;
          optFrame.resize(200, 32);
          if (oi === 0) {
            setFills(optFrame, C.surfaceSunken);
          } else {
            optFrame.fills = [];
          }
          var optTxt = figma.createText();
          optTxt.characters = options[oi];
          optTxt.fontSize = 14;
          optTxt.fills = [solid(C.foreground)];
          optFrame.appendChild(optTxt);
          dropdown.appendChild(optFrame);
        }
        selComp.appendChild(dropdown);
      }
    }
    createLabel(page, "Select", startX + 400, startY);

    // ═══════════════════════════════════════════════════════════
    //  SEGMENTED CONTROL
    // ═══════════════════════════════════════════════════════════

    var segSet = figma.createComponentSet();
    segSet.name = "SegmentedControl";
    segSet.x = startX + 400;
    segSet.y = nextY;
    page.appendChild(segSet);

    var segLabels = ["Light", "Dark", "System"];
    for (var ai = 0; ai < 3; ai++) {
      var segComp = figma.createComponent();
      segComp.name = "active=" + segLabels[ai].toLowerCase();
      segComp.layoutMode = "HORIZONTAL";
      segComp.itemSpacing = 0;
      segComp.paddingLeft = 3;
      segComp.paddingRight = 3;
      segComp.paddingTop = 3;
      segComp.paddingBottom = 3;
      segComp.cornerRadius = 10;
      segComp.counterAxisSizingMode = "FIXED";
      segComp.resize(300, 38);
      setFills(segComp, C.surfaceSunken);
      segComp.x = ai * 320;

      for (var sj = 0; sj < 3; sj++) {
        var seg = figma.createFrame();
        seg.layoutMode = "HORIZONTAL";
        seg.paddingLeft = 12;
        seg.paddingRight = 12;
        seg.paddingTop = 6;
        seg.paddingBottom = 6;
        seg.cornerRadius = 8;
        seg.counterAxisSizingMode = "FIXED";
        seg.resize(96, 32);
        seg.layoutSizingHorizontal = "FILL";

        if (sj === ai) {
          setFills(seg, C.surfaceBase);
          seg.effects = [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.06 }, offset: { x: 0, y: 1 }, radius: 3, spread: 0, visible: true }];
        } else {
          seg.fills = [];
          seg.effects = [];
        }

        var segTxt = figma.createText();
        segTxt.characters = segLabels[sj];
        segTxt.fontSize = 13;
        segTxt.fills = [solid(sj === ai ? C.foreground : C.muted)];
        seg.appendChild(segTxt);
        segComp.appendChild(seg);
      }
      segSet.appendChild(segComp);
    }
    createLabel(page, "SegmentedControl", startX + 400, nextY);

    // ═══════════════════════════════════════════════════════════
    //  SWITCH
    // ═══════════════════════════════════════════════════════════

    var swSet = figma.createComponentSet();
    swSet.name = "Switch";
    swSet.x = startX + 800;
    swSet.y = startY;
    page.appendChild(swSet);

    var swStates = ["off", "on", "disabled"];
    for (var wi = 0; wi < swStates.length; wi++) {
      var wst = swStates[wi];
      var swComp = figma.createComponent();
      swComp.name = "state=" + wst;
      swComp.counterAxisSizingMode = "FIXED";
      swComp.resize(44, 24);
      swComp.cornerRadius = 12;
      swComp.x = wi * 60;

      if (wst === "off") {
        setFills(swComp, C.white, 0);
        setStrokes(swComp, C.border, 1);
      } else if (wst === "on") {
        setFills(swComp, C.primary);
        clearStrokes(swComp);
      } else {
        swComp.opacity = 0.5;
        setFills(swComp, C.white, 0);
        setStrokes(swComp, C.border, 1);
      }

      var thumb = figma.createEllipse();
      thumb.resizeWithoutConstraints(18, 18);
      thumb.cornerRadius = 9;
      thumb.fills = [solid(C.white)];
      thumb.effects = [{ type: "DROP_SHADOW", color: { r: 0, g: 0, b: 0, a: 0.1 }, offset: { x: 0, y: 1 }, radius: 3, spread: 0, visible: true }];
      if (wst === "on") {
        thumb.x = 23;
      } else {
        thumb.x = 3;
      }
      thumb.y = 3;
      swComp.appendChild(thumb);
      swSet.appendChild(swComp);
    }
    createLabel(page, "Switch", startX + 800, startY);

    figma.viewport.scrollAndZoomIntoView([inputSet, cbSet, segSet, swSet]);
    figma.closePlugin();
  });
})();
