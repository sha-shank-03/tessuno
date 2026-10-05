'use strict';
const search = document.querySelector('#search');
const kind = document.querySelector('#kind');
const stack = document.querySelector('#stack');
const reset = document.querySelector('#reset');
const cards = [...document.querySelectorAll('article')];
const targets = new Map(cards.map(card => [card.id, card]));
function update() {
  const tokens = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
  let visible = 0;
  for (const card of cards) {
    card.hidden = !tokens.every(token => card.dataset.search.toLowerCase().includes(token))
      || (kind.value !== '' && card.dataset.kind !== kind.value)
      || (stack.value !== '' && !JSON.parse(card.dataset.stacks).includes(stack.value));
    if (!card.hidden) visible++;
  }
  document.querySelector('#count').textContent = `${visible} of ${cards.length} object${cards.length === 1 ? '' : 's'}`;
  document.querySelector('#empty').hidden = visible !== 0;
}
search.addEventListener('input', update);
kind.addEventListener('change', update);
stack.addEventListener('change', update);
reset.addEventListener('click', () => {
  search.value = kind.value = stack.value = '';
  update();
  search.focus();
});
function revealFragment() {
  let id;
  try { id = decodeURIComponent(window.location.hash.slice(1)); }
  catch { return false; }
  const card = targets.get(id);
  if (!card) return false;
  search.value = kind.value = stack.value = '';
  update();
  card.focus();
  card.scrollIntoView({block: 'start'});
  return true;
}
let historyRefresh;
function refreshFromHistory() {
  // History traversal can restore form values and scroll after pageshow/popstate.
  // Read the current fragment when the browser has finished that restoration.
  clearTimeout(historyRefresh);
  historyRefresh = setTimeout(() => {
    historyRefresh = undefined;
    if (!revealFragment()) update();
  }, 0);
}
window.addEventListener('hashchange', revealFragment);
window.addEventListener('pageshow', refreshFromHistory);
window.addEventListener('popstate', refreshFromHistory);
for (const control of [search, kind, stack, reset]) control.disabled = false;
update();
revealFragment();
