(() => {
  const tools = document.querySelector('.publication-tools');
  if (!tools) return;
  const search = document.querySelector('#publication-search');
  const buttons = [...tools.querySelectorAll('[data-publication-filter]')];
  const reset = tools.querySelector('.publication-reset');
  const count = document.querySelector('#publication-count');
  const empty = document.querySelector('.publication-empty');
  const contents = document.querySelector('.publications-contents');
  const sections = [...document.querySelectorAll('.publications-section')].map(section => ({
    element: section,
    records: [...section.querySelectorAll('.bibliography > li')].map(element => ({
      element,
      text: element.textContent.normalize('NFKC').toLocaleLowerCase()
    }))
  }));
  let type = 'all';
  const update = () => {
    const terms = search.value.normalize('NFKC').toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let matches = 0;
    for (const section of sections) {
      let visible = 0;
      for (const record of section.records) {
        const show = (type === 'all' || type === section.element.id) && terms.every(term => record.text.includes(term));
        record.element.hidden = !show;
        if (show) visible++;
      }
      section.element.hidden = visible === 0;
      matches += visible;
    }
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.publicationFilter === type)));
    count.textContent = `${matches} of 11 works`;
    empty.hidden = matches !== 0;
    reset.hidden = type === 'all' && !search.value;
  };
  buttons.forEach(button => button.addEventListener('click', () => {
    type = button.dataset.publicationFilter;
    update();
  }));
  search.addEventListener('input', update);
  reset.addEventListener('click', () => {
    type = 'all';
    search.value = '';
    update();
    search.focus();
  });
  tools.hidden = false;
  contents.hidden = true;
  update();
})();
