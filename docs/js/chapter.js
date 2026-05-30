/**
 * chapter.js — Client-side interactivity for tianwen-kb chapter pages
 * Dark astronomy theme · Pure vanilla JavaScript
 * Features: TOC generation, anchor links, back-to-top, astro-entity tooltips, keyboard shortcuts
 */
(function () {
  'use strict';

  /* =============================================================
   * Color palette (matching style.css dark astronomy theme)
   * ============================================================= */
  const COLORS = {
    bgDeepest:  '#0a0e1a',
    bgCard:     '#111827',
    bgSidebar:  '#1a1f35',
    bgHover:    '#1e2540',
    textBody:   '#c8d0dc',
    textHeading:'#e8ecf2',
    textMuted:  '#8b95a8',
    accentGold: '#c9a96e',
    accentWarm: '#d4a574',
    border:     '#2a3045',
    borderLight:'#3a4058',
    starRed:    '#F49B8A',
  };

  /* =============================================================
   * 1. TABLE OF CONTENTS (auto-generate from h2/h3 headings)
   * ============================================================= */
  function buildTOC() {
    var body = document.querySelector('.chapter-body');
    if (!body) return;

    var headings = body.querySelectorAll('h2, h3');
    if (headings.length < 2) return; // skip if too few headings

    // --- Create TOC container ---
    var nav = document.createElement('nav');
    nav.className = 'toc-nav';
    nav.setAttribute('aria-label', 'Table of Contents');

    var tocTitle = document.createElement('div');
    tocTitle.className = 'toc-title';
    tocTitle.textContent = '目 录';
    nav.appendChild(tocTitle);

    var list = document.createElement('ol');
    list.className = 'toc-list';

    // --- Map heading text to sanitized id ---
    var usedIds = {};

    function makeId(text) {
      var base = text
        .replace(/[【】\[\]「」『』]/g, '')
        .replace(/[·‧・]/g, '-')
        .replace(/[^\w\u4e00-\u9fff-]/g, '')
        .trim();
      if (!base) base = 'section';
      var id = base;
      var n = 1;
      while (usedIds[id]) {
        n++;
        id = base + '-' + n;
      }
      usedIds[id] = true;
      return id;
    }

    headings.forEach(function (heading, i) {
      var text = heading.textContent.trim();
      var id = heading.id || makeId(text);
      if (!heading.id) heading.id = id;

      var li = document.createElement('li');
      li.className = 'toc-item toc-' + heading.tagName.toLowerCase();

      var a = document.createElement('a');
      a.href = '#' + id;
      a.textContent = text;
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var target = document.getElementById(id);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          history.pushState(null, '', '#' + id);
        }
      });

      li.appendChild(a);
      list.appendChild(li);
    });

    nav.appendChild(list);

    // --- Insert TOC at top of chapter-body ---
    var firstChild = body.firstChild;
    body.insertBefore(nav, firstChild);
  }

  /* =============================================================
   * 2. ANCHOR LINKS ON HEADINGS (click to copy URL with hash)
   * ============================================================= */
  function addAnchorLinks() {
    var body = document.querySelector('.chapter-body');
    if (!body) return;

    var headings = body.querySelectorAll('h2, h3, h4');
    headings.forEach(function (heading) {
      // Ensure heading has an id
      if (!heading.id) {
        var text = heading.textContent.trim();
        var id = text
          .replace(/[【】\[\]「」『』]/g, '')
          .replace(/[^\w\u4e00-\u9fff-]/g, '')
          .trim() || 'section';
        heading.id = id;
      }

      // Make heading clickable for anchor copy
      heading.style.cursor = 'pointer';
      heading.setAttribute('title', '点击复制链接');
      heading.setAttribute('role', 'button');
      heading.setAttribute('tabindex', '0');

      heading.addEventListener('click', function (e) {
        copyAnchor(heading.id);
      });

      // Keyboard accessibility
      heading.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          copyAnchor(heading.id);
        }
      });

      // Insert ¶ anchor icon
      var anchor = document.createElement('span');
      anchor.className = 'heading-anchor';
      anchor.setAttribute('aria-hidden', 'true');
      anchor.textContent = ' ¶';
      heading.appendChild(anchor);
    });
  }

  function copyAnchor(id) {
    var url = window.location.origin + window.location.pathname + '#' + id;
    history.pushState(null, '', '#' + id);

    // Try Clipboard API first
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () {
        showToast('链接已复制到剪贴板');
      }).catch(function () {
        showToast('链接: ' + url);
      });
    } else {
      // Fallback
      var ta = document.createElement('textarea');
      ta.value = url;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); showToast('链接已复制到剪贴板'); } catch (err) { showToast('链接: ' + url); }
      document.body.removeChild(ta);
    }
  }

  /* =============================================================
   * Toast notification helper
   * ============================================================= */
  function showToast(message) {
    // Remove any existing toast
    var existing = document.querySelector('.chapter-toast');
    if (existing) existing.remove();

    var toast = document.createElement('div');
    toast.className = 'chapter-toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    // Trigger reflow for transition
    void toast.offsetWidth;
    toast.classList.add('visible');

    setTimeout(function () {
      toast.classList.remove('visible');
      setTimeout(function () { if (toast.parentNode) toast.remove(); }, 300);
    }, 2000);
  }

  /* =============================================================
   * 3. BACK-TO-TOP BUTTON
   * ============================================================= */
  function initBackToTop() {
    var btn = document.createElement('button');
    btn.className = 'back-to-top';
    btn.setAttribute('aria-label', '回到顶部');
    btn.innerHTML = '&#9650;';
    btn.title = '回到顶部';

    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    document.body.appendChild(btn);

    var ticking = false;
    window.addEventListener('scroll', function () {
      if (!ticking) {
        requestAnimationFrame(function () {
          if (window.scrollY > 300) {
            btn.classList.add('visible');
          } else {
            btn.classList.remove('visible');
          }
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  /* =============================================================
   * 4. ENHANCED TOOLTIPS ON .astro-entity SPANS
   * ============================================================= */
  function initEntityTooltips() {
    var tooltip = null;
    var currentTarget = null;

    function createTooltip() {
      var el = document.createElement('div');
      el.className = 'astro-tooltip';
      el.setAttribute('role', 'tooltip');
      document.body.appendChild(el);
      return el;
    }

    function positionTooltip(tip, target) {
      var rect = target.getBoundingClientRect();
      var tipH = tip.offsetHeight;
      var tipW = tip.offsetWidth;

      var left = rect.left + rect.width / 2 - tipW / 2;
      var top = rect.top - tipH - 8;

      // Keep within viewport
      if (left < 8) left = 8;
      if (left + tipW > window.innerWidth - 8) left = window.innerWidth - tipW - 8;
      if (top < 8) top = rect.bottom + 8;

      tip.style.left = left + 'px';
      tip.style.top = top + 'px';
    }

    function showTooltip(target) {
      if (!tooltip) tooltip = createTooltip();
      currentTarget = target;

      // Extract name from title attribute (set during HTML generation)
      var name = target.getAttribute('title') || target.textContent.trim();
      // Also get the color from inline style
      var color = '';
      var style = target.getAttribute('style') || '';
      var colorMatch = style.match(/color:\s*([^;]+)/);
      if (colorMatch) color = colorMatch[1].trim();

      // Build tooltip content
      var colorDot = color ? '<span class="tooltip-dot" style="background:' + color + '"></span>' : '';
      tooltip.innerHTML = colorDot + '<span class="tooltip-name">' + escapeHTML(name) + '</span>';

      positionTooltip(tooltip, target);
      tooltip.classList.add('visible');
    }

    function hideTooltip() {
      if (tooltip) {
        tooltip.classList.remove('visible');
        currentTarget = null;
      }
    }

    function escapeHTML(str) {
      var div = document.createElement('div');
      div.appendChild(document.createTextNode(str));
      return div.innerHTML;
    }

    // Delegate events on document.body for efficiency
    document.body.addEventListener('mouseover', function (e) {
      var entity = e.target.closest('.astro-entity');
      if (!entity) {
        // Check if we moved from entity to something else
        if (currentTarget && !currentTarget.contains(e.relatedTarget)) {
          hideTooltip();
        }
        return;
      }
      if (entity !== currentTarget) {
        showTooltip(entity);
      }
    });

    document.body.addEventListener('mouseout', function (e) {
      var entity = e.target.closest('.astro-entity');
      if (entity && !entity.contains(e.relatedTarget)) {
        hideTooltip();
      }
    });

    // Touch support: show on tap, hide on scroll or outside tap
    document.body.addEventListener('touchstart', function (e) {
      var entity = e.target.closest('.astro-entity');
      if (entity) {
        e.preventDefault();
        showTooltip(entity);
      } else if (!e.target.closest('.astro-tooltip')) {
        hideTooltip();
      }
    }, { passive: false });

    window.addEventListener('scroll', function () {
      if (currentTarget) hideTooltip();
    }, { passive: true });
  }

  /* =============================================================
   * 5. KEYBOARD SHORTCUTS
   * ============================================================= */
  function initKeyboardShortcuts() {
    var tocNav = null;

    document.addEventListener('keydown', function (e) {
      // Ignore if user is typing in an input/textarea
      var tag = (e.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select' || e.target.isContentEditable) {
        return;
      }
      // Ignore if modifier keys are pressed (except no modifiers)
      if (e.ctrlKey || e.altKey || e.metaKey) return;

      // 's' — focus search
      if (e.key === 's' || e.key === 'S') {
        e.preventDefault();
        focusSearch();
        return;
      }

      // 't' — toggle TOC
      if (e.key === 't' || e.key === 'T') {
        e.preventDefault();
        toggleTOC();
      }
    });
  }

  function focusSearch() {
    // Try to focus a search input on the page (from top nav or sidebar)
    var searchInput = document.querySelector('input[type="search"], input[name="search"], input[placeholder*="搜索"], input[placeholder*="search"], #search-input');
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
      return;
    }
    // Fallback: navigate to search page
    window.location.href = '../search.html';
  }

  function toggleTOC() {
    var toc = document.querySelector('.toc-nav');
    if (!toc) return;

    if (toc.classList.contains('toc-collapsed')) {
      toc.classList.remove('toc-collapsed');
      showToast('目录已展开');
    } else {
      toc.classList.add('toc-collapsed');
      showToast('目录已折叠');
    }
  }

  /* =============================================================
   * STYLE INJECTION (all CSS for JS-generated elements)
   * ============================================================= */
  function injectStyles() {
    var css = [
      /* ---- TOC ---- */
      '.toc-nav {',
        'background:' + COLORS.bgCard + ';',
        'border:1px solid ' + COLORS.border + ';',
        'border-radius:8px;',
        'padding:24px 28px;',
        'margin-bottom:32px;',
        'transition:max-height 0.35s ease, opacity 0.35s ease, padding 0.35s ease;',
        'overflow:hidden;',
      '}',
      '.toc-nav.toc-collapsed {',
        'max-height:48px !important;',
        'padding-top:12px !important;',
        'padding-bottom:12px !important;',
        'opacity:0.85;',
      '}',
      '.toc-nav.toc-collapsed .toc-list {',
        'display:none;',
      '}',
      '.toc-title {',
        'font-family:var(--font-serif);',
        'font-size:1.15rem;',
        'font-weight:700;',
        'color:' + COLORS.accentGold + ';',
        'padding-bottom:12px;',
        'margin-bottom:8px;',
        'border-bottom:1px solid ' + COLORS.border + ';',
        'letter-spacing:0.15em;',
        'text-align:center;',
      '}',
      '.toc-list {',
        'list-style:none;',
        'padding:0;',
        'margin:0;',
      '}',
      '.toc-item {',
        'line-height:1.6;',
      '}',
      '.toc-item a {',
        'color:' + COLORS.textBody + ';',
        'text-decoration:none;',
        'display:block;',
        'padding:4px 0;',
        'transition:color 0.2s ease;',
        'font-size:0.95rem;',
      '}',
      '.toc-item a:hover {',
        'color:' + COLORS.accentGold + ';',
      '}',
      '.toc-h3 a {',
        'padding-left:20px;',
        'font-size:0.88rem;',
        'color:' + COLORS.textMuted + ';',
      '}',
      '.toc-h3 a::before {',
        'content:"└ ";',
        'color:' + COLORS.borderLight + ';',
        'opacity:0.6;',
      '}',

      /* ---- Heading Anchor ---- */
      '.heading-anchor {',
        'opacity:0;',
        'font-size:0.8em;',
        'color:' + COLORS.accentGold + ';',
        'transition:opacity 0.2s ease;',
        'margin-left:4px;',
        'cursor:pointer;',
      '}',
      'h2:hover .heading-anchor,',
      'h3:hover .heading-anchor,',
      'h4:hover .heading-anchor {',
        'opacity:1;',
      '}',
      'h2:hover, h3:hover, h4:hover {',
        'color:' + COLORS.accentGold + ';',
        'transition:color 0.2s ease;',
      '}',

      /* ---- Back-to-top ---- */
      '.back-to-top {',
        'position:fixed;',
        'bottom:32px;',
        'right:32px;',
        'width:44px;',
        'height:44px;',
        'border-radius:50%;',
        'border:1px solid ' + COLORS.borderLight + ';',
        'background:' + COLORS.bgCard + ';',
        'color:' + COLORS.accentGold + ';',
        'font-size:1.1rem;',
        'cursor:pointer;',
        'opacity:0;',
        'transform:translateY(20px);',
        'transition:opacity 0.3s ease, transform 0.3s ease, background 0.2s ease;',
        'z-index:999;',
        'display:flex;',
        'align-items:center;',
        'justify-content:center;',
        'backdrop-filter:blur(8px);',
        '-webkit-backdrop-filter:blur(8px);',
      '}',
      '.back-to-top.visible {',
        'opacity:0.85;',
        'transform:translateY(0);',
      '}',
      '.back-to-top:hover {',
        'background:' + COLORS.bgHover + ';',
        'opacity:1;',
        'color:' + COLORS.accentWarm + ';',
        'border-color:' + COLORS.accentGold + ';',
      '}',

      /* ---- Astro Tooltip ---- */
      '.astro-tooltip {',
        'position:fixed;',
        'z-index:1000;',
        'pointer-events:none;',
        'padding:8px 14px;',
        'background:' + COLORS.bgCard + ';',
        'border:1px solid ' + COLORS.borderLight + ';',
        'border-radius:6px;',
        'font-family:var(--font-sans);',
        'font-size:0.92rem;',
        'color:' + COLORS.textHeading + ';',
        'white-space:nowrap;',
        'opacity:0;',
        'transform:translateY(6px);',
        'transition:opacity 0.2s ease, transform 0.2s ease;',
        'box-shadow:0 4px 16px rgba(0,0,0,0.5);',
        'display:flex;',
        'align-items:center;',
        'gap:8px;',
      '}',
      '.astro-tooltip.visible {',
        'opacity:1;',
        'transform:translateY(0);',
      '}',
      '.tooltip-dot {',
        'display:inline-block;',
        'width:10px;',
        'height:10px;',
        'border-radius:50%;',
        'flex-shrink:0;',
        'box-shadow:0 0 6px currentColor;',
      '}',
      '.tooltip-name {',
        'font-weight:500;',
        'letter-spacing:0.03em;',
      '}',

      /* ---- Toast ---- */
      '.chapter-toast {',
        'position:fixed;',
        'bottom:40px;',
        'left:50%;',
        'transform:translateX(-50%) translateY(16px);',
        'background:' + COLORS.bgCard + ';',
        'border:1px solid ' + COLORS.accentGold + ';',
        'color:' + COLORS.accentGold + ';',
        'padding:10px 24px;',
        'border-radius:6px;',
        'font-family:var(--font-sans);',
        'font-size:0.88rem;',
        'z-index:2000;',
        'opacity:0;',
        'transition:opacity 0.3s ease, transform 0.3s ease;',
        'box-shadow:0 4px 20px rgba(0,0,0,0.5);',
        'pointer-events:none;',
      '}',
      '.chapter-toast.visible {',
        'opacity:1;',
        'transform:translateX(-50%) translateY(0);',
      '}',
    ].join('\n');

    var style = document.createElement('style');
    style.id = 'chapter-js-styles';
    style.textContent = css;
    document.head.appendChild(style);
  }

  /* =============================================================
   * INITIALIZATION
   * ============================================================= */
  function init() {
    injectStyles();
    buildTOC();
    addAnchorLinks();
    initBackToTop();
    initEntityTooltips();
    initKeyboardShortcuts();
  }

  // Run on DOMContentLoaded (or immediately if already loaded)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
