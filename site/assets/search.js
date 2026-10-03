'use strict';
const search = document.querySelector('#search');
const cards = [...document.querySelectorAll('article')];
search.addEventListener('input', () => {
  const tokens = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
  let visible = 0;
  for (const card of cards) {
    card.hidden = !tokens.every(token => card.dataset.search.toLowerCase().includes(token));
    if (!card.hidden) visible++;
  }
  document.querySelector('#count').textContent = `${visible} object${visible === 1 ? '' : 's'}`;
});
