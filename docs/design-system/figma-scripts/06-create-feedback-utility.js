// ============================================================
// 06 – Create Feedback & Utility Components
// Avatar, ScrollArea, Skeleton, Progress, AlertBanner, EmptyState
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
    mutedFgHalf:      { r: 0.471, g: 0.384, b: 0.294 },
    primary:          { r: 0.902, g: 0.635, b: 0.235 },
    primaryFg:        { r: 0.169, g: 0.129, b: 0.086 },
    primaryHover:     { r: 0.847, g: 0.580, b: 0.196 },
    border:           { r: 0.863, g: 0.780, b: 0.655 },
    surfaceBase:      { r: 1.000, g: 0.976, b: 0.949 },
    surfaceSunken:    { r: 0.965, g: 0.902, b: 0.792 },
    muted:            { r: 0.941, g: 0.910, b: 0.855 },
    surfaceRaised:    { r: 0.137, g: 0.106, b: 0.078 },
    accent:           { r: 0.965, g: 0.902, b: 0.792 },
    white:            { r: 1.000, g: 1.000, b: 1.000 },
    black:            { r: 0.000, g: 0.000, b: 0.000 },
    statusInfo:       { r: 0.345, g: 0.420, b: 0.478 },
    statusInfoBg:     { r: 0.910, g: 0.929, b: 0.949 },
    statusSuccess:    { r: 0.286, g: 0.427, b: 0.243 },
    statusSuccessBg:  { r: 0.918, g: 0.949, b: 0.902 },
    statusWarning:    { r: 0.541, g: 0.353, b: 0.071 },
    statusWarningBg:  { r: 0.984, g: 0.941, b: 0.851 },
    statusError:      { r: 0.635, g: 0.263, b: 0.169 },
    statusErrorBg:    { r: 0.973, g: 0.902, b: 0.878 },
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

  // ──────────────────────────────────────────────────────────
  // SECTION HEADER
  // ──────────────────────────────────────────────────────────
  var header = makeText("Section: Feedback & Utility", "FEEDBACK & UTILITY", 20, 600, C.foreground);
  header.x = cx;
  header.y = cy;
  page.appendChild(header);
  cy += 50;

  // ──────────────────────────────────────────────────────────
  // 1. AVATAR (sm/default/lg × default/outline/loading)
  // ──────────────────────────────────────────────────────────
  var avatarSet = makeFrame("Avatar", cx, cy, 600, 180);
  autoLayout(avatarSet, "HORIZONTAL", 0, 0, 32, "FIXED", "AUTO");
  page.appendChild(avatarSet);

  var sizes = [
    { name: "sm", dim: 32, fontSize: 12 },
    { name: "default", dim: 40, fontSize: 14 },
    { name: "lg", dim: 56, fontSize: 18 },
  ];

  sizes.forEach(function (size) {
    var col = makeFrame("col-" + size.name, 0, 0, 0, 180);
    autoLayout(col, "VERTICAL", 0, 0, 12, "AUTO", "AUTO");
    col.counterAxisAlignItems = "CENTER";

    var sizeLabel = makeText("SizeLabel", size.name, 11, 400, C.mutedFg);
    col.appendChild(sizeLabel);

    var row = makeFrame("row-" + size.name, 0, 0, 0, 0);
    autoLayout(row, "HORIZONTAL", 0, 0, 12, "AUTO", "AUTO");

    // Default
    var av1 = makeFrame("Avatar/default", 0, 0, size.dim, size.dim);
    setFills(av1, C.primary);
    av1.cornerRadius = 9999;
    av1.primaryAxisAlignItems = "CENTER";
    av1.counterAxisAlignItems = "CENTER";
    var initials1 = makeText("Initials", "AB", size.fontSize, 500, C.primaryFg);
    av1.appendChild(initials1);
    row.appendChild(av1);

    // Outline
    var av2 = makeFrame("Avatar/outline", 0, 0, size.dim, size.dim);
    setFills(av2, C.primary);
    av2.cornerRadius = 9999;
    setStrokes(av2, C.primary, 1, 2);
    av2.primaryAxisAlignItems = "CENTER";
    av2.counterAxisAlignItems = "CENTER";
    var initials2 = makeText("Initials", "AB", size.fontSize, 500, C.primaryFg);
    av2.appendChild(initials2);
    row.appendChild(av2);

    // Loading
    var av3 = makeFrame("Avatar/loading", 0, 0, size.dim, size.dim);
    setFills(av3, C.muted);
    av3.cornerRadius = 9999;
    row.appendChild(av3);

    col.appendChild(row);
    avatarSet.appendChild(col);
  });

  var avatarLabel = makeText("Avatar Label", "Avatar", 14, 600, C.mutedFg);
  avatarLabel.x = cx;
  avatarLabel.y = cy - 20;
  page.appendChild(avatarLabel);
  cy += 220;

  // ──────────────────────────────────────────────────────────
  // 2. SCROLL AREA
  // ──────────────────────────────────────────────────────────
  var scrollSet = makeFrame("ScrollArea", cx, cy, 600, 200);
  autoLayout(scrollSet, "HORIZONTAL", 0, 0, 40, "FIXED", "AUTO");
  page.appendChild(scrollSet);

  ["standard", "glass"].forEach(function (mode) {
    var isGlass = mode === "glass";
    var container = makeFrame("ScrollArea/" + mode, 0, 0, 200, 160);
    container.cornerRadius = 8;
    setFills(container, C.surfaceBase);
    container.overflow = "HIDDEN";

    var content = makeFrame("content", 0, 0, 180, 120);
    autoLayout(content, "VERTICAL", 12, 12, 6, "FIXED", "AUTO");
    for (var i = 0; i < 5; i++) {
      var line = makeText("line" + i, "Content line " + (i + 1), 13, 400, C.foreground);
      content.appendChild(line);
    }
    container.appendChild(content);

    // Scrollbar track
    var scrollbar = makeFrame("Scrollbar", 0, 0, 6, 160);
    setFills(scrollbar, { r: 0, g: 0, b: 0 }, 0);
    scrollbar.x = 194;
    scrollbar.y = 0;

    // Thumb
    var thumb = makeFrame("Thumb", 0, 0, 6, 60);
    thumb.cornerRadius = 9999;
    if (isGlass) {
      setFills(thumb, C.white, 0.20);
    } else {
      setFills(thumb, C.border);
    }
    thumb.y = 10;
    scrollbar.appendChild(thumb);
    container.appendChild(scrollbar);

    scrollSet.appendChild(container);
  });

  var scrollLabel = makeText("ScrollArea Label", "ScrollArea", 14, 600, C.mutedFg);
  scrollLabel.x = cx;
  scrollLabel.y = cy - 20;
  page.appendChild(scrollLabel);
  cy += 240;

  // ──────────────────────────────────────────────────────────
  // 3. SKELETON (text/circle/card)
  // ──────────────────────────────────────────────────────────
  var skelSet = makeFrame("Skeleton", cx, cy, 600, 180);
  autoLayout(skelSet, "HORIZONTAL", 0, 0, 40, "FIXED", "AUTO");
  page.appendChild(skelSet);

  // Text variant
  var skelTextCol = makeFrame("skel-text-col", 0, 0, 200, 0);
  autoLayout(skelTextCol, "VERTICAL", 0, 0, 8, "FIXED", "AUTO");
  var skelTextLabel = makeText("label", "text", 11, 400, C.mutedFg);
  skelTextCol.appendChild(skelTextLabel);
  for (var i = 0; i < 3; i++) {
    var w = i === 2 ? 140 : 200;
    var line = makeFrame("Skeleton/text", 0, 0, w, 16);
    setFills(line, C.muted);
    line.cornerRadius = 6;
    skelTextCol.appendChild(line);
  }
  skelSet.appendChild(skelTextCol);

  // Circle variant
  var skelCircCol = makeFrame("skel-circle-col", 0, 0, 0, 0);
  autoLayout(skelCircCol, "VERTICAL", 0, 0, 8, "AUTO", "AUTO");
  skelCircCol.counterAxisAlignItems = "CENTER";
  var skelCircLabel = makeText("label", "circle", 11, 400, C.mutedFg);
  skelCircCol.appendChild(skelCircLabel);

  [32, 40, 56].forEach(function (dim) {
    var circle = makeFrame("Skeleton/circle", 0, 0, dim, dim);
    setFills(circle, C.muted);
    circle.cornerRadius = 9999;
    skelCircCol.appendChild(circle);
  });
  skelSet.appendChild(skelCircCol);

  // Card variant
  var skelCardCol = makeFrame("skel-card-col", 0, 0, 0, 0);
  autoLayout(skelCardCol, "VERTICAL", 0, 0, 8, "AUTO", "AUTO");
  var skelCardLabel = makeText("label", "card", 11, 400, C.mutedFg);
  skelCardCol.appendChild(skelCardLabel);
  var skelCard = makeFrame("Skeleton/card", 0, 0, 200, 128);
  setFills(skelCard, C.muted);
  skelCard.cornerRadius = 14;
  skelCardCol.appendChild(skelCard);
  skelSet.appendChild(skelCardCol);

  var skelLabel = makeText("Skeleton Label", "Skeleton", 14, 600, C.mutedFg);
  skelLabel.x = cx;
  skelLabel.y = cy - 20;
  page.appendChild(skelLabel);
  cy += 220;

  // ──────────────────────────────────────────────────────────
  // 4. PROGRESS (4 variants × determinate/indeterminate)
  // ──────────────────────────────────────────────────────────
  var progSet = makeFrame("Progress", cx, cy, 600, 220);
  autoLayout(progSet, "VERTICAL", 0, 0, 16, "FIXED", "AUTO");
  page.appendChild(progSet);

  var progVariants = [
    { name: "default", color: C.primary },
    { name: "success", color: C.statusSuccess },
    { name: "warning", color: C.statusWarning },
    { name: "destructive", color: C.statusError },
  ];

  progVariants.forEach(function (v) {
    var row = makeFrame("Progress/" + v.name, 0, 0, 400, 28);
    autoLayout(row, "VERTICAL", 0, 0, 4, "FIXED", "AUTO");

    var label = makeText("label", v.name, 11, 400, C.mutedFg);
    row.appendChild(label);

    // Track
    var track = makeFrame("Track", 0, 0, 400, 8);
    setFills(track, C.border);
    track.cornerRadius = 9999;
    track.overflow = "HIDDEN";

    // Fill (60%)
    var fill = makeFrame("Fill", 0, 0, 240, 8);
    setFills(fill, v.color);
    fill.cornerRadius = 9999;
    track.appendChild(fill);
    row.appendChild(track);

    // Indeterminate track
    var indTrack = makeFrame("Track-ind", 0, 0, 400, 8);
    setFills(indTrack, C.border);
    indTrack.cornerRadius = 9999;
    indTrack.overflow = "HIDDEN";

    var indFill = makeFrame("Fill-ind", 0, 0, 130, 8);
    setFills(indFill, v.color);
    indFill.cornerRadius = 9999;
    indFill.x = 10;
    indTrack.appendChild(indFill);
    row.appendChild(indTrack);

    progSet.appendChild(row);
  });

  var progLabel = makeText("Progress Label", "Progress", 14, 600, C.mutedFg);
  progLabel.x = cx;
  progLabel.y = cy - 20;
  page.appendChild(progLabel);
  cy += 260;

  // ──────────────────────────────────────────────────────────
  // 5. ALERT BANNER (4 variants)
  // ──────────────────────────────────────────────────────────
  var alertSet = makeFrame("AlertBanner", cx, cy, 600, 0);
  autoLayout(alertSet, "VERTICAL", 0, 0, 10, "FIXED", "AUTO");
  page.appendChild(alertSet);

  var alertVariants = [
    { name: "info", color: C.statusInfo, bg: C.statusInfoBg, icon: "ℹ" },
    { name: "success", color: C.statusSuccess, bg: C.statusSuccessBg, icon: "✓" },
    { name: "warning", color: C.statusWarning, bg: C.statusWarningBg, icon: "⚠" },
    { name: "error", color: C.statusError, bg: C.statusErrorBg, icon: "✕" },
  ];

  alertVariants.forEach(function (v) {
    var banner = makeFrame("AlertBanner/" + v.name, 0, 0, 500, 0);
    autoLayout(banner, "HORIZONTAL", 16, 12, 12, "FIXED", "AUTO");
    banner.cornerRadius = 14;
    setFills(banner, v.bg);
    banner.overflow = "HIDDEN";

    // Left stripe
    var stripe = makeFrame("Stripe", 0, 0, 3, 0);
    setFills(stripe, v.color);
    stripe.cornerRadius = 9999;
    stripe.x = 8;
    stripe.y = 8;
    stripe.resize(3, banner.height - 16 > 8 ? 28 : 20);
    banner.appendChild(stripe);

    // Icon
    var iconFrame = makeFrame("Icon", 0, 0, 16, 16);
    var iconText = makeText("Icon", v.icon, 14, 600, v.color);
    iconFrame.appendChild(iconText);
    banner.appendChild(iconFrame);

    // Content
    var content = makeFrame("Content", 0, 0, 0, 0);
    autoLayout(content, "VERTICAL", 0, 0, 2, "AUTO", "AUTO");
    content.flexGrow = 1;
    var alertTitle = makeText("Title", v.name.charAt(0).toUpperCase() + v.name.slice(1) + " alert title", 13, 500, C.foreground);
    var alertMsg = makeText("Message", "Alert description text goes here.", 14, 400, C.mutedFg);
    content.appendChild(alertTitle);
    content.appendChild(alertMsg);
    banner.appendChild(content);

    // Dismiss
    var dismiss = makeFrame("Dismiss", 0, 0, 24, 24);
    setFills(dismiss, { r: 0, g: 0, b: 0 }, 0);
    dismiss.cornerRadius = 4;
    var dismissX = makeText("X", "✕", 12, 400, C.mutedFg);
    dismiss.appendChild(dismissX);
    banner.appendChild(dismiss);

    alertSet.appendChild(banner);
  });

  var alertLabel = makeText("AlertBanner Label", "AlertBanner", 14, 600, C.mutedFg);
  alertLabel.x = cx;
  alertLabel.y = cy - 20;
  page.appendChild(alertLabel);
  cy += 300;

  // ──────────────────────────────────────────────────────────
  // 6. EMPTY STATE
  // ──────────────────────────────────────────────────────────
  var emptySet = makeFrame("EmptyState", cx, cy, 600, 300);
  autoLayout(emptySet, "HORIZONTAL", 0, 0, 40, "FIXED", "AUTO");
  page.appendChild(emptySet);

  [true, false].forEach(function (hasBg) {
    var empty = makeFrame("EmptyState" + (hasBg ? "/bg" : "/no-bg"), 0, 0, 260, 0);
    autoLayout(empty, "VERTICAL", 0, 64, 12, "FIXED", "AUTO");
    empty.counterAxisAlignItems = "CENTER";

    // Icon
    if (hasBg) {
      var iconBg = makeFrame("IconBg", 0, 0, 56, 56);
      setFills(iconBg, C.white, 0.45);
      iconBg.cornerRadius = 9999;
      iconBg.primaryAxisAlignItems = "CENTER";
      iconBg.counterAxisAlignItems = "CENTER";
      var iconInner = makeText("Icon", "💬", 28, 400, C.mutedFg);
      iconBg.appendChild(iconInner);
      empty.appendChild(iconBg);
    } else {
      var iconPlain = makeText("Icon", "💬", 40, 400, C.mutedFg);
      empty.appendChild(iconPlain);
    }

    // Title
    var emptyTitle = makeText("Title", "No conversation selected", 18, 600, C.foreground);
    empty.appendChild(emptyTitle);

    // Description
    var emptyDesc = makeText("Desc", "Create a new chat to get started.", 15, 400, C.mutedFg);
    empty.appendChild(emptyDesc);

    // Action
    var actionBtn = makeFrame("Action", 0, 0, 0, 32);
    autoLayout(actionBtn, "HORIZONTAL", 12, 6, 0, "AUTO", "FIXED");
    setFills(actionBtn, C.primary);
    actionBtn.cornerRadius = 8;
    var actionText = makeText("Label", "New Chat", 13, 500, C.primaryFg);
    actionBtn.appendChild(actionText);
    empty.appendChild(actionBtn);

    emptySet.appendChild(empty);
  });

  var emptyLabel = makeText("EmptyState Label", "EmptyState", 14, 600, C.mutedFg);
  emptyLabel.x = cx;
  emptyLabel.y = cy - 20;
  page.appendChild(emptyLabel);

  figma.notify("06 Feedback & Utility components created!");
})();
