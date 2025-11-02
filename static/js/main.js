const video = document.getElementById("video");
const chName = document.getElementById("ch-name");
const grid = document.getElementById("channelGrid");
const search = document.getElementById("search");
const categoryTabs = document.getElementById("categoryTabs");

let channels = [];
let selectedCategory = "All";
let hls;

// 📺 Load Channels
fetch("/channels")
  .then(res => res.json())
  .then(data => {
    channels = data;
    renderCategories(data);
    renderChannels(data);
    autoplayRandomChannel(); // 👈 auto play random channel
  });

// 🧩 Render Category Tabs
function renderCategories(data) {
  const categories = ["All", ...new Set(data.map(ch => ch.category))];
  categoryTabs.innerHTML = '';
  categories.forEach(cat => {
    const btn = document.createElement("button");
    btn.className = "btn btn-outline-info btn-sm me-2 category-btn";
    btn.textContent = cat;
    if (cat === "All") btn.classList.add("active");
    btn.addEventListener("click", () => {
      selectedCategory = cat;
      document.querySelectorAll(".category-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      filterChannels();
    });
    categoryTabs.appendChild(btn);
  });
}

// 🔎 Search Filter
search.addEventListener("input", filterChannels);

function filterChannels() {
  const term = search.value.toLowerCase();
  let filtered = channels.filter(ch => ch.name.toLowerCase().includes(term));
  if (selectedCategory !== "All") {
    filtered = filtered.filter(ch => ch.category === selectedCategory);
  }
  renderChannels(filtered);
}

// 🎬 Render Channel Grid
function renderChannels(list) {
  grid.innerHTML = '';
  if (list.length === 0) {
    grid.innerHTML = '<p class="text-center">No channels found</p>';
    return;
  }
  list.forEach(ch => {
    const col = document.createElement("div");
    col.className = "col";
    const card = document.createElement("div");
    card.className = "card channel-card text-white h-100";
    card.innerHTML = `
      <img src="${ch.logo}" class="card-img-top p-2" alt="${ch.name}">
      <div class="card-body text-center p-2">
        <p class="card-text">${ch.name}</p>
      </div>
    `;
    card.addEventListener("click", () => playChannel(ch.url, ch.name, card));
    col.appendChild(card);
    grid.appendChild(col);
  });
}

// ▶️ Play Channel
function playChannel(src, name, el) {
  if (hls) hls.destroy();
  if (Hls.isSupported()) {
    hls = new Hls();
    hls.loadSource(src);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, () => video.play());
  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    video.src = src;
    video.play();
  }
  chName.textContent = name;
  document.querySelectorAll(".channel-card").forEach(c => c.classList.remove("active"));
  el?.classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" }); // scroll to video
}

// 🔀 Auto-play random channel
function autoplayRandomChannel() {
  if (channels.length === 0) return;
  const randomIndex = Math.floor(Math.random() * channels.length);
  const randomChannel = channels[randomIndex];
  chName.textContent = "Auto-playing: " + randomChannel.name;
  playChannel(randomChannel.url, randomChannel.name);
}
