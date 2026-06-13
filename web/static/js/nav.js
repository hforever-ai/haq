// Aarambha Haq — nav interactions
(function() {
  "use strict";

  // ── Mobile drawer ──────────────────────────────────────────────
  const hamburger   = document.getElementById("hamburger");
  const drawer      = document.getElementById("navDrawer");
  const overlay     = document.getElementById("drawerOverlay");
  const drawerClose = document.getElementById("drawerClose");

  function openDrawer() {
    drawer.classList.add("open");
    hamburger.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
    // Move focus to first focusable element in drawer
    const first = drawer.querySelector("a, button");
    if (first) first.focus();
  }
  function closeDrawer() {
    drawer.classList.remove("open");
    hamburger.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
    hamburger.focus();
  }

  if (hamburger) hamburger.addEventListener("click", openDrawer);
  if (overlay)   overlay.addEventListener("click", closeDrawer);
  if (drawerClose) drawerClose.addEventListener("click", closeDrawer);

  // ESC closes drawer and any open dropdowns
  document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
      closeDrawer();
      closeLangDropdown();
      closeMegaDrop();
    }
  });

  // ── Language picker ─────────────────────────────────────────────
  const langBtn      = document.getElementById("langBtn");
  const langDropdown = document.getElementById("langDropdown");
  const langPicker   = document.getElementById("langPicker");

  function openLangDropdown() {
    langDropdown.classList.add("open");
    langBtn.setAttribute("aria-expanded", "true");
    // Focus active or first option
    const active = langDropdown.querySelector(".lang-item.active") ||
                   langDropdown.querySelector(".lang-item");
    if (active) active.focus();
  }
  function closeLangDropdown() {
    langDropdown.classList.remove("open");
    langBtn.setAttribute("aria-expanded", "false");
  }

  if (langBtn) {
    langBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      if (langDropdown.classList.contains("open")) {
        closeLangDropdown();
      } else {
        openLangDropdown();
      }
    });

    // Open on ArrowDown too
    langBtn.addEventListener("keydown", function(e) {
      if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openLangDropdown();
      }
    });
  }

  // Close on outside click
  document.addEventListener("click", function(e) {
    if (langPicker && !langPicker.contains(e.target)) closeLangDropdown();
  });

  // Language option keyboard nav (arrow keys + Enter/Space)
  document.querySelectorAll(".lang-item").forEach(function(item) {
    item.addEventListener("click", function() {
      const lang = item.dataset.lang;
      const pathBase = item.dataset.path || "/";
      window.location.href = lang === "hi" ? pathBase : "/" + lang + pathBase;
    });

    item.addEventListener("keydown", function(e) {
      const items = Array.from(langDropdown.querySelectorAll(".lang-item"));
      const idx   = items.indexOf(item);

      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        item.click();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        const next = items[idx + 1];
        if (next) next.focus();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        const prev = items[idx - 1];
        if (prev) prev.focus();
        else { closeLangDropdown(); langBtn.focus(); }
      } else if (e.key === "Tab" || e.key === "Escape") {
        closeLangDropdown();
        langBtn.focus();
      }
    });
  });

  // ── Mega-dropdown keyboard nav ──────────────────────────────────
  const megaNavItem = document.querySelector(".nav-item");
  const megaBtn     = megaNavItem && megaNavItem.querySelector(".nav-link[aria-haspopup]");
  const megaDrop    = megaNavItem && megaNavItem.querySelector(".mega-drop");

  function openMegaDrop() {
    if (!megaDrop) return;
    megaDrop.classList.add("open");
    megaBtn.setAttribute("aria-expanded", "true");
    const first = megaDrop.querySelector("a");
    if (first) first.focus();
  }
  function closeMegaDrop() {
    if (!megaDrop) return;
    megaDrop.classList.remove("open");
    if (megaBtn) megaBtn.setAttribute("aria-expanded", "false");
  }

  if (megaBtn) {
    // Add aria-expanded if missing
    if (!megaBtn.hasAttribute("aria-expanded")) {
      megaBtn.setAttribute("aria-expanded", "false");
    }

    megaBtn.addEventListener("keydown", function(e) {
      if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
        e.preventDefault();
        openMegaDrop();
      }
    });

    // Click toggles too
    megaBtn.addEventListener("click", function() {
      if (megaDrop.classList.contains("open")) closeMegaDrop();
      else openMegaDrop();
    });
  }

  if (megaDrop) {
    const megaLinks = Array.from(megaDrop.querySelectorAll("a"));

    megaLinks.forEach(function(link, i) {
      link.addEventListener("keydown", function(e) {
        if (e.key === "ArrowDown") {
          e.preventDefault();
          const next = megaLinks[i + 1];
          if (next) next.focus();
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          if (i === 0) { closeMegaDrop(); megaBtn.focus(); }
          else megaLinks[i - 1].focus();
        } else if (e.key === "Escape" || e.key === "Tab") {
          closeMegaDrop();
          megaBtn.focus();
        }
      });
    });

    // Close on outside click
    document.addEventListener("click", function(e) {
      if (megaNavItem && !megaNavItem.contains(e.target)) closeMegaDrop();
    });
  }

  // ── Active nav link ─────────────────────────────────────────────
  document.querySelectorAll(".nav-link, .drawer-link").forEach(function(a) {
    if (a.href && window.location.href.startsWith(a.href) && a.href.length > 4) {
      a.classList.add("active");
    }
  });

  // ── Smooth scroll anchor links ──────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    a.addEventListener("click", function(e) {
      const target = document.querySelector(a.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

})();
