/* ═══════════════════════════════════════════════════════
   KrishiMind AI — Dashboard Application Logic
   Real-time data, smooth animations, all features working
   ═══════════════════════════════════════════════════════ */

const API = window.location.origin + '/api';
const WEATHER_API = 'https://api.open-meteo.com/v1/forecast';
let onlineMode = true;
let history = [];

// Weather code → emoji + description
const WMO = {
    0: '☀️ Clear', 1: '🌤️ Mostly Clear', 2: '⛅ Partly Cloudy', 3: '☁️ Overcast',
    45: '🌫️ Fog', 48: '🌫️ Rime Fog', 51: '🌦️ Light Drizzle', 53: '🌧️ Drizzle',
    55: '🌧️ Heavy Drizzle', 61: '🌧️ Light Rain', 63: '🌧️ Rain', 65: '🌧️ Heavy Rain',
    71: '🌨️ Light Snow', 73: '🌨️ Snow', 75: '🌨️ Heavy Snow', 80: '🌦️ Showers',
    81: '🌧️ Heavy Showers', 82: '⛈️ Violent Showers', 95: '⛈️ Thunderstorm',
    96: '⛈️ Hail Storm', 99: '⛈️ Heavy Hail'
};
function wmoIcon(code) { return (WMO[code] || '🌤️ Unknown').split(' ')[0]; }
function wmoDesc(code) { return (WMO[code] || 'Unknown').split(' ').slice(1).join(' '); }

// ── INIT ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadPopularQuestions();
    loadWeather();
    loadMarketPrices();
    loadCropGuide();
    loadPestSolutions();
    checkHealth();
});

