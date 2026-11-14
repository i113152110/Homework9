/* 首頁搜尋與分類，無外部套件。Article metadata is maintained in data/articles.js */
(function () {
  const grid = document.getElementById('article-grid');
  if (!grid) return;
  const articles = Array.isArray(window.REPORT_ARTICLES) ? window.REPORT_ARTICLES : [];
  const search = document.getElementById('article-search');
  const filters = Array.from(document.querySelectorAll('[data-filter]'));
  const counter = document.getElementById('result-count');
  const empty = document.getElementById('empty-state');
  let active = '全部';
  // 資料文字只能透過 textContent 填入；連結僅接受專案相對路徑。
  function makeCard(article) {
    const a = document.createElement('a');
    if (!/^pages\/[a-z0-9-]+\.html$/.test(article.path)) return null;
    a.className = 'article-card';
    a.href = article.path;
    const top = document.createElement('div'); top.className = 'card-top';
    const num = document.createElement('span'); num.className = 'card-num'; num.textContent = article.number;
    const cat = document.createElement('span'); cat.textContent = article.category + ' / ' + article.level;
    top.append(num, cat);
    const title = document.createElement('h3'); title.className = 'card-title'; title.textContent = article.title;
    const desc = document.createElement('p'); desc.className = 'card-desc'; desc.textContent = article.subtitle;
    const bottom = document.createElement('div'); bottom.className = 'card-bottom';
    const mins = document.createElement('span'); mins.textContent = '約 ' + article.minutes + ' 分鐘閱讀';
    const read = document.createElement('span'); read.className = 'card-read'; read.textContent = '閱讀文章 →';
    bottom.append(mins, read);
    a.append(top, title, desc, bottom);
    return a;
  }
  function update() {
    const q = search.value.trim().toLocaleLowerCase('zh-Hant');
    const visible = articles.filter(article => {
      const categoryMatches = active === '全部' || article.category === active;
      const haystack = [article.title, article.subtitle, article.category, ...(article.tags || [])].join(' ').toLocaleLowerCase('zh-Hant');
      return categoryMatches && haystack.includes(q);
    });
    grid.replaceChildren(...visible.map(makeCard).filter(Boolean));
    counter.textContent = '目前顯示 ' + visible.length + ' / ' + articles.length + ' 篇筆記';
    empty.classList.toggle('hidden', visible.length !== 0);
  }
  search.addEventListener('input', update);
  filters.forEach(button => button.addEventListener('click', () => {
    active = button.dataset.filter;
    filters.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    update();
  }));
  update();
})();
