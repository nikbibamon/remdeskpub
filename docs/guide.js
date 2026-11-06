/* Optional local checklist. It stores only step IDs, never credentials. */
(() => {
  'use strict';
  document.documentElement.classList.add('has-js');
  const key = 'tvijo.remdesk.owner-guide.v1';
  const checks = [...document.querySelectorAll('[data-check]')];
  const live = document.querySelector('#copy-status');
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || '{}') || {}; } catch (_) {}
  checks.forEach(el => { el.checked = saved[el.dataset.check] === true; });
  function update(persist) {
    const done = checks.filter(el => el.checked).length;
    const count = document.querySelector('#progress-count');
    const bar = document.querySelector('progress');
    if (count) count.textContent = `${done} / ${checks.length}`;
    if (bar) { bar.max = checks.length; bar.value = done; }
    if (persist) {
      const state = Object.fromEntries(checks.map(el => [el.dataset.check, el.checked]));
      try { localStorage.setItem(key, JSON.stringify(state)); } catch (_) {}
    }
  }
  checks.forEach(el => el.addEventListener('change', () => update(true)));
  document.querySelector('[data-reset]')?.addEventListener('click', () => {
    checks.forEach(el => { el.checked = false; });
    update(true);
  });
  document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      const target = document.getElementById(button.dataset.copy);
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.textContent);
        live.textContent = button.dataset.success;
      } catch (_) {
        const range = document.createRange(); range.selectNodeContents(target);
        const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
        live.textContent = button.dataset.fallback;
      }
    });
  });
  update(false);
})();