// ── NAVIGATION ──────────────────────────────────────────
function navigate(page, el) {
    // Update pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const target = document.getElementById('page-' + page);
    if (target) target.classList.add('active');

    // Update nav
    if (el) {
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
    } else {
        document.querySelectorAll('.nav-item').forEach(n => {
            n.classList.toggle('active', n.dataset.page === page);
        });
    }

    // Close sidebar on mobile
    document.getElementById('sidebar').classList.remove('open');
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// ── ONLINE/OFFLINE ──────────────────────────────────────
function toggleOnline() {
    onlineMode = !onlineMode;
    const btn = document.getElementById('modeBtn');
    const dot = document.getElementById('modeDot');
    const text = document.getElementById('modeText');
    btn.className = 'mode-btn ' + (onlineMode ? 'online' : 'offline');
    text.textContent = onlineMode ? 'Online' : 'Offline';
}

async function checkHealth() {
    try {
        const r = await fetch(API + '/health');
        const d = await r.json();
        if (!d.ai_ready) { onlineMode = false; toggleOnline(); }
    } catch { onlineMode = false; }
}

// ── WEATHER (Real-time Open-Meteo) ──────────────────────
async function loadWeather() {
    const sel = document.getElementById('weatherCity');
    const [lat, lon] = sel.value.split(',');
    const cityName = sel.options[sel.selectedIndex].text;

    try {
        const url = `${WEATHER_API}?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,apparent_temperature&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code&hourly=soil_moisture_0_to_1cm&timezone=Asia/Kolkata&forecast_days=7`;
        const r = await fetch(url);
        const d = await r.json();

        const c = d.current;
        const icon = wmoIcon(c.weather_code);
        const desc = wmoDesc(c.weather_code);

        // Update dashboard cards
        document.getElementById('dashTemp').textContent = Math.round(c.temperature_2m) + '°C';
        document.getElementById('dashWeatherDesc').textContent = desc;
        document.getElementById('dashWeatherDesc').className = 'stat-delta';

        // Soil moisture
        const soilArr = d.hourly.soil_moisture_0_to_1cm;
        const latestSoil = soilArr[soilArr.length - 1];
        const soilPct = Math.round(latestSoil * 100);
        document.getElementById('dashSoil').textContent = soilPct + '%';
        const soilEl = document.getElementById('dashSoilStatus');
        soilEl.textContent = soilPct > 30 ? 'Good' : soilPct > 15 ? 'Moderate' : 'Low';
        soilEl.className = 'stat-delta ' + (soilPct > 30 ? 'up' : soilPct > 15 ? '' : 'warn');

        // Weather page — current card
        document.getElementById('weatherCurrent').innerHTML = `
            <div class="weather-current-card">
                <div>
                    <p style="font-size:0.8rem;opacity:0.8;margin-bottom:0.5rem">📍 ${cityName} • Now</p>
                    <p class="wc-temp">${Math.round(c.temperature_2m)}°C</p>
                    <p class="wc-desc">${desc}</p>
                    <div class="wc-details">
                        <div class="wc-detail"><p class="wc-detail-val">${c.relative_humidity_2m}%</p><p class="wc-detail-label">Humidity</p></div>
                        <div class="wc-detail"><p class="wc-detail-val">${c.wind_speed_10m} km/h</p><p class="wc-detail-label">Wind Speed</p></div>
                        <div class="wc-detail"><p class="wc-detail-val">${Math.round(c.apparent_temperature)}°C</p><p class="wc-detail-label">Feels Like</p></div>
                    </div>
                </div>
                <div class="wc-icon">${icon}</div>
            </div>`;

        // 7-day forecast
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        let fg = '';
        for (let i = 0; i < 7; i++) {
            const date = new Date(d.daily.time[i]);
            const dayName = i === 0 ? 'Today' : days[date.getDay()];
            const hi = Math.round(d.daily.temperature_2m_max[i]);
            const lo = Math.round(d.daily.temperature_2m_min[i]);
            const rain = d.daily.precipitation_sum[i];
            const ic = wmoIcon(d.daily.weather_code[i]);
            fg += `<div class="forecast-card" style="animation-delay:${i * 0.06}s">
                <p class="fc-day">${dayName}</p>
                <p class="fc-icon">${ic}</p>
                <p class="fc-temp">${hi}° / ${lo}°</p>
                ${rain > 0 ? `<p class="fc-rain">💧 ${rain.toFixed(1)}mm</p>` : ''}
            </div>`;
        }
        document.getElementById('forecastGrid').innerHTML = fg;

    } catch (err) {
        document.getElementById('weatherCurrent').innerHTML =
            '<p style="color:#ef4444;padding:1rem">❌ Failed to load weather data. Check your internet connection.</p>';
    }
}

// ── MARKET PRICES ───────────────────────────────────────
async function loadMarketPrices() {
    try {
        const r = await fetch(API + '/market-prices');
        const d = await r.json();
        const grid = document.getElementById('marketGrid');
        grid.innerHTML = d.prices.map((p, i) => `
            <div class="market-card" style="animation-delay:${i * 0.05}s"
                 onclick="navigate('chat');setTimeout(()=>askQuestion('What is the current ${p.crop} price and market trend?'),300)">
                <div class="mc-icon">${p.icon}</div>
                <div class="mc-info">
                    <p class="mc-name">${p.crop}</p>
                    <p class="mc-mandi">📍 ${p.mandi}</p>
                </div>
                <div class="mc-right">
                    <p class="mc-price">₹${p.price.toLocaleString('en-IN')}/${p.unit}</p>
                    <p class="mc-change ${p.change >= 0 ? 'up' : 'down'}">${p.change >= 0 ? '↑' : '↓'} ${Math.abs(p.change)}%</p>
                    <canvas class="mc-sparkline" width="80" height="30" id="spark-${i}"></canvas>
                </div>
            </div>
        `).join('');

        // Draw sparklines
        d.prices.forEach((p, i) => {
            const canvas = document.getElementById('spark-' + i);
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const vals = p.history;
            const min = Math.min(...vals), max = Math.max(...vals);
            const range = max - min || 1;
            ctx.strokeStyle = p.change >= 0 ? '#059669' : '#ef4444';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            vals.forEach((v, j) => {
                const x = (j / (vals.length - 1)) * 80;
                const y = 28 - ((v - min) / range) * 26;
                j === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
            });
            ctx.stroke();
        });
    } catch {
        document.getElementById('marketGrid').innerHTML =
            '<p style="color:#ef4444">❌ Failed to load market prices</p>';
    }
}

// ── CROP GUIDE ──────────────────────────────────────────
async function loadCropGuide() {
    try {
        const r = await fetch(API + '/crop-guide');
        const d = await r.json();
        document.getElementById('cropsGrid').innerHTML = d.crops.map((c, i) => `
            <div class="crop-card" style="animation-delay:${i * 0.06}s">
                <div class="cc-header">
                    <span class="cc-icon">${c.icon}</span>
                    <div>
                        <p class="cc-name">${c.name}</p>
                        <span class="cc-season">${c.season}</span>
                    </div>
                </div>
                <div class="cc-details">
                    <p class="cc-det">💧 <strong>${c.water}</strong></p>
                    <p class="cc-det">🌡️ <strong>${c.temp}</strong></p>
                    <p class="cc-det">🏞️ <strong>${c.soil}</strong></p>
                    <p class="cc-det">⏱️ <strong>${c.duration}</strong></p>
                </div>
                <p style="font-size:0.72rem;color:#6b7280;margin-bottom:0.5rem">📍 ${c.states.join(', ')}</p>
                <ul class="cc-tips">${c.tips.map(t => `<li>${t}</li>`).join('')}</ul>
                <button class="pop-chip" style="margin-top:0.75rem;justify-content:center;border-color:#bbf7d0"
                    onclick="navigate('chat');setTimeout(()=>askQuestion('Tell me more about growing ${c.name} in India'),300)">
                    🤖 Ask AI about ${c.name}
                </button>
            </div>
        `).join('');
    } catch {
        document.getElementById('cropsGrid').innerHTML = '<p style="color:#ef4444">❌ Failed to load crop guide</p>';
    }
}

// ── PEST SOLUTIONS ──────────────────────────────────────
async function loadPestSolutions() {
    try {
        const r = await fetch(API + '/pest-solutions');
        const d = await r.json();
        document.getElementById('pestsGrid').innerHTML = d.pests.map((p, i) => `
            <div class="pest-card" style="animation-delay:${i * 0.06}s">
                <div class="pc-header">
                    <span style="font-size:1.5rem">${p.icon}</span>
                    <div style="flex:1">
                        <p class="pc-name">${p.name}</p>
                        <p class="pc-crops">Affects: ${p.crops.join(', ')}</p>
                    </div>
                    <span class="pc-severity sev-${p.severity}">${p.severity}</span>
                </div>
                <div class="pc-symptoms">⚠️ ${p.symptoms}</div>
                <ul class="pc-solutions">${p.solutions.map(s =>
            `<li><span class="sol-type sol-${s.type}">${s.type}</span> ${s.method}</li>`
        ).join('')}</ul>
                <button class="pop-chip" style="margin-top:0.75rem;justify-content:center;border-color:#fde68a"
                    onclick="navigate('chat');setTimeout(()=>askQuestion('How to control ${p.name} in my crop?'),300)">
                    🤖 Ask AI about ${p.name}
                </button>
            </div>
        `).join('');
    } catch {
        document.getElementById('pestsGrid').innerHTML = '<p style="color:#ef4444">❌ Failed to load pest solutions</p>';
    }
}

// ── POPULAR QUESTIONS ───────────────────────────────────
async function loadPopularQuestions() {
    try {
        const r = await fetch(API + '/popular');
        const d = await r.json();

        // Right panel (chat page)
        const rp = document.getElementById('popularQuestions');
        rp.innerHTML = d.categories.flatMap(c =>
            c.questions.slice(0, 2).map(q =>
                `<button class="rp-chip" onclick="askQuestion('${esc(q)}')">${c.icon} ${q}</button>`
            )
        ).join('');

        // Dashboard popular grid
        const dp = document.getElementById('dashPopular');
        dp.innerHTML = d.categories.flatMap(c =>
            c.questions.slice(0, 1).map(q =>
                `<button class="pop-chip" onclick="navigate('chat');setTimeout(()=>askQuestion('${esc(q)}'),200)">${c.icon} ${q}</button>`
            )
        ).join('');
    } catch { }
}

// ── CHAT ────────────────────────────────────────────────
function askFromGlobal(val) {
    if (!val || !val.trim()) return;
    document.getElementById('globalSearch').value = '';
    navigate('chat');
    setTimeout(() => askQuestion(val.trim()), 200);
}

function askQuestion(q) {
    document.getElementById('chatInput').value = '';
    processQuery(q);
}

function sendChat() {
    const input = document.getElementById('chatInput');
    const q = input.value.trim();
    if (!q) return;
    input.value = '';
    processQuery(q);
}

async function processQuery(query) {
    const chat = document.getElementById('chatArea');
    const welcome = chat.querySelector('.chat-welcome');
    if (welcome) welcome.remove();

    addBubble('user', query);
    const typingEl = showTyping();

    try {
        const r = await fetch(API + '/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, online_mode: onlineMode, top_k: 5 })
        });
        const d = await r.json();
        typingEl.remove();

        if (d.error) { addBubble('ai', '❌ ' + d.error); return; }

        let answer = d.online_answer || d.offline_answer || 'No relevant results found. Try rephrasing your question.';
        let meta = '';
        if (d.results && d.results.length > 0) {
            const top = d.results[0];
            const crops = [...new Set(d.results.map(r => r.crop).filter(Boolean))];
            meta = `<div class="bubble-meta">
                <span class="meta-tag conf">✅ ${top.confidence}% match</span>
                ${crops.length ? `<span class="meta-tag info">🌱 ${crops.join(', ')}</span>` : ''}
                <span class="meta-tag info">⏱️ ${d.elapsed}s</span>
            </div>`;
        }
        addBubble('ai', formatMarkdown(answer) + meta);

        history.unshift({ query, time: new Date() });
        updateHistory();
    } catch {
        typingEl.remove();
        addBubble('ai', '❌ Cannot connect to API. Make sure <code>python api_server.py</code> is running.');
    }
}

