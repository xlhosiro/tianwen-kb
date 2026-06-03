/**
 * paralink.js — Paragraph permalink system for tianwen-kb
 * 
 * Features:
 * - Shows ¶ icon on paragraph hover
 * - Click to copy paragraph URL to clipboard
 * - Updates browser URL without page reload
 * - Highlights target paragraph when navigated via #para-NNNN
 * - Smooth scroll to target paragraph
 */
(function() {
  'use strict';

  var PARA_SELECTOR = '.chapter-body .para, .chapter-body p[id^="para-"]';
  var PERMALINK_TEXT = '\u00B6'; // ¶ pilcrow
  var HIGHLIGHT_DURATION = 10000; // ms

  // --- Create permalink button element ---
  function createPermalink(id) {
    var btn = document.createElement('span');
    btn.className = 'para-link';
    btn.textContent = PERMALINK_TEXT;
    btn.title = '复制段落文字';
    btn.setAttribute('data-para-id', id);
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      copyParagraphLink(id);
    });
    return btn;
  }

  // --- Copy paragraph text to clipboard, update URL ---
  function copyParagraphLink(id) {
    var el = document.getElementById(id);
    var url = window.location.href.split('#')[0] + '#' + id;

    // Update URL without reload
    try {
      history.replaceState(null, '', url);
    } catch(e) {}

    // Get plain text from paragraph (exclude ¶ permalink)
    var text = '';
    if (el) {
      var clone = el.cloneNode(true);
      var btn = clone.querySelector('.para-link');
      if (btn) btn.remove();
      text = clone.textContent.trim();
    }

    // Copy paragraph TEXT to clipboard
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function() {
        showToast('段落文字已复制');
      }).catch(function() {
        fallbackCopy(text);
      });
    } else {
      fallbackCopy(text);
    }
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      showToast('链接已复制！');
    } catch(e) {
      showToast('复制失败，请手动复制地址栏链接');
    }
    document.body.removeChild(ta);
  }

  // --- Toast notification ---
  function showToast(msg) {
    var existing = document.querySelector('.para-toast');
    if (existing) existing.remove();

    var toast = document.createElement('div');
    toast.className = 'para-toast';
    toast.textContent = msg;
    document.body.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(function() {
      toast.classList.add('show');
    });

    setTimeout(function() {
      toast.classList.remove('show');
      setTimeout(function() {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 300);
    }, 1800);
  }

  // --- Highlight target paragraph ---
  function highlightTarget() {
    var hash = window.location.hash;
    if (!hash || hash.indexOf('para-') !== 1) return;

    var id = hash.substring(1);
    var el = document.getElementById(id);
    if (!el) return;

    // Scroll to element
    setTimeout(function() {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);

    // Add highlight class
    el.classList.add('para-highlight');
    setTimeout(function() {
      el.classList.remove('para-highlight');
    }, HIGHLIGHT_DURATION);
  }

  // --- Setup all paragraphs ---
  function setupParagraphs() {
    var paragraphs = document.querySelectorAll(PARA_SELECTOR);
    
    paragraphs.forEach(function(para) {
      var id = para.id;
      if (!id) return;

      // Skip if already has a permalink
      if (para.querySelector('.para-link')) return;

      // Add relative positioning context
      // (already set via CSS on .chapter-body .para)

      // Create and insert permalink
      var link = createPermalink(id);
      para.insertBefore(link, para.firstChild);
    });
  }

  // --- Handle hash change (browser back/forward) ---
  window.addEventListener('hashchange', function() {
    var hash = window.location.hash;
    if (hash && hash.indexOf('para-') === 1) {
      highlightTarget();
    }
  });

  // --- Initialize ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setupParagraphs();
      highlightTarget();
    });
  } else {
    setupParagraphs();
    highlightTarget();
  }

})();
