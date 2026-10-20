(() => {
  'use strict';

  const preferenceKey = 'edwin-jose-portfolio-theme';
  const root = document.documentElement;
  const themeColor = document.querySelector('meta[name="theme-color"]');
  let currentTheme = 'dark';
  let controls = [];

  try {
    if (localStorage.getItem(preferenceKey) === 'light') currentTheme = 'light';
  } catch {
    // The switch still works for this page when browser storage is unavailable.
  }

  function applyTheme(theme) {
    currentTheme = theme === 'light' ? 'light' : 'dark';
    root.dataset.theme = currentTheme;
    if (themeColor) themeColor.content = currentTheme === 'light' ? '#F4F7FA' : '#0C1015';

    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    for (const control of controls) {
      control.setAttribute('aria-pressed', String(currentTheme === 'light'));
      control.setAttribute('aria-label', `Switch to ${nextTheme} theme`);
      control.querySelector('[data-theme-label]').textContent = `${nextTheme === 'light' ? 'Light' : 'Dark'} theme`;
    }
  }

  // Runs before the stylesheet to restore a saved choice without a dark flash.
  applyTheme(currentTheme);

  function bindControls() {
    controls = Array.from(document.querySelectorAll('[data-theme-toggle]'));
    for (const control of controls) {
      control.hidden = false;
      control.addEventListener('click', () => {
        applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
        try {
          localStorage.setItem(preferenceKey, currentTheme);
        } catch {
          // Do not block the current-page preference if persistence is denied.
        }
      });
    }
    applyTheme(currentTheme);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindControls, { once: true });
  } else {
    bindControls();
  }

  window.addEventListener('storage', (event) => {
    if (event.key === preferenceKey || event.key === null) applyTheme(event.newValue);
  });
})();
