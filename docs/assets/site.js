(() => {
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.menu-button');
  const navigation = document.querySelector('#primary-navigation');

  if (header && toggle && navigation) {
    const closeMenu = (restoreFocus = false) => {
      navigation.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.textContent = 'Menu';
      if (restoreFocus) toggle.focus();
    };

    toggle.hidden = false;
    header.dataset.enhanced = 'true';
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open));
      toggle.textContent = open ? 'Close' : 'Menu';
      navigation.classList.toggle('is-open', open);
    });
    navigation.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMenu();
    });
    header.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        closeMenu(true);
      }
    });
  }

  const printButton = document.querySelector('[data-print]');
  if (printButton) {
    printButton.hidden = false;
    printButton.addEventListener('click', () => window.print());
  }

  // Preserve the reader's disclosure choices after printing the full page.
  let disclosuresToRestore = [];
  window.addEventListener('beforeprint', () => {
    disclosuresToRestore = Array.from(document.querySelectorAll('details:not([open])'));
    disclosuresToRestore.forEach((details) => { details.open = true; });
  });
  window.addEventListener('afterprint', () => {
    disclosuresToRestore.forEach((details) => { details.open = false; });
    disclosuresToRestore = [];
  });
})();
