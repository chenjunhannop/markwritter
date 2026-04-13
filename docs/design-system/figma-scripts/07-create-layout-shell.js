// ============================================================
// 07 – Create Layout Shell Frames
// BackgroundMesh, Sidebar (expanded/collapsed), Header, MobileDrawer
// 8 Frames: Desktop×2 states×2 themes + Mobile×2 states×2 themes
// ------------------------------------------------------------
// Paste into Figma Console: Plugins → Development → Console
// Safe to re-run: removes existing page and recreates.
// ============================================================

(function () {
  "use strict";

  var C = {
    foreground:       { r: 0.169, g: 0.129, b: 0.086 },
    foregroundDark:   { r: 0.973, g: 0.945, b: 0.906 },
    mutedFg:          { r: 0.471, g: 0.384, b: 0.294 },
    mutedFgDark:      { r: 0.780, g: 0.714, b: 0.624 },
    primary:          { r: 0.902, g: 0.635, b: 0.235 },
    primaryDark:      { r: 0.941, g: 0.690, b: 0.290 },
    border:           { r: 0.863, g: 0.780, b: 0.655 },
    surfaceBase:      { r: 1.000, g: 0.976, b: 0.949 },
    surfaceBaseDark:  { r: 0.102, g: 0.078, b: 0.059 },
    accent:           { r: 0.965, g: 0.902, b: 0.792 },
    accentDark:       { r: 0.192, g: 0.149, b: 0.110 },
    white:            { r: 1.000, g: 1.000, b: 1.000 },
    black:            { r: 0.000, g: 0.000, b: 0.000 },
    meshGold1:        { r: 0.961, g: 0.867, b: 0.690 },
    meshGold2:        { r: 0.922, g: 0.800, b: 0.565 },
    meshPeach:        { r: 0.957, g: 0.882, b: 0.761 },
    meshDarkEmber1:   { r: 0.180, g: 0.110, b: 0.051 },
    meshDarkEmber2:   { r: 0.137, g: 0.082, b: 0.039 },
    meshDarkGlow:     { r: 0.220, g: 0.149, b: 0.078 },
  };

  function solid(color, opacity) {
    var p = { type: "SOLID", color: { r: color.r, g: color.g, b: color.b } };
    if (opacity !== undefined) p.opacity = opacity;
    return p;
  }

  function gradFill(colors, positions) {
    var g = { type: "GRADIENT_LINEAR", gradientStops: [] };
    g.gradientHandlePositions = [
      { x: 0, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 0 }
    ];
    for (var i = 0; i < colors.length; i++) {
      g.gradientStops.push({ color: { r: colors[i].r, g: colors[i].g, b: colors[i].b }, position: positions[i] });
    }
    return g;
  }

  function radialFill(color, cx, cy, r) {
    var g = {
      type: "GRADIENT_RADIAL",
      gradientStops: [
        { color: { r: color.r, g: color.g, b: color.b }, position: 0 },
        { color: { r: color.r, g: color.g, b: color.b }, position: 1 }
      ],
      gradientHandlePositions: [
        { x: cx, y: cy }, { x: cx, y: cy + r }, { x: cx + r, y: cy }
      ]
    };
    g.gradientStops[0].color = Object.assign({}, color);
    g.gradientStops[1] = { color: { r: 0, g: 0, b: 0 }, position: 1 };
    return g;
  }

  function setFills(node, color, opacity) { node.fills = [solid(color, opacity)]; }
  function setStrokes(node, color, opacity, weight) {
    node.strokes = [solid(color, opacity)];
    node.strokeWeight = weight || 1;
  }

  function makeFrame(name, w, h) {
    var f = figma.createFrame();
    f.name = name;
    f.resize(w, h);
    return f;
  }

  function makeText(chars, fontSize, fontWeight, color) {
    var t = figma.createText();
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

  var navItems = [
    { icon: "💬", label: "Chat" },
    { icon: "📦", label: "Skills" },
    { icon: "🌿", label: "Explore" },
    { icon: "🔍", label: "Query" },
    { icon: "📝", label: "Record" },
    { icon: "📜", label: "Logs" },
    { icon: "⚙️", label: "Settings" },
  ];

  var existingPage = figma.root.children.find(function (p) { return p.name === "03 Layout Shell"; });
  if (existingPage) { existingPage.remove(); }
  var page = figma.createPage();
  page.name = "03 Layout Shell";

  var cx = 0;
  var cy = 0;

  function buildLayout(frameName, w, h, isDark, isMobile, drawerOpen, isCollapsed) {
    var frame = makeFrame(frameName, w, h);
    frame.x = cx;
    frame.y = cy;
    page.appendChild(frame);

    var fg = isDark ? C.foregroundDark : C.foreground;
    var mfg = isDark ? C.mutedFgDark : C.mutedFg;
    var sBase = isDark ? C.surfaceBaseDark : C.surfaceBase;
    var acc = isDark ? C.accentDark : C.accent;
    var prim = isDark ? C.primaryDark : C.primary;
    var bgOp = isDark ? 0.70 : 0.65;
    var headerOp = isDark ? 0.80 : 0.78;
    var borderOp = isDark ? 0.12 : 0.40;
    var headerBorderOp = isDark ? 0.15 : 0.45;
    var sepOp = isDark ? 0.06 : 0.10;

    // Background mesh
    if (isDark) {
      setFills(frame, C.meshDarkEmber1);
    } else {
      setFills(frame, C.meshPeach);
    }

    // Mesh overlay blobs (decorative ellipses)
    var blob1 = makeFrame("blob1", w * 0.4, h * 0.5);
    setFills(blob1, isDark ? C.meshDarkGlow : C.meshGold1, 0.30);
    blob1.cornerRadius = 9999;
    blob1.x = w * 0.05;
    blob1.y = h * 0.05;
    frame.appendChild(blob1);

    var blob2 = makeFrame("blob2", w * 0.35, h * 0.4);
    setFills(blob2, isDark ? C.meshDarkEmber2 : C.meshGold2, 0.25);
    blob2.cornerRadius = 9999;
    blob2.x = w * 0.6;
    blob2.y = h * 0.1;
    frame.appendChild(blob2);

    var blob3 = makeFrame("blob3", w * 0.45, h * 0.55);
    setFills(blob3, isDark ? C.meshDarkEmber1 : C.meshPeach, 0.20);
    blob3.cornerRadius = 9999;
    blob3.x = w * 0.4;
    blob3.y = h * 0.5;
    frame.appendChild(blob3);

    var contentLayer = makeFrame("Content", w, h);
    autoLayout(contentLayer, "HORIZONTAL", 0, 0, 0, "FIXED", "FIXED");

    var sidebarW = 0;
    var showSidebar = !isMobile;

    if (showSidebar) {
      sidebarW = isCollapsed ? 56 : 256;

      // Sidebar
      var sidebar = makeFrame("Sidebar", sidebarW, h);
      autoLayout(sidebar, "VERTICAL", 0, 0, 0, "FIXED", "FIXED");
      setFills(sidebar, C.white, bgOp);
      setStrokes(sidebar, C.white, borderOp, 1);
      sidebar.strokeAlign = "INSIDE";
      sidebar.strokeLeft = 0;
      sidebar.strokeTop = 0;
      sidebar.strokeBottom = 0;

      // Brand row
      var brandRow = makeFrame("BrandRow", sidebarW, 56);
      autoLayout(brandRow, "HORIZONTAL", 16, 0, 8, "FIXED", "FIXED");
      brandRow.primaryAxisAlignItems = "CENTER";
      brandRow.counterAxisAlignItems = "CENTER";
      var brandIcon = makeText("✏️", 20, 400, prim);
      brandRow.appendChild(brandIcon);
      if (!isCollapsed) {
        var brandText = makeText("Markwritter", 18, 600, fg);
        brandRow.appendChild(brandText);
      }
      sidebar.appendChild(brandRow);

      // Separator 1
      var sep1 = makeFrame("Sep1", sidebarW, 1);
      setFills(sep1, C.white, sepOp);
      sidebar.appendChild(sep1);

      // Nav items
      var navList = makeFrame("NavList", sidebarW - 16, 0);
      autoLayout(navList, "VERTICAL", 0, 8, 4, "FIXED", "AUTO");

      navItems.forEach(function (item, idx) {
        var navItem = makeFrame("Nav/" + item.label, isCollapsed ? 40 : 240, 40);
        autoLayout(navItem, "HORIZONTAL", isCollapsed ? 0 : 12, 0, 12, isCollapsed ? "FIXED" : "FIXED", "FIXED");
        navItem.primaryAxisAlignItems = "CENTER";
        navItem.counterAxisAlignItems = "CENTER";
        navItem.cornerRadius = 10;

        if (idx === 0) {
          setFills(navItem, acc);
        } else {
          setFills(navItem, { r: 0, g: 0, b: 0 }, 0);
        }

        // Active stripe for first item
        if (idx === 0) {
          var stripe = makeFrame("Stripe", 3, 24);
          setFills(stripe, prim);
          stripe.cornerRadius = 9999;
          stripe.x = 0;
          stripe.y = 8;
          navItem.appendChild(stripe);
        }

        var icon = makeText("icon", item.icon, 16, 400, idx === 0 ? fg : mfg);
        navItem.appendChild(icon);
        if (!isCollapsed) {
          var label = makeText("label", item.label, 14, 500, idx === 0 ? fg : mfg);
          navItem.appendChild(label);
        }
        navList.appendChild(navItem);
      });

      var navScroll = makeFrame("NavScroll", sidebarW, 0);
      autoLayout(navScroll, "VERTICAL", 8, 8, 0, "FIXED", "AUTO");
      navScroll.flexGrow = 1;
      navScroll.appendChild(navList);
      sidebar.appendChild(navScroll);

      // Separator 2
      var sep2 = makeFrame("Sep2", sidebarW, 1);
      setFills(sep2, C.white, sepOp);
      sidebar.appendChild(sep2);

      // Collapse toggle
      var footer = makeFrame("Footer", sidebarW, 44);
      autoLayout(footer, "HORIZONTAL", 0, 0, 0, "FIXED", "FIXED");
      footer.primaryAxisAlignItems = "CENTER";
      footer.counterAxisAlignItems = "CENTER";
      var toggleBtn = makeFrame("Toggle", 28, 28);
      autoLayout(toggleBtn, "HORIZONTAL", 0, 0, 0, "FIXED", "FIXED");
      toggleBtn.primaryAxisAlignItems = "CENTER";
      toggleBtn.counterAxisAlignItems = "CENTER";
      toggleBtn.cornerRadius = 6;
      var toggleIcon = makeText("icon", isCollapsed ? "►" : "◄", 12, 400, mfg);
      toggleBtn.appendChild(toggleIcon);
      footer.appendChild(toggleBtn);
      sidebar.appendChild(footer);

      contentLayer.appendChild(sidebar);
    }

    // Main column
    var mainW = w - sidebarW;
    var mainCol = makeFrame("MainCol", mainW, h);
    autoLayout(mainCol, "VERTICAL", 0, 0, 0, "FIXED", "FIXED");

    // Header
    var header = makeFrame("Header", mainW, 56);
    autoLayout(header, "HORIZONTAL", isMobile ? 16 : 24, 0, 0, "FIXED", "FIXED");
    header.primaryAxisAlignItems = "CENTER";
    setFills(header, C.white, headerOp);
    header.strokeBottom = 1;
    setStrokes(header, C.white, headerBorderOp, 1);
    header.strokeAlign = "INSIDE";
    header.strokeTop = 0;
    header.strokeLeft = 0;
    header.strokeRight = 0;

    var leftGroup = makeFrame("Left", 0, 40);
    autoLayout(leftGroup, "HORIZONTAL", 0, 0, 12, "AUTO", "FIXED");
    leftGroup.primaryAxisAlignItems = "CENTER";
    leftGroup.counterAxisAlignItems = "CENTER";

    if (isMobile) {
      var hamburger = makeFrame("Hamburger", 28, 28);
      autoLayout(hamburger, "HORIZONTAL", 0, 0, 0, "FIXED", "FIXED");
      hamburger.primaryAxisAlignItems = "CENTER";
      hamburger.counterAxisAlignItems = "CENTER";
      hamburger.cornerRadius = 6;
      var hamburgerIcon = makeText("icon", "☰", 14, 400, fg);
      hamburger.appendChild(hamburgerIcon);
      leftGroup.appendChild(hamburger);
    }

    var pageTitle = makeText("Chat", 18, 600, fg);
    leftGroup.appendChild(pageTitle);
    header.appendChild(leftGroup);

    // Right group
    var rightGroup = makeFrame("Right", 0, 40);
    autoLayout(rightGroup, "HORIZONTAL", 0, 0, 8, "AUTO", "FIXED");
    rightGroup.primaryAxisAlignItems = "CENTER";
    rightGroup.counterAxisAlignItems = "CENTER";

    var themeBtn = makeFrame("ThemeToggle", 28, 28);
    autoLayout(themeBtn, "HORIZONTAL", 0, 0, 0, "FIXED", "FIXED");
    themeBtn.primaryAxisAlignItems = "CENTER";
    themeBtn.counterAxisAlignItems = "CENTER";
    themeBtn.cornerRadius = 6;
    var themeIcon = makeText("icon", isDark ? "🌙" : "☀️", 14, 400, fg);
    themeBtn.appendChild(themeIcon);
    rightGroup.appendChild(themeBtn);

    if (!isMobile) {
      var sidebarBtn = makeFrame("SidebarToggle", 28, 28);
      autoLayout(sidebarBtn, "HORIZONTAL", 0, 0, 0, "FIXED", "FIXED");
      sidebarBtn.primaryAxisAlignItems = "CENTER";
      sidebarBtn.counterAxisAlignItems = "CENTER";
      sidebarBtn.cornerRadius = 6;
      var sidebarIcon = makeText("icon", "☰", 14, 400, fg);
      sidebarBtn.appendChild(sidebarIcon);
      rightGroup.appendChild(sidebarBtn);
    }

    rightGroup.x = mainW - (isMobile ? 50 : 80);
    header.appendChild(rightGroup);
    mainCol.appendChild(header);

    // Content area
    var contentArea = makeFrame("ContentArea", mainW, h - 56);
    autoLayout(contentArea, "VERTICAL", 0, 64, 0, "FIXED", "FIXED");
    contentArea.primaryAxisAlignItems = "CENTER";
    contentArea.counterAxisAlignItems = "CENTER";
    var contentPlaceholder = makeText("text", "Main content area", 16, 400, mfg);
    contentArea.appendChild(contentPlaceholder);
    mainCol.appendChild(contentArea);

    contentLayer.appendChild(mainCol);

    // Mobile drawer overlay
    if (isMobile && drawerOpen) {
      var overlay = makeFrame("Overlay", w, h);
      setFills(overlay, C.black, 0.40);
      frame.appendChild(overlay);
      contentLayer.opacity = 0.95;

      var drawer = makeFrame("Drawer", 256, h);
      autoLayout(drawer, "VERTICAL", 0, 0, 0, "FIXED", "FIXED");
      setFills(drawer, C.white, bgOp);
      setStrokes(drawer, C.white, borderOp, 1);
      drawer.strokeAlign = "INSIDE";
      drawer.strokeTop = 0;
      drawer.strokeBottom = 0;
      drawer.strokeLeft = 0;
      drawer.cornerRadius = { topLeft: 0, topRight: 18, bottomLeft: 0, bottomRight: 18 };

      // Drawer brand
      var dBrand = makeFrame("BrandRow", 256, 56);
      autoLayout(dBrand, "HORIZONTAL", 16, 0, 8, "FIXED", "FIXED");
      dBrand.primaryAxisAlignItems = "CENTER";
      dBrand.counterAxisAlignItems = "CENTER";
      var dIcon = makeText("✏️", 20, 400, prim);
      var dText = makeText("Markwritter", 18, 600, fg);
      dBrand.appendChild(dIcon);
      dBrand.appendChild(dText);

      var dClose = makeFrame("Close", 28, 28);
      autoLayout(dClose, "HORIZONTAL", 0, 0, 0, "FIXED", "FIXED");
      dClose.primaryAxisAlignItems = "CENTER";
      dClose.counterAxisAlignItems = "CENTER";
      dClose.cornerRadius = 6;
      dClose.x = 256 - 48;
      dClose.y = 14;
      var dCloseIcon = makeText("✕", 14, 400, mfg);
      dClose.appendChild(dCloseIcon);
      dBrand.appendChild(dClose);
      drawer.appendChild(dBrand);

      var dSep1 = makeFrame("Sep1", 256, 1);
      setFills(dSep1, C.white, sepOp);
      drawer.appendChild(dSep1);

      var dNav = makeFrame("NavList", 240, 0);
      autoLayout(dNav, "VERTICAL", 0, 8, 4, "FIXED", "AUTO");
      navItems.forEach(function (item, idx) {
        var navItem = makeFrame("Nav/" + item.label, 240, 40);
        autoLayout(navItem, "HORIZONTAL", 12, 0, 12, "FIXED", "FIXED");
        navItem.primaryAxisAlignItems = "CENTER";
        navItem.counterAxisAlignItems = "CENTER";
        navItem.cornerRadius = 10;
        setFills(navItem, idx === 0 ? acc : { r: 0, g: 0, b: 0 }, idx === 0 ? 1 : 0);
        var icon = makeText("icon", item.icon, 16, 400, idx === 0 ? fg : mfg);
        var label = makeText("label", item.label, 14, 500, idx === 0 ? fg : mfg);
        navItem.appendChild(icon);
        navItem.appendChild(label);
        dNav.appendChild(navItem);
      });

      var dNavScroll = makeFrame("NavScroll", 256, 0);
      autoLayout(dNavScroll, "VERTICAL", 8, 8, 0, "FIXED", "AUTO");
      dNavScroll.flexGrow = 1;
      dNavScroll.appendChild(dNav);
      drawer.appendChild(dNavScroll);

      drawer.x = 0;
      drawer.y = 0;
      frame.appendChild(drawer);
    }

    frame.appendChild(contentLayer);
    return frame;
  }

  var GAP = 80;

  // Desktop layouts
  buildLayout("Desktop / Expanded / Light", 1440, 900, false, false, false, false);
  cx += 1440 + GAP;

  buildLayout("Desktop / Collapsed / Light", 1440, 900, false, false, false, true);
  cx += 1440 + GAP;

  buildLayout("Desktop / Expanded / Dark", 1440, 900, true, false, false, false);
  cx += 1440 + GAP;

  buildLayout("Desktop / Collapsed / Dark", 1440, 900, true, false, false, true);
  cx = 0;
  cy += 900 + GAP;

  // Mobile layouts
  buildLayout("Mobile / Closed / Light", 390, 844, false, true, false, false);
  cx += 390 + GAP;

  buildLayout("Mobile / Open / Light", 390, 844, false, true, true, false);
  cx += 390 + GAP;

  buildLayout("Mobile / Closed / Dark", 390, 844, true, true, false, false);
  cx += 390 + GAP;

  buildLayout("Mobile / Open / Dark", 390, 844, true, true, true, false);

  figma.currentPage = page;
  figma.notify("07 Layout Shell frames created! (8 frames: 4 desktop + 4 mobile)");
})();
