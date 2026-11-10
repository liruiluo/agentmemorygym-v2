/* Small, offline-friendly enhancements. The entire research story remains readable without JS. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  document.querySelectorAll('[data-tabs]').forEach(group => {
    const tabs = [...group.querySelectorAll('button')];
    group.setAttribute('role', 'tablist');
    const panels = tabs.map(tab => document.getElementById(tab.getAttribute('aria-controls')));
    const select = (index, focus = false) => {
      tabs.forEach((tab, i) => {
        tab.setAttribute('role', 'tab');
        tab.setAttribute('aria-selected', String(i === index));
        tab.tabIndex = i === index ? 0 : -1;
        panels[i].setAttribute('role', 'tabpanel');
        panels[i].hidden = i !== index;
      });
      if (focus) tabs[index].focus();
    };
    tabs.forEach((tab, i) => {
      tab.addEventListener('click', () => select(i));
      tab.addEventListener('keydown', event => {
        let next;
        if (event.key === 'ArrowRight') next = (i + 1) % tabs.length;
        else if (event.key === 'ArrowLeft') next = (i + tabs.length - 1) % tabs.length;
        else if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = tabs.length - 1;
        if (next !== undefined) { event.preventDefault(); select(next, true); }
      });
    });
    select(0);
  });
  const copy = document.getElementById('copy-citation');
  const status = document.getElementById('copy-status');
  if (copy) copy.addEventListener('click', async () => {
    const content = document.getElementById('citation-text');
    try {
      if (!navigator.clipboard) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(content.textContent);
      status.textContent = 'Citation copied.';
    } catch (_) {
      const range = document.createRange();
      range.selectNodeContents(content);
      const selection = window.getSelection();
      selection.removeAllRanges(); selection.addRange(range);
      status.textContent = 'Citation selected. Press ⌘C or Ctrl+C to copy.';
    }
  });
})();