function addBubble(type, content) {
    const chat = document.getElementById('chatArea');
    const time = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    const div = document.createElement('div');
    div.className = 'bubble-row ' + type;

    if (type === 'user') {
        div.innerHTML = `<div><div class="bubble user-b">${escapeHtml(content)}</div><p class="bubble-time">${time}</p></div>`;
    } else {
        div.innerHTML = `<div class="bubble-avatar">🌾</div><div><div class="bubble ai-b">${content}</div><p class="bubble-time">${time} • IBM Watsonx Granite</p></div>`;
    }
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

function showTyping() {
    const chat = document.getElementById('chatArea');
    const div = document.createElement('div');
    div.className = 'bubble-row ai';
    div.innerHTML = `<div class="bubble-avatar">🌾</div><div class="bubble ai-b"><div class="typing-dots"><span></span><span></span><span></span></div></div>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
}

function updateHistory() {
    const el = document.getElementById('historyList');
    if (!history.length) { el.innerHTML = '<p class="rp-empty">No queries yet</p>'; return; }
    el.innerHTML = history.slice(0, 6).map(h =>
        `<button class="rp-chip" onclick="askQuestion('${esc(h.query)}')">🕐 ${escapeHtml(h.query.substring(0, 50))}</button>`
    ).join('');
}

// ── HELPERS ─────────────────────────────────────────────
function escapeHtml(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }
function esc(s) { return s.replace(/'/g, "\\'").replace(/"/g, '&quot;'); }

function formatMarkdown(text) {
    return text
        .replace(/### (.*)/g, '<strong style="display:block;margin:0.6rem 0 0.3rem;font-size:0.9rem">$1</strong>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\* /g, '<br>• ')
        .replace(/\n- /g, '<br>• ')
        .replace(/\n\d+\. /g, (m) => '<br>' + m.trim() + ' ')
        .replace(/\n/g, '<br>')
        .replace(/`(.*?)`/g, '<code style="background:#f3f4f6;padding:1px 4px;border-radius:4px;font-size:0.8rem">$1</code>');
}
