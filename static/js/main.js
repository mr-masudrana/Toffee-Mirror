const video = document.getElementById("video");
const chName = document.getElementById("ch-name");
const grid = document.getElementById("channelGrid");
const search = document.getElementById("search");
const categoryTabs = document.getElementById("categoryTabs");

let channels = [];
let selectedCategory = "All";
let hls;

// Load channels
fetch('/channels')
  .then(res => res.json())
  .then(data => {
    channels = data;
    renderCategories(data);
    renderChannels(data);
    autoplayRandomChannel();
  }).catch(err => {
    grid.innerHTML = '<p class="text-center text-danger">Failed to load channels</p>';
    console.error('channels load error', err);
  });

// Render categories
function renderCategories(data) {
  const cats = ["All", ...new Set(data.map(c=>c.category))];
  categoryTabs.innerHTML = '';
  cats.forEach(cat => {
    const btn = document.createElement('button');
    btn.className = 'btn btn-outline-info btn-sm me-2 category-btn';
    btn.textContent = cat;
    if (cat === 'All') btn.classList.add('active');
    btn.addEventListener('click', () => { document.querySelectorAll('.category-btn').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); selectedCategory = cat; filterChannels(); });
    categoryTabs.appendChild(btn);
  });
}

// Search
search.addEventListener('input', filterChannels);

function filterChannels() {
  const term = search.value.toLowerCase();
  let filtered = channels.filter(ch => ch.name.toLowerCase().includes(term));
  if (selectedCategory !== 'All') filtered = filtered.filter(ch => ch.category === selectedCategory);
  renderChannels(filtered);
}

function renderChannels(list) {
  grid.innerHTML = '';
  if (!list.length) { grid.innerHTML = '<p class="text-center">No channels found</p>'; return; }
  list.forEach(ch => {
    const col = document.createElement('div'); col.className = 'col';
    const card = document.createElement('div'); card.className = 'card channel-card text-white h-100';
    card.innerHTML = `<img src="${ch.logo}" class="card-img-top p-2" alt="${ch.name}"><div class="card-body text-center p-2"><p class="card-text">${ch.name}</p></div>`;
    card.addEventListener('click', () => playChannel(ch.url, ch.name, card));
    col.appendChild(card); grid.appendChild(col);
  });
}

function playChannel(src, name, el) {
  // Ensure src routes through our proxy (must start with /cdn/)
  if (!src.startsWith('/')) src = '/' + src;
  if (!src.startsWith('/cdn/')) {
    // assume it's relative to /cdn/
    src = '/cdn' + src;
  }

  if (hls) { try { hls.destroy(); } catch(e) { console.warn(e); } }
  if (Hls.isSupported()) {
    hls = new Hls();
    hls.loadSource(src);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, () => video.play());
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = src;
    video.play();
  }
  chName.textContent = name;
  document.querySelectorAll('.channel-card').forEach(c=>c.classList.remove('active'));
  el?.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function autoplayRandomChannel() {
  if (!channels.length) return;
  const idx = Math.floor(Math.random() * channels.length);
  const ch = channels[idx];
  chName.textContent = 'Auto-playing: ' + ch.name;
  playChannel(ch.url, ch.name);
}
