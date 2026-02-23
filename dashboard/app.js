/* ═══════════════════════════════════════════════════════
   KrishiMind AI — Dashboard Application Logic v2
   Bento grid, real-time data, charts, gauges, calendar
   ═══════════════════════════════════════════════════════ */

const API = window.KRISHI_API_URL || window.location.origin + '/api';
const WEATHER_API = 'https://api.open-meteo.com/v1/forecast';
let onlineMode = navigator.onLine; // auto-detect internet on load
let isInternetAvailable = navigator.onLine;
let history = [];
let weatherData = null;  // cached for chart + hero

// ── INTERNET CONNECTIVITY DETECTION ──────────────────────
function showToast(msg, type = 'info') {
    const t = document.createElement('div');
    t.className = 'krishi-toast ' + type;
    t.textContent = msg;
    t.style.cssText = `position:fixed;top:20px;right:20px;z-index:10000;
        padding:12px 20px;border-radius:12px;font-size:0.85rem;font-weight:600;
        box-shadow:0 8px 24px rgba(0,0,0,0.15);transition:all 0.4s ease;
        opacity:0;transform:translateY(-10px);`;
    if (type === 'offline') {
        t.style.background = '#fef2f2'; t.style.color = '#dc2626'; t.style.border = '1px solid #fca5a5';
    } else if (type === 'online') {
        t.style.background = '#f0fdf4'; t.style.color = '#16a34a'; t.style.border = '1px solid #86efac';
    }
    document.body.appendChild(t);
    requestAnimationFrame(() => { t.style.opacity = '1'; t.style.transform = 'translateY(0)'; });
    setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 400); }, 3500);
}

window.addEventListener('offline', () => {
    isInternetAvailable = false;
    if (onlineMode) {
        onlineMode = false;
        updateModeUI();
    }
    const lang = document.getElementById('langSelect')?.value || 'en';
    const msg = lang === 'hi' ? '📴 इंटरनेट कनेक्शन खो गया — ऑफलाइन मोड' :
        lang === 'te' ? '📴 ఇంటర్నెట్ కనెక్షన్ పోయింది — ఆఫ్‌లైన్ మోడ్' :
            '📴 Internet disconnected — Switched to Offline mode';
    showToast(msg, 'offline');
});

window.addEventListener('online', () => {
    isInternetAvailable = true;
    onlineMode = true;
    updateModeUI();
    const lang = document.getElementById('langSelect')?.value || 'en';
    const msg = lang === 'hi' ? '🌐 इंटरनेट वापस आ गया — ऑनलाइन मोड' :
        lang === 'te' ? '🌐 ఇంటర్నెట్ తిరిగి వచ్చింది — ఆన్‌లైన్ మోడ్' :
            '🌐 Internet restored — Back Online!';
    showToast(msg, 'online');
    // Reload weather and market data
    loadWeather();
    loadMarketTicker();
});

function updateModeUI() {
    const btn = document.getElementById('modeBtn');
    const text = document.getElementById('modeText');
    if (!btn || !text) return;
    btn.className = 'mode-btn ' + (onlineMode ? 'online' : 'offline');
    const lang = document.getElementById('langSelect')?.value || 'en';
    const labels = {
        en: ['Online', 'Offline'],
        hi: ['ऑनलाइन', 'ऑफलाइन'],
        te: ['ఆన్‌లైన్', 'ఆఫ్‌లైన్']
    };
    const [on, off] = labels[lang] || labels.en;
    text.textContent = onlineMode ? on : off;
}

// Weather code → emoji + description
const WMO = {
    0: '☀️ Clear', 1: '🌤️ Mostly Clear', 2: '⛅ Partly Cloudy', 3: '☁️ Overcast',
    45: '🌫️ Fog', 48: '🌫️ Rime Fog', 51: '🌦️ Light Drizzle', 53: '🌧️ Drizzle',
    55: '🌧️ Heavy Drizzle', 61: '🌧️ Light Rain', 63: '🌧️ Rain', 65: '🌧️ Heavy Rain',
    71: '🌨️ Light Snow', 73: '🌨️ Snow', 75: '🌨️ Heavy Snow', 80: '🌦️ Showers',
    81: '🌧️ Heavy Showers', 82: '⛈️ Violent Showers', 95: '⛈️ Thunderstorm',
    96: '⛈️ Hail Storm', 99: '⛈️ Heavy Hail'
};

// ── i18n TRANSLATIONS ────────────────────────────────────
const TRANSLATIONS = {
    en: {
        // Sidebar nav
        nav_dashboard: 'Dashboard',
        nav_ask_ai: 'Ask AI',
        nav_online: 'Online',
        nav_weather: 'Weather',
        nav_market: 'Market Prices',
        nav_crops: 'Crop Guide',
        nav_pests: 'Pest Solutions',
        // Header
        search_placeholder: 'Ask anything about farming...',
        select_location: 'Select Location',
        btn_ask: 'Ask',
        // Hero
        hero_greeting: 'Good Evening',
        hero_welcome: 'Welcome back, Farmer! 👋',
        hero_sub: 'Your smart farming assistant is ready',
        // Bento cards
        wheat_price: 'Wheat Price',
        weather: 'Weather',
        soil_health: 'Soil Health',
        moisture: 'Moisture',
        ai_daily_tip: 'AI Daily Tip',
        powered_by: 'Powered by KrishiMind AI',
        ask_more: 'Ask more →',
        seven_day_temp: '📈 7-Day Temperature',
        market_prices_top: '💰 Market Prices — Top Crops',
        view_all: 'View all →',
        // Quick actions
        quick_actions: '⚡ Quick Actions',
        qa_crop: 'Crop Advice',
        qa_crop_sub: 'AI recommendation',
        qa_pest: 'Pest Check',
        qa_pest_sub: 'Identify & treat',
        qa_weather: 'Weather',
        qa_weather_sub: '7-day forecast',
        qa_market: 'Market',
        qa_market_sub: 'Live mandi rates',
        // Sections
        popular_questions: '🔥 Popular Questions',
        activity_feed: '📝 Activity Feed',
        recent_history: '🕐 Recent History',
        // Chat page
        chat_welcome: 'Welcome to KrishiMind AI',
        chat_welcome_sub: 'Ask any farming question — crop advice, pest control, weather, market prices',
        chat_placeholder: 'Type your farming question...',
        // Weather page
        weather_title: '🌤️ Weather Forecast',
        weather_sub: 'Real-time weather data for your region',
        seven_day_forecast: '📅 7-Day Forecast',
        // Market page
        market_title: '💰 Market Prices',
        market_sub: 'Live mandi rates from across India',
        // Crop page
        crop_title: '🌱 Crop Guide',
        crop_sub: 'Complete growing guide for major Indian crops',
        // Pest page
        pest_title: '🐛 Pest Solutions',
        pest_sub: 'Identify and treat common crop pests and diseases',
        // Location modal
        loc_title: '📍 Select Your Location',
        loc_sub: 'Choose your nearest city for accurate weather, market prices, and AI advice',
    },
    hi: {
        nav_dashboard: 'डैशबोर्ड',
        nav_ask_ai: 'AI से पूछें',
        nav_online: 'ऑनलाइन',
        nav_weather: 'मौसम',
        nav_market: 'मंडी भाव',
        nav_crops: 'फसल गाइड',
        nav_pests: 'कीट समाधान',
        search_placeholder: 'खेती के बारे में कुछ भी पूछें...',
        select_location: 'स्थान चुनें',
        btn_ask: 'पूछें',
        hero_greeting: 'नमस्ते',
        hero_welcome: 'स्वागत है, किसान भाई! 👋',
        hero_sub: 'आपका स्मार्ट कृषि सहायक तैयार है',
        wheat_price: 'गेहूं का भाव',
        weather: 'मौसम',
        soil_health: 'मिट्टी स्वास्थ्य',
        moisture: 'नमी',
        ai_daily_tip: 'AI दैनिक सुझाव',
        powered_by: 'KrishiMind AI द्वारा संचालित',
        ask_more: 'और पूछें →',
        seven_day_temp: '📈 7-दिन का तापमान',
        market_prices_top: '💰 मंडी भाव — प्रमुख फसलें',
        view_all: 'सभी देखें →',
        quick_actions: '⚡ त्वरित कार्य',
        qa_crop: 'फसल सलाह',
        qa_crop_sub: 'AI अनुशंसा',
        qa_pest: 'कीट जाँच',
        qa_pest_sub: 'पहचानें और उपचार करें',
        qa_weather: 'मौसम',
        qa_weather_sub: '7-दिन का पूर्वानुमान',
        qa_market: 'मंडी',
        qa_market_sub: 'लाइव मंडी भाव',
        popular_questions: '🔥 लोकप्रिय प्रश्न',
        activity_feed: '📝 गतिविधि फ़ीड',
        recent_history: '🕐 हाल का इतिहास',
        chat_welcome: 'KrishiMind AI में आपका स्वागत है',
        chat_welcome_sub: 'कोई भी खेती का सवाल पूछें — फसल सलाह, कीट नियंत्रण, मौसम, मंडी भाव',
        chat_placeholder: 'अपना खेती का सवाल लिखें...',
        weather_title: '🌤️ मौसम पूर्वानुमान',
        weather_sub: 'आपके क्षेत्र का रीयल-टाइम मौसम डेटा',
        seven_day_forecast: '📅 7-दिन का पूर्वानुमान',
        market_title: '💰 मंडी भाव',
        market_sub: 'भारत भर की लाइव मंडी दरें',
        crop_title: '🌱 फसल गाइड',
        crop_sub: 'प्रमुख भारतीय फसलों की पूरी उगाई गाइड',
        pest_title: '🐛 कीट समाधान',
        pest_sub: 'सामान्य फसल कीट और रोगों की पहचान और उपचार',
        loc_title: '📍 अपना स्थान चुनें',
        loc_sub: 'सटीक मौसम, मंडी भाव और AI सलाह के लिए अपना निकटतम शहर चुनें',
    },
    te: {
        nav_dashboard: 'డ్యాష్‌బోర్డ్',
        nav_ask_ai: 'AI ని అడగండి',
        nav_online: 'ఆన్‌లైన్',
        nav_weather: 'వాతావరణం',
        nav_market: 'మార్కెట్ ధరలు',
        nav_crops: 'పంట గైడ్',
        nav_pests: 'పురుగుల పరిష్కారాలు',
        search_placeholder: 'వ్యవసాయం గురించి ఏదైనా అడగండి...',
        select_location: 'ప్రదేశాన్ని ఎంచుకోండి',
        btn_ask: 'అడగండి',
        hero_greeting: 'నమస్కారం',
        hero_welcome: 'తిరిగి స్వాగతం, రైతు! 👋',
        hero_sub: 'మీ స్మార్ట్ వ్యవసాయ సహాయకుడు సిద్ధంగా ఉన్నాడు',
        wheat_price: 'గోధుమ ధర',
        weather: 'వాతావరణం',
        soil_health: 'నేల ఆరోగ్యం',
        moisture: 'తేమ',
        ai_daily_tip: 'AI రోజువారీ చిట్కా',
        powered_by: 'KrishiMind AI ద్వారా నడుస్తుంది',
        ask_more: 'మరింత అడగండి →',
        seven_day_temp: '📈 7-రోజుల ఉష్ణోగ్రత',
        market_prices_top: '💰 మార్కెట్ ధరలు — ప్రధాన పంటలు',
        view_all: 'అన్నీ చూడండి →',
        quick_actions: '⚡ త్వరిత చర్యలు',
        qa_crop: 'పంట సలహా',
        qa_crop_sub: 'AI సిఫార్సు',
        qa_pest: 'పురుగుల తనిఖీ',
        qa_pest_sub: 'గుర్తించి చికిత్స చేయండి',
        qa_weather: 'వాతావరణం',
        qa_weather_sub: '7-రోజుల అంచనా',
        qa_market: 'మార్కెట్',
        qa_market_sub: 'లైవ్ మార్కెట్ ధరలు',
        popular_questions: '🔥 జనాదరణ పొందిన ప్రశ్నలు',
        activity_feed: '📝 కార్యకలాపాల ఫీడ్',
        recent_history: '🕐 ఇటీవలి చరిత్ర',
        chat_welcome: 'KrishiMind AI కి స్వాగతం',
        chat_welcome_sub: 'ఏదైనా వ్యవసాయ ప్రశ్న అడగండి — పంట సలహా, పురుగుల నియంత్రణ, వాతావరణం, మార్కెట్ ధరలు',
        chat_placeholder: 'మీ వ్యవసాయ ప్రశ్నను టైప్ చేయండి...',
        weather_title: '🌤️ వాతావరణ అంచనా',
        weather_sub: 'మీ ప్రాంతానికి రియల్-టైమ్ వాతావరణ డేటా',
        seven_day_forecast: '📅 7-రోజుల అంచనా',
        market_title: '💰 మార్కెట్ ధరలు',
        market_sub: 'భారతదేశం అంతటా లైవ్ మండి ధరలు',
        crop_title: '🌱 పంట గైడ్',
        crop_sub: 'ప్రధాన భారతీయ పంటల పూర్తి పెంపకం గైడ్',
        pest_title: '🐛 పురుగుల పరిష్కారాలు',
        pest_sub: 'సాధారణ పంట తెగుళ్ళు మరియు వ్యాధులను గుర్తించి చికిత్స చేయండి',
        loc_title: '📍 మీ ప్రదేశాన్ని ఎంచుకోండి',
        loc_sub: 'ఖచ్చితమైన వాతావరణం, మార్కెట్ ధరలు మరియు AI సలహా కోసం మీ సమీప నగరాన్ని ఎంచుకోండి',
    }
};

function getCurrentLang() {
    return document.getElementById('langSelect')?.value || localStorage.getItem('krishi_lang') || 'en';
}

function applyLanguage(lang) {
    const dict = TRANSLATIONS[lang] || TRANSLATIONS['en'];
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) el.textContent = dict[key];
    });
    // Update placeholders
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
        const key = el.getAttribute('data-i18n-ph');
        if (dict[key]) el.placeholder = dict[key];
    });
    // Set HTML lang attribute
    document.documentElement.lang = lang;

    // Re-render all dynamic content with new language
    initHeroBanner();
    loadCropCalendar();
    loadPopularQuestions();
    loadAIDailyTip();

    // Reset lazy-loaded sub-page flags so they re-fetch with correct language
    if (typeof marketLoaded !== 'undefined') { marketLoaded = false; }
    if (typeof cropsLoaded !== 'undefined') { cropsLoaded = false; }
    if (typeof pestsLoaded !== 'undefined') { pestsLoaded = false; }

    // If sub-pages are currently visible, reload them immediately
    const activePage = document.querySelector('.page.active');
    if (activePage) {
        const pageId = activePage.id;
        if (pageId === 'page-crops') loadCropGuide();
        if (pageId === 'page-pests') loadPestSolutions();
        if (pageId === 'page-market') loadMarketPrices();
    }
}
function wmoIcon(code) { return (WMO[code] || '🌤️ Unknown').split(' ')[0]; }
function wmoDesc(code) { return (WMO[code] || 'Unknown').split(' ').slice(1).join(' '); }

// ── GLOBAL LOCATION SYSTEM ──────────────────────────────
// Auto-detects via GPS on first visit, stored in localStorage
let userLocation = JSON.parse(localStorage.getItem('krishimind_location') || 'null');
// { name: "Amravati", lat: "20.9320", lon: "77.7523" }

// All known cities with coords for nearest-match
const KNOWN_CITIES = [
    { name: 'Amravati', lat: 20.9320, lon: 77.7523, state: 'Maharashtra' },
    { name: 'Nagpur', lat: 21.1458, lon: 79.0882, state: 'Maharashtra' },
    { name: 'Mumbai', lat: 19.0760, lon: 72.8777, state: 'Maharashtra' },
    { name: 'Pune', lat: 18.5204, lon: 73.8567, state: 'Maharashtra' },
    { name: 'Nashik', lat: 19.9975, lon: 73.7898, state: 'Maharashtra' },
    { name: 'Aurangabad', lat: 19.8762, lon: 75.3433, state: 'Maharashtra' },
    { name: 'Kolhapur', lat: 16.7050, lon: 74.2433, state: 'Maharashtra' },
    { name: 'Solapur', lat: 17.6599, lon: 75.9064, state: 'Maharashtra' },
    { name: 'Delhi', lat: 28.6139, lon: 77.2090, state: 'Delhi' },
    { name: 'Lucknow', lat: 26.8467, lon: 80.9462, state: 'Uttar Pradesh' },
    { name: 'Jaipur', lat: 26.9124, lon: 75.7873, state: 'Rajasthan' },
    { name: 'Chandigarh', lat: 30.7333, lon: 76.7794, state: 'Punjab' },
    { name: 'Varanasi', lat: 25.3176, lon: 82.9739, state: 'Uttar Pradesh' },
    { name: 'Bhopal', lat: 23.2599, lon: 77.4126, state: 'Madhya Pradesh' },
    { name: 'Indore', lat: 22.7196, lon: 75.8577, state: 'Madhya Pradesh' },
    { name: 'Agra', lat: 27.1767, lon: 78.0081, state: 'Uttar Pradesh' },
    { name: 'Bangalore', lat: 12.9716, lon: 77.5946, state: 'Karnataka' },
    { name: 'Chennai', lat: 13.0827, lon: 80.2707, state: 'Tamil Nadu' },
    { name: 'Hyderabad', lat: 17.3850, lon: 78.4867, state: 'Telangana' },
    { name: 'Kochi', lat: 9.9312, lon: 76.2673, state: 'Kerala' },
    { name: 'Kolkata', lat: 22.5726, lon: 88.3639, state: 'West Bengal' },
    { name: 'Patna', lat: 25.6093, lon: 85.1376, state: 'Bihar' },
    { name: 'Ranchi', lat: 23.3441, lon: 85.3096, state: 'Jharkhand' },
    { name: 'Ahmedabad', lat: 23.0225, lon: 72.5714, state: 'Gujarat' },
    { name: 'Rajkot', lat: 22.3039, lon: 70.8022, state: 'Gujarat' },
    { name: 'Raipur', lat: 21.2514, lon: 81.6296, state: 'Chhattisgarh' },
    { name: 'Ludhiana', lat: 30.9010, lon: 75.8573, state: 'Punjab' },
    { name: 'Karnal', lat: 29.6857, lon: 76.9905, state: 'Haryana' },
    { name: 'Amritsar', lat: 31.6340, lon: 74.8723, state: 'Punjab' },
    // Andhra Pradesh
    { name: 'Vijayawada', lat: 16.5062, lon: 80.6480, state: 'Andhra Pradesh' },
    { name: 'Visakhapatnam', lat: 17.6868, lon: 83.2185, state: 'Andhra Pradesh' },
    { name: 'Guntur', lat: 16.3067, lon: 80.4365, state: 'Andhra Pradesh' },
    { name: 'Nellore', lat: 14.4426, lon: 79.9865, state: 'Andhra Pradesh' },
];

function getLocationName() {
    return userLocation ? userLocation.name : 'India';
}
function getLocationState() {
    return userLocation ? (userLocation.state || '') : '';
}
function getLocationCoords() {
    return userLocation ? { lat: userLocation.lat, lon: userLocation.lon } : { lat: '20.5937', lon: '78.9629' };
}
function getFullTimestamp() {
    const now = new Date();
    const date = now.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    const time = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    return `${date}, ${time}`;
}

// Find nearest known city to given GPS coordinates
function findNearestCity(lat, lon) {
    let nearest = KNOWN_CITIES[0], minDist = Infinity;
    KNOWN_CITIES.forEach(city => {
        const d = Math.sqrt(Math.pow(city.lat - lat, 2) + Math.pow(city.lon - lon, 2));
        if (d < minDist) { minDist = d; nearest = city; }
    });
    return nearest;
}

// Auto-detect location using browser GPS + reverse geocoding
async function autoDetectLocation() {
    const badge = document.getElementById('locationBadgeText');
    if (badge) badge.textContent = '📡 Detecting...';

    try {
        const pos = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: false, timeout: 8000, maximumAge: 300000
            });
        });

        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        // Try reverse geocoding with Nominatim (free, no key)
        let cityName = null;
        try {
            const res = await fetch(
                `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&zoom=10`,
                { headers: { 'User-Agent': 'KrishiMindAI/1.0' } }
            );
            const geo = await res.json();
            cityName = geo.address?.city || geo.address?.town || geo.address?.county || geo.address?.state_district;
        } catch { /* Nominatim failed, will use nearest match */ }

        // Find nearest known city
        const nearest = findNearestCity(lat, lon);

        // Use geocoded name if available, otherwise nearest city name
        const finalName = cityName || nearest.name;

        setLocationSilently(finalName, String(lat), String(lon), nearest.state || '');
        addFeedItem(`📍 Location auto-detected: ${finalName}`, 'dot-blue');

    } catch (err) {
        // GPS denied or failed — default to Delhi silently
        console.log('Geolocation unavailable:', err.message);
        const fallback = KNOWN_CITIES.find(c => c.name === 'Delhi') || KNOWN_CITIES[0];
        setLocationSilently(fallback.name, String(fallback.lat), String(fallback.lon), fallback.state || '');
        addFeedItem(`📍 Using default location: ${fallback.name}`, 'dot-blue');
    }
}

// Set location without opening/closing the modal
function setLocationSilently(name, lat, lon, state) {
    userLocation = { name, lat, lon, state: state || '' };
    localStorage.setItem('krishimind_location', JSON.stringify(userLocation));
    updateLocationUI();
    // Reload widgets with new location
    loadWeather();
    loadAIDailyTip();
    loadMarketTicker();
    loadPricePrediction(document.getElementById('predCropSelect')?.value || 'Wheat');
    loadPriceAdvisory();
    initHeroBanner();
}

// Show location picker only when user CLICKS the badge
function showLocationPicker() {
    document.getElementById('locationModal').classList.add('active');
    document.getElementById('locSearch').value = '';
    setTimeout(() => document.getElementById('locSearch').focus(), 100);
    filterLocations('');
    // Highlight current selection
    document.querySelectorAll('.loc-btn').forEach(btn => {
        btn.classList.toggle('selected', userLocation && btn.textContent.trim() === userLocation.name);
    });
}

function selectLocation(name, lat, lon) {
    const cityData = KNOWN_CITIES.find(c => c.name === name) || {};
    userLocation = { name, lat, lon, state: cityData.state || '' };
    localStorage.setItem('krishimind_location', JSON.stringify(userLocation));
    document.getElementById('locationModal').classList.remove('active');
    updateLocationUI();
    // Reload all location-dependent data
    loadWeather();
    loadAIDailyTip();
    loadMarketTicker();
    loadPricePrediction(document.getElementById('predCropSelect')?.value || 'Wheat');
    loadPriceAdvisory();
    initHeroBanner();
    addFeedItem(`📍 Location changed to ${name} (${cityData.state || 'India'})`, 'dot-blue');
}

function filterLocations(q) {
    const lower = q.toLowerCase();
    document.querySelectorAll('#locGrid .loc-btn').forEach(btn => {
        btn.style.display = btn.textContent.toLowerCase().includes(lower) ? '' : 'none';
    });
    document.querySelectorAll('#locGrid .loc-region').forEach(region => {
        let next = region.nextElementSibling;
        let anyVisible = false;
        while (next && !next.classList.contains('loc-region')) {
            if (next.classList.contains('loc-btn') && next.style.display !== 'none') anyVisible = true;
            next = next.nextElementSibling;
        }
        region.style.display = anyVisible ? '' : 'none';
    });
}

function updateLocationUI() {
    const badge = document.getElementById('locationBadgeText');
    if (badge) badge.textContent = userLocation ? userLocation.name : 'Detecting...';

    // Sync the weather page dropdown if it exists
    const sel = document.getElementById('weatherCity');
    if (sel && userLocation) {
        for (let opt of sel.options) {
            if (opt.text === userLocation.name) { sel.value = opt.value; break; }
        }
    }

    // Sync the Prediction page State dropdown if it exists
    const stateSel = document.getElementById('predStateSelect');
    if (stateSel && userLocation && userLocation.state) {
        stateSel.value = userLocation.state;
    }
}

// When user changes city from weather page dropdown → update global location
function selectLocationFromDropdown(sel) {
    const [lat, lon] = sel.value.split(',');
    const name = sel.options[sel.selectedIndex].text;
    selectLocation(name, lat, lon);
}

// ── AUTHENTICATION ──────────────────────────────────────
async function checkAuth() {
    try {
        const r = await fetch(API + '/auth/me');
        if (r.status === 401) {
            window.location.href = '/login';
            return;
        }
        const user = await r.json();
        if (user.authenticated) {
            document.querySelector('.user-name').textContent = user.full_name || user.username;
            document.querySelector('.user-role').innerHTML = `<span style="color:#059669;font-weight:700">● Online</span>`;
        }
    } catch { /* stay silent on error */ }
}

async function logout() {
    await fetch(API + '/auth/logout', { method: 'POST' });
    window.location.href = '/login';
}

// ── INIT ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();

    // Language — restore saved preference and apply
    const ls = document.getElementById('langSelect');
    if (ls) {
        const savedLang = localStorage.getItem('krishi_lang') || 'en';
        ls.value = savedLang;
        applyLanguage(savedLang);
        ls.addEventListener('change', (e) => {
            localStorage.setItem('krishi_lang', e.target.value);
            applyLanguage(e.target.value);
        });
    }

    if (!userLocation) {
        // First visit → auto-detect via GPS (browser asks permission)
        autoDetectLocation();
    } else {
        updateLocationUI();
    }

    // All init calls in parallel for speed
    initHeroBanner();
    loadWeather();
    loadPopularQuestions();
    loadMarketTicker();
    loadCropCalendar();
    loadAIDailyTip();
    checkHealth();

    // Close modal on overlay click (only if location already set)
    document.getElementById('locationModal').addEventListener('click', (e) => {
        if (e.target.classList.contains('loc-modal-overlay') && userLocation) {
            e.target.classList.remove('active');
        }
    });
});

// ── HERO BANNER ─────────────────────────────────────────
function initHeroBanner() {
    const lang = getCurrentLang();
    const h = new Date().getHours();

    const greetingTexts = {
        en: h < 5 ? 'Good Night 🌙' : h < 12 ? 'Good Morning ☀️' : h < 17 ? 'Good Afternoon 🌤️' : 'Good Evening 🌇',
        hi: h < 5 ? 'शुभ रात्रि 🌙' : h < 12 ? 'सुप्रभात ☀️' : h < 17 ? 'शुभ दोपहर 🌤️' : 'शुभ संध्या 🌇',
        te: h < 5 ? 'శుభ రాత్రి 🌙' : h < 12 ? 'శుభోదయం ☀️' : h < 17 ? 'శుభ మధ్యాహ్నం 🌤️' : 'శుభ సాయంత్రం 🌇',
    };
    document.getElementById('heroGreeting').textContent = greetingTexts[lang] || greetingTexts.en;

    const loc = getLocationName();
    const now = new Date();
    const localeMap = { en: 'en-IN', hi: 'hi-IN', te: 'te-IN' };
    const locale = localeMap[lang] || 'en-IN';
    const dateStr = now.toLocaleDateString(locale, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    const timeStr = now.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' });
    document.getElementById('heroDate').innerHTML = `<div>📍 ${loc}</div><div>${dateStr}</div><div style="font-weight:700;font-size:1.1em">${timeStr}</div>`;

    // Rabi/Kharif season — multilingual
    const month = now.getMonth() + 1;
    let subtext;
    const seasonTexts = {
        en: {
            rabi: `📍 ${loc} • Rabi season — Wheat, Mustard, Barley growing`,
            kharif: `📍 ${loc} • Kharif season — Rice, Maize, Cotton growing`,
            zaid: `📍 ${loc} • Zaid season — Watermelon, Cucumber, Moong growing`,
        },
        hi: {
            rabi: `📍 ${loc} • रबी मौसम — गेहूं, सरसों, जौ की खेती`,
            kharif: `📍 ${loc} • खरीफ मौसम — चावल, मक्का, कपास की खेती`,
            zaid: `📍 ${loc} • जायद मौसम — तरबूज, खीरा, मूंग की खेती`,
        },
        te: {
            rabi: `📍 ${loc} • రబీ కాలం — గోధుమ, ఆవాలు, బార్లీ పెరుగుతున్నాయి`,
            kharif: `📍 ${loc} • ఖరీఫ్ కాలం — వరి, మొక్కజొన్న, పత్తి పెరుగుతున్నాయి`,
            zaid: `📍 ${loc} • జైద్ కాలం — పుచ్చకాయ, దోసకాయ, పెసలు పెరుగుతున్నాయి`,
        }
    };
    const st = seasonTexts[lang] || seasonTexts.en;
    if (month >= 10 || month <= 3) { subtext = st.rabi; }
    else if (month >= 6 && month <= 9) { subtext = st.kharif; }
    else { subtext = st.zaid; }
    document.getElementById('heroSub').textContent = subtext;
}

// ── NAVIGATION ──────────────────────────────────────────
function navigate(page, el) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const target = document.getElementById('page-' + page);
    if (target) target.classList.add('active');

    if (el) {
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
    } else {
        document.querySelectorAll('.nav-item').forEach(n => {
            n.classList.toggle('active', n.dataset.page === page);
        });
    }
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('active');
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
}

// ── ONLINE/OFFLINE ──────────────────────────────────────
function toggleOnline() {
    // If no internet, prevent switching to online
    if (!isInternetAvailable && !onlineMode) {
        const lang = document.getElementById('langSelect')?.value || 'en';
        const msg = lang === 'hi' ? '📴 इंटरनेट नहीं है — ऑनलाइन मोड उपलब्ध नहीं' :
            lang === 'te' ? '📴 ఇంటర్నెట్ లేదు — ఆన్‌లైన్ మోడ్ అందుబాటులో లేదు' :
                '📴 No internet — Online mode unavailable';
        showToast(msg, 'offline');
        return;
    }
    onlineMode = !onlineMode;
    updateModeUI();
}

async function checkHealth() {
    try {
        const r = await fetch(API + '/health');
        const d = await r.json();
        if (!d.ai_ready && isInternetAvailable) {
            // AI not ready but internet available — still keep online for weather etc.
        } else if (!d.ai_ready) {
            onlineMode = false;
            updateModeUI();
        }
    } catch {
        // Cannot reach localhost API
        onlineMode = false;
        updateModeUI();
    }
}

// ── WEATHER (Real-time Open-Meteo) ──────────────────────
async function loadWeather() {
    // Use global location, fallback to dropdown
    const coords = getLocationCoords();
    const lat = coords.lat;
    const lon = coords.lon;
    const cityName = getLocationName();

    try {
        const url = `${WEATHER_API}?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,apparent_temperature&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code&hourly=soil_moisture_0_to_1cm&timezone=Asia/Kolkata&forecast_days=7`;
        const r = await fetch(url);
        const d = await r.json();
        weatherData = d; // cache for chart

        const c = d.current;
        const icon = wmoIcon(c.weather_code);
        const desc = wmoDesc(c.weather_code);

        // Dashboard stat cards
        document.getElementById('dashTemp').textContent = Math.round(c.temperature_2m) + '°C';
        document.getElementById('dashWeatherDesc').textContent = desc;

        // Hero weather mini
        document.getElementById('heroTemp').textContent = Math.round(c.temperature_2m) + '°';
        document.getElementById('heroWicon').textContent = icon;

        // Mini forecast (3 days in weather card)
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        let mf = '';
        for (let i = 1; i <= 3; i++) {
            const date = new Date(d.daily.time[i]);
            mf += `<div class="mf-day">
                <span>${days[date.getDay()]}</span>
                <span class="mf-icon">${wmoIcon(d.daily.weather_code[i])}</span>
                <span class="mf-temp">${Math.round(d.daily.temperature_2m_max[i])}°</span>
            </div>`;
        }
        document.getElementById('miniForecast').innerHTML = mf;

        // Soil moisture gauge
        const soilArr = d.hourly.soil_moisture_0_to_1cm;
        const latestSoil = soilArr[soilArr.length - 1];
        const soilPct = Math.round(latestSoil * 100);
        document.getElementById('dashSoilVal').textContent = soilPct + '%';
        const soilStatus = document.getElementById('dashSoilStatus');
        soilStatus.textContent = soilPct > 30 ? 'Good' : soilPct > 15 ? 'Moderate' : 'Low';
        soilStatus.className = 'stat-delta ' + (soilPct > 30 ? 'up' : soilPct > 15 ? '' : 'warn');

        // Animate gauge ring
        const circumference = 2 * Math.PI * 34; // r=34
        const offset = circumference - (soilPct / 100) * circumference;
        const gaugeCircle = document.getElementById('soilGaugeCircle');
        gaugeCircle.style.stroke = soilPct > 30 ? '#22c55e' : soilPct > 15 ? '#f59e0b' : '#ef4444';
        setTimeout(() => { gaugeCircle.style.strokeDashoffset = offset; }, 300);

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

        // 7-day forecast (weather page)
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

        // Dashboard temperature chart
        drawTemperatureChart(d.daily);

    } catch (err) {
        const lang = document.getElementById('langSelect')?.value || 'en';
        const noInternetMsg = lang === 'hi' ? '📴 इंटरनेट उपलब्ध नहीं — मौसम डेटा लोड नहीं हो सकता' :
            lang === 'te' ? '📴 ఇంటర్నెట్ అందుబాటులో లేదు — వాతావరణ డేటా లోడ్ చేయడం సాధ్యం కాదు' :
                '📴 No internet connection — Weather data unavailable';
        const retryLabel = lang === 'hi' ? 'पुनः प्रयास करें' : lang === 'te' ? 'మళ్ళీ ప్రయత్నించండి' : 'Retry';
        document.getElementById('weatherCurrent').innerHTML =
            `<div style="text-align:center;padding:2rem;color:#6b7280">
                <p style="font-size:2rem;margin-bottom:8px">📴</p>
                <p style="font-weight:600;margin-bottom:4px">${noInternetMsg}</p>
                <p style="font-size:0.75rem;margin-bottom:12px">Weather requires internet • FAISS search works offline</p>
                <button onclick="loadWeather()" style="padding:6px 16px;border-radius:8px;background:#059669;color:white;border:none;cursor:pointer;font-size:0.8rem">${retryLabel}</button>
            </div>`;
        document.getElementById('dashTemp').textContent = '--°C';
        document.getElementById('dashWeatherDesc').textContent = 'Offline';
        document.getElementById('forecastGrid').innerHTML =
            '<p style="color:#6b7280;text-align:center;padding:1rem;grid-column:1/-1">📴 Weather forecast needs internet connection</p>';
    }
}

// ── 7-DAY TEMPERATURE CHART (Canvas) ────────────────────
function drawTemperatureChart(daily) {
    const canvas = document.getElementById('tempChart');
    if (!canvas) return;

    // Set canvas resolution
    const rect = canvas.parentElement.getBoundingClientRect();
    const w = rect.width - 32; // padding
    const h = 120;
    canvas.width = w * 2;
    canvas.height = h * 2;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    const ctx = canvas.getContext('2d');
    ctx.scale(2, 2);

    const maxTemps = daily.temperature_2m_max;
    const minTemps = daily.temperature_2m_min;
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const allTemps = [...maxTemps, ...minTemps];
    const min = Math.min(...allTemps) - 2;
    const max = Math.max(...allTemps) + 2;
    const range = max - min;

    const padL = 30, padR = 10, padT = 15, padB = 25;
    const graphW = w - padL - padR;
    const graphH = h - padT - padB;

    const xStep = graphW / (maxTemps.length - 1);
    const toY = (v) => padT + graphH - ((v - min) / range) * graphH;
    const toX = (i) => padL + i * xStep;

    // Grid lines
    ctx.strokeStyle = '#f3f4f6';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 4; i++) {
        const y = padT + (graphH / 4) * i;
        ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(w - padR, y); ctx.stroke();
    }

    // Max temp gradient fill
    ctx.beginPath();
    maxTemps.forEach((t, i) => { i === 0 ? ctx.moveTo(toX(i), toY(t)) : ctx.lineTo(toX(i), toY(t)); });
    ctx.lineTo(toX(maxTemps.length - 1), padT + graphH);
    ctx.lineTo(toX(0), padT + graphH);
    ctx.closePath();
    const grad = ctx.createLinearGradient(0, padT, 0, padT + graphH);
    grad.addColorStop(0, 'rgba(239,68,68,0.15)');
    grad.addColorStop(1, 'rgba(239,68,68,0)');
    ctx.fillStyle = grad;
    ctx.fill();

    // Max temp line
    ctx.beginPath();
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    maxTemps.forEach((t, i) => { i === 0 ? ctx.moveTo(toX(i), toY(t)) : ctx.lineTo(toX(i), toY(t)); });
    ctx.stroke();

    // Min temp gradient fill
    ctx.beginPath();
    minTemps.forEach((t, i) => { i === 0 ? ctx.moveTo(toX(i), toY(t)) : ctx.lineTo(toX(i), toY(t)); });
    ctx.lineTo(toX(minTemps.length - 1), padT + graphH);
    ctx.lineTo(toX(0), padT + graphH);
    ctx.closePath();
    const grad2 = ctx.createLinearGradient(0, padT, 0, padT + graphH);
    grad2.addColorStop(0, 'rgba(59,130,246,0.12)');
    grad2.addColorStop(1, 'rgba(59,130,246,0)');
    ctx.fillStyle = grad2;
    ctx.fill();

    // Min temp line
    ctx.beginPath();
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    minTemps.forEach((t, i) => { i === 0 ? ctx.moveTo(toX(i), toY(t)) : ctx.lineTo(toX(i), toY(t)); });
    ctx.stroke();

    // Data points & labels
    ctx.font = '600 9px Inter, sans-serif';
    maxTemps.forEach((t, i) => {
        // Max dot
        ctx.fillStyle = '#ef4444';
        ctx.beginPath(); ctx.arc(toX(i), toY(t), 3, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#ef4444';
        ctx.textAlign = 'center';
        ctx.fillText(Math.round(t) + '°', toX(i), toY(t) - 7);

        // Min dot
        ctx.fillStyle = '#3b82f6';
        ctx.beginPath(); ctx.arc(toX(i), toY(minTemps[i]), 3, 0, Math.PI * 2); ctx.fill();
        ctx.fillText(Math.round(minTemps[i]) + '°', toX(i), toY(minTemps[i]) + 14);

        // Day label
        const date = new Date(daily.time[i]);
        const dayName = i === 0 ? 'Today' : days[date.getDay()];
        ctx.fillStyle = '#9ca3af';
        ctx.font = '500 8px Inter, sans-serif';
        ctx.fillText(dayName, toX(i), h - 5);
        ctx.font = '600 9px Inter, sans-serif';
    });

    // Legend
    ctx.font = '500 8px Inter, sans-serif';
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(padL, 3, 8, 3); ctx.fillText(' Max', padL + 10, 7);
    ctx.fillStyle = '#3b82f6';
    ctx.fillRect(padL + 45, 3, 8, 3); ctx.fillText(' Min', padL + 55, 7);
}

// ── WHEAT SPARKLINE ─────────────────────────────────────
function drawWheatSparkline(priceHistory) {
    const canvas = document.getElementById('wheatSparkline');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const vals = priceHistory;
    const w = canvas.width, h = canvas.height;
    const min = Math.min(...vals), max = Math.max(...vals);
    const range = max - min || 1;

    ctx.clearRect(0, 0, w, h);

    // Gradient fill
    ctx.beginPath();
    vals.forEach((v, i) => {
        const x = (i / (vals.length - 1)) * w;
        const y = h - 4 - ((v - min) / range) * (h - 8);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath();
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, 'rgba(34,197,94,0.2)');
    grad.addColorStop(1, 'rgba(34,197,94,0)');
    ctx.fillStyle = grad;
    ctx.fill();

    // Line
    ctx.beginPath();
    ctx.strokeStyle = '#22c55e';
    ctx.lineWidth = 1.5;
    vals.forEach((v, i) => {
        const x = (i / (vals.length - 1)) * w;
        const y = h - 4 - ((v - min) / range) * (h - 8);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();
}

// ── MARKET TICKER ───────────────────────────────────────
async function loadMarketTicker() {
    try {
        const state = getLocationState();
        const stateParam = state ? `?state=${encodeURIComponent(state)}` : '';
        const r = await fetch(API + '/market-prices' + stateParam);
        const d = await r.json();
        const scroll = document.getElementById('tickerScroll');
        const locationLabel = d.location || 'India';
        const isOffline = d.offline || false;
        const dateBadge = isOffline
            ? '<span style="font-size:0.55rem;color:#f59e0b;font-weight:700;margin-left:4px">⚠️ Offline</span>'
            : `<span style="font-size:0.55rem;color:#6b7280;margin-left:4px">📅 Daily·${locationLabel}</span>`;
        scroll.innerHTML = d.prices.slice(0, 6).map(p => `
            <div class="ticker-chip" onclick="navigate('market')" title="${p.mandi || 'N/A'} | ${p.source}">
                <span class="tc-icon">${p.icon}</span>
                <div class="tc-info">
                    <p class="tc-name">${p.crop}${dateBadge}</p>
                    <p class="tc-price">₹${p.price.toLocaleString('en-IN')}</p>
                </div>
                <span class="tc-change ${p.change >= 0 ? 'up' : 'down'}">${p.change >= 0 ? '↑' : '↓'}${Math.abs(p.change)}%</span>
            </div>
        `).join('');

        // Wheat sparkline from first price's history
        const wheat = d.prices.find(p => p.crop === 'Wheat') || d.prices[0];
        if (wheat) {
            document.getElementById('dashWheatPrice').innerHTML =
                `₹${wheat.price.toLocaleString('en-IN')}<span class="stat-unit">/${wheat.unit}</span>`;
            document.getElementById('dashWheatDelta').textContent =
                `${wheat.change >= 0 ? '↑' : '↓'} ${Math.abs(wheat.change)}%`;
            document.getElementById('dashWheatDelta').className =
                'stat-delta ' + (wheat.change >= 0 ? 'up' : 'down');
            if (wheat.history) drawWheatSparkline(wheat.history);
        }
    } catch {
        // Market API runs on localhost, so should always work
        // If it fails, server might not be running
        document.getElementById('tickerScroll').innerHTML =
            '<p style="color:#6b7280;font-size:0.8rem;padding:0.5rem">📴 Market data unavailable — API server may be offline</p>';
    }
}

// ── CROP CALENDAR ───────────────────────────────────────
function loadCropCalendar() {
    const month = new Date().getMonth() + 1; // 1-12
    const lang = getCurrentLang();
    let events, seasonName;

    const calData = {
        en: {
            rabi: {
                name: 'Rabi Season (Oct–Mar)',
                events: [
                    { month: 'Oct', task: 'Land preparation & sowing' },
                    { month: 'Nov', task: 'Wheat sowing, first irrigation' },
                    { month: 'Dec', task: 'Weed control & 2nd irrigation' },
                    { month: 'Jan', task: 'Top dressing fertilizer' },
                    { month: 'Feb', task: '3rd irrigation, pest monitoring' },
                    { month: 'Mar', task: 'Harvest preparation' },
                ]
            },
            kharif: {
                name: 'Kharif Season (Jun–Sep)',
                events: [
                    { month: 'Jun', task: 'Monsoon sowing — Rice, Maize' },
                    { month: 'Jul', task: 'Transplanting & weed control' },
                    { month: 'Aug', task: 'Fertilizer application' },
                    { month: 'Sep', task: 'Pest control & pre-harvest' },
                ]
            },
            zaid: {
                name: 'Zaid Season (Apr–Jun)',
                events: [
                    { month: 'Apr', task: 'Summer sowing — Watermelon, Moong' },
                    { month: 'May', task: 'Irrigation management' },
                    { month: 'Jun', task: 'Harvesting zaid crops' },
                ]
            }
        },
        hi: {
            rabi: {
                name: 'रबी मौसम (अक्टू–मार्च)',
                events: [
                    { month: 'अक्टू', task: 'भूमि तैयारी और बुवाई' },
                    { month: 'नवं', task: 'गेहूं बुवाई, पहली सिंचाई' },
                    { month: 'दिसं', task: 'खरपतवार नियंत्रण और दूसरी सिंचाई' },
                    { month: 'जन', task: 'टॉप ड्रेसिंग उर्वरक' },
                    { month: 'फर', task: 'तीसरी सिंचाई, कीट निगरानी' },
                    { month: 'मार्च', task: 'कटाई की तैयारी' },
                ]
            },
            kharif: {
                name: 'खरीफ मौसम (जून–सितं)',
                events: [
                    { month: 'जून', task: 'मानसून बुवाई — चावल, मक्का' },
                    { month: 'जुला', task: 'रोपाई और खरपतवार नियंत्रण' },
                    { month: 'अग', task: 'उर्वरक डालना' },
                    { month: 'सितं', task: 'कीट नियंत्रण और पूर्व-कटाई' },
                ]
            },
            zaid: {
                name: 'जायद मौसम (अप्रैल–जून)',
                events: [
                    { month: 'अप्रैल', task: 'ग्रीष्म बुवाई — तरबूज, मूंग' },
                    { month: 'मई', task: 'सिंचाई प्रबंधन' },
                    { month: 'जून', task: 'जायद फसल कटाई' },
                ]
            }
        },
        te: {
            rabi: {
                name: 'రబీ కాలం (అక్టో–మార్చి)',
                events: [
                    { month: 'అక్టో', task: 'భూమి తయారీ & విత్తడం' },
                    { month: 'నవం', task: 'గోధుమ విత్తడం, మొదటి నీటి తడి' },
                    { month: 'డిసెం', task: 'కలుపు నియంత్రణ & రెండో నీటి తడి' },
                    { month: 'జన', task: 'టాప్ డ్రెస్సింగ్ ఎరువు' },
                    { month: 'ఫిబ్ర', task: 'మూడో నీటి తడి, పురుగుల పరీక్ష' },
                    { month: 'మార్చి', task: 'కోత సిద్ధం' },
                ]
            },
            kharif: {
                name: 'ఖరీఫ్ కాలం (జూన్–సెప్టెం)',
                events: [
                    { month: 'జూన్', task: 'వర్షాకాల విత్తనం — వరి, మొక్కజొన్న' },
                    { month: 'జులై', task: 'నాట్లు & కలుపు నియంత్రణ' },
                    { month: 'ఆగ', task: 'ఎరువు వేయడం' },
                    { month: 'సెప్టెం', task: 'పురుగుల నియంత్రణ & ముందు-కోత' },
                ]
            },
            zaid: {
                name: 'జైద్ కాలం (ఏప్రిల్–జూన్)',
                events: [
                    { month: 'ఏప్రిల్', task: 'వేసవి విత్తనం — పుచ్చకాయ, పెసలు' },
                    { month: 'మే', task: 'నీటి తడి నిర్వహణ' },
                    { month: 'జూన్', task: 'జైద్ పంటల కోత' },
                ]
            }
        }
    };

    const cd = calData[lang] || calData.en;
    let seasonKey;
    if (month >= 10 || month <= 3) seasonKey = 'rabi';
    else if (month >= 6 && month <= 9) seasonKey = 'kharif';
    else seasonKey = 'zaid';

    const season = cd[seasonKey];
    seasonName = season.name;

    // Add status based on current month
    const monthNums = { rabi: [10, 11, 12, 1, 2, 3], kharif: [6, 7, 8, 9], zaid: [4, 5, 6] };
    const nums = monthNums[seasonKey];
    events = season.events.map((e, i) => {
        const eventMonth = nums[i];
        let status = 'pending';
        if (seasonKey === 'rabi') {
            const adjustedCurrent = month < 6 ? month + 12 : month;
            const adjustedEvent = eventMonth < 6 ? eventMonth + 12 : eventMonth;
            if (adjustedCurrent > adjustedEvent) status = 'done';
            else if (adjustedCurrent === adjustedEvent) status = 'active';
        } else {
            if (month > eventMonth) status = 'done';
            else if (month === eventMonth) status = 'active';
        }
        return { ...e, status };
    });

    document.getElementById('calSeasonName').textContent = seasonName;
    document.getElementById('cropCalendar').innerHTML = events.map(e => `
        <div class="cal-item ${e.status}">
            <p class="cal-month">${e.month}</p>
            <p class="cal-task">${e.task}</p>
        </div>
    `).join('');
}

// ── AI DAILY TIP ────────────────────────────────────────
async function loadAIDailyTip() {
    const body = document.getElementById('aiTipBody');
    const month = new Date().getMonth() + 1;
    const season = (month >= 10 || month <= 3) ? 'Rabi' : (month >= 6 && month <= 9) ? 'Kharif' : 'Zaid';
    const lang = document.getElementById('langSelect')?.value || 'en';

    // Offline seasonal tips (no API needed)
    const offlineTips = {
        Rabi: {
            en: 'Apply balanced NPK fertilizer during vegetative growth. Monitor soil moisture weekly and irrigate when below 30%. Watch for aphids in mustard and rust in wheat crops.',
            hi: 'वानस्पतिक वृद्धि के दौरान संतुलित NPK उर्वरक डालें। साप्ताहिक मिट्टी की नमी जाँचें और 30% से नीचे होने पर सिंचाई करें। सरसों में एफिड और गेहूं में रतुआ रोग पर नज़र रखें।',
            te: 'మొక్కల పెరుగుదల సమయంలో సమతుల్య NPK ఎరువు వేయండి. వారానికొకసారి నేల తేమ పరీక్షించి 30% కంటే తక్కువగా ఉంటే నీరు పెట్టండి. ఆవాలో అఫిడ్స్ మరియు గోధుమలో తుప్పు వ్యాధిని గమనించండి.'
        },
        Kharif: {
            en: 'Ensure proper drainage in rice paddies during heavy monsoon. Apply neem-based pesticide for organic pest control. Monitor cotton crop for bollworm at flowering stage.',
            hi: 'भारी मानसून के दौरान धान के खेतों में उचित जल निकासी सुनिश्चित करें। जैविक कीट नियंत्रण के लिए नीम आधारित कीटनाशक लगाएं। फूल आने पर कपास में बॉलवर्म की निगरानी करें।',
            te: 'భారీ వర్షాల సమయంలో వరి పొలాల్లో సరైన నీటి తీసుకుపోవడం నిర్ధారించండి. సేంద్రియ పురుగుల నియంత్రణ కోసం వేప ఆధారిత పురుగుమందు వాడండి. పత్తిలో పువ్వుల దశలో బోల్‌వార్మ్ గమనించండి.'
        },
        Zaid: {
            en: 'Increase irrigation frequency for watermelon and cucumber in summer heat. Use mulching to retain soil moisture. Plant moong and sunflower early for best yield.',
            hi: 'गर्मी में तरबूज और खीरे के लिए सिंचाई बढ़ाएं। मिट्टी की नमी बनाए रखने के लिए मल्चिंग करें। बेहतर उपज के लिए मूंग और सूरजमुखी जल्दी बोएं।',
            te: 'వేసవిలో పుచ్చకాయ మరియు దోసకు నీటి తడులు పెంచండి. నేల తేమ నిలుపుకోవడానికి మల్చింగ్ వాడండి. మంచి దిగుబడి కోసం పెసలు మరియు పొద్దుతిరుగుడు ముందుగా విత్తండి.'
        }
    };

    // If truly offline (no internet), show a pre-loaded tip
    if (!isInternetAvailable) {
        const tip = offlineTips[season]?.[lang] || offlineTips[season]?.en;
        body.innerHTML = `<p>${tip}</p><p style="font-size:0.65rem;color:#9ca3af;margin-top:6px">📴 Offline tip • ${season} season</p>`;
        return;
    }

    try {
        const location = getLocationName();
        const monthName = new Date().toLocaleString('en-IN', { month: 'long' });
        const q = `Give a short practical farming tip for ${season} season in ${monthName} for farmers near ${location}, India. Keep it under 3 sentences.`;

        const r = await fetch(API + '/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: q, online_mode: onlineMode, top_k: 3, location })
        });
        const d = await r.json();
        const tip = d.online_answer || d.offline_answer || offlineTips[season]?.en;
        body.innerHTML = `<p>${tip.substring(0, 300)}</p>`;
        addFeedItem('AI daily tip generated', 'dot-blue');
    } catch {
        const tip = offlineTips[season]?.[lang] || offlineTips[season]?.en;
        body.innerHTML = `<p>${tip}</p>`;
    }
}

// ── POPULAR QUESTIONS ───────────────────────────────────
async function loadPopularQuestions() {
    try {
        const lang = getCurrentLang();
        const r = await fetch(API + '/popular?lang=' + lang);
        const d = await r.json();

        // Right panel (chat page)
        const rp = document.getElementById('popularQuestions');
        rp.innerHTML = d.categories.flatMap(c =>
            c.questions.slice(0, 2).map(q =>
                `<button class="rp-chip" onclick="askQuestion('${esc(q)}')">${c.icon} ${q}</button>`
            )
        ).join('');

        // Dashboard popular grid (compact)
        const dp = document.getElementById('dashPopular');
        dp.innerHTML = d.categories.flatMap(c =>
            c.questions.slice(0, 1).map(q =>
                `<button class="pop-chip" onclick="navigate('chat');setTimeout(()=>askQuestion('${esc(q)}'),200)">${c.icon} ${q}</button>`
            )
        ).join('');
    } catch { }
}

// ── MARKET PAGE (full) ──────────────────────────────────
async function loadMarketPrices() {
    try {
        const r = await fetch(API + '/market-prices');
        const d = await r.json();
        const grid = document.getElementById('marketGrid');
        const isLive = d.live;
        grid.innerHTML = d.prices.map((p, i) => `
            <div class="market-card" style="animation-delay:${i * 0.05}s"
                 onclick="navigate('chat');setTimeout(()=>askQuestion('What is the current ${p.crop} price and market trend?'),300)">
                <div class="mc-icon">${p.icon}</div>
                <div class="mc-info">
                    <p class="mc-name">${p.crop}${p.msp ? ' <span style="background:#dcfce7;color:#166534;padding:1px 6px;border-radius:8px;font-size:0.6rem;font-weight:600">MSP ₹' + p.msp + '</span>' : ''}</p>
                    <p class="mc-mandi">📍 ${p.mandi}</p>
                    <p style="font-size:0.6rem;color:#9ca3af;margin-top:2px">${isLive ? '🟢' : '📄'} ${p.source}${p.arrival_date ? ' • ' + p.arrival_date : ''}</p>
                </div>
                <div class="mc-right">
                    <p class="mc-price">₹${p.price.toLocaleString('en-IN')}/${p.unit}</p>
                    <p class="mc-change ${p.change >= 0 ? 'up' : 'down'}">${p.change >= 0 ? '↑' : '↓'} ${Math.abs(p.change)}%${p.msp && isLive ? ' vs MSP' : ''}</p>
                    <canvas class="mc-sparkline" width="80" height="30" id="spark-${i}"></canvas>
                </div>
            </div>
        `).join('') + `<p style="grid-column:1/-1;text-align:center;font-size:0.65rem;color:#9ca3af;padding:0.5rem">${isLive ? '🟢 LIVE' : '📄'} Source: ${d.source || 'Govt. of India'} • ${d.note || ''}</p>`;

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

// ── CROP GUIDE PAGE ─────────────────────────────────────
async function loadCropGuide() {
    try {
        const lang = getCurrentLang();
        const askAILabel = { en: '🤖 Ask AI about', hi: '🤖 AI से पूछें', te: '🤖 AI ని అడగండి' };
        const askLabel = askAILabel[lang] || askAILabel.en;
        const r = await fetch(API + '/crop-guide?lang=' + lang);
        const d = await r.json();
        document.getElementById('cropsGrid').innerHTML = d.crops.map((c, i) => `
            <div class="crop-card" style="animation-delay:${i * 0.06}s">
                <div class="cc-header">
                    <span class="cc-icon">${c.icon}</span>
                    <div><p class="cc-name">${c.name}</p><span class="cc-season">${c.season}</span></div>
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
                    ${askLabel} ${c.name}
                </button>
            </div>
        `).join('');
    } catch {
        document.getElementById('cropsGrid').innerHTML = '<p style="color:#ef4444">❌ Failed to load crop guide</p>';
    }
}

// ── PEST SOLUTIONS PAGE ─────────────────────────────────
async function loadPestSolutions() {
    try {
        const lang = getCurrentLang();
        const r = await fetch(API + '/pest-solutions?lang=' + lang);
        const d = await r.json();
        const labels = d.labels || { affects: 'Affects', ask_ai: '🤖 Ask AI about' };
        document.getElementById('pestsGrid').innerHTML = d.pests.map((p, i) => `
            <div class="pest-card" style="animation-delay:${i * 0.06}s">
                <div class="pc-header">
                    <span style="font-size:1.5rem">${p.icon}</span>
                    <div style="flex:1"><p class="pc-name">${p.name}</p><p class="pc-crops">${labels.affects}: ${p.crops.join(', ')}</p></div>
                    <span class="pc-severity sev-${p.severity}">${p.severity}</span>
                </div>
                <div class="pc-symptoms">⚠️ ${p.symptoms}</div>
                <ul class="pc-solutions">${p.solutions.map(s =>
            `<li><span class="sol-type sol-${s.type}">${s.type}</span> ${s.method}</li>`
        ).join('')}</ul>
                <button class="pop-chip" style="margin-top:0.75rem;justify-content:center;border-color:#fde68a"
                    onclick="navigate('chat');setTimeout(()=>askQuestion('How to control ${p.name} in my crop?'),300)">
                    ${labels.ask_ai} ${p.name}
                </button>
            </div>
        `).join('');
    } catch {
        document.getElementById('pestsGrid').innerHTML = '<p style="color:#ef4444">❌ Failed to load pest solutions</p>';
    }
}

// ── ACTIVITY FEED ───────────────────────────────────────
function addFeedItem(text, dotClass = 'dot-green') {
    const feed = document.getElementById('activityFeed');
    if (!feed) return;
    const time = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    const item = document.createElement('div');
    item.className = 'feed-item';
    item.innerHTML = `<span class="feed-dot ${dotClass}"></span><div><p>${escapeHtml(text)}</p><small>${time}</small></div>`;
    feed.insertBefore(item, feed.firstChild);

    // Keep max 10 items
    while (feed.children.length > 10) feed.removeChild(feed.lastChild);
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
    const location = getLocationName();

    const langSelect = document.getElementById('langSelect');
    const language = langSelect ? langSelect.value : 'en';

    try {
        const r = await fetch(API + '/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, online_mode: onlineMode, top_k: 5, location, language })
        });
        const d = await r.json();
        typingEl.remove();

        if (d.error) { addBubble('ai', '❌ ' + d.error); return; }

        const serverTime = d.timestamp || getFullTimestamp();
        const serverLoc = d.location || location;
        const isOffline = d.mode === 'offline';
        let answer = '';
        let meta = '';

        if (!isOffline && d.online_answer) {
            // ── ONLINE MODE: AI-generated answer ──
            answer = d.online_answer;
        } else {
            // ── OFFLINE MODE: Show formatted FAISS knowledge base results ──
            if (d.results && d.results.length > 0) {
                const lang = langSelect ? langSelect.value : 'en';
                const offlineTitle = lang === 'hi' ? '📚 किसान कॉल सेंटर ज्ञानकोश से उत्तर' :
                    lang === 'te' ? '📚 కిసాన్ కాల్ సెంటర్ డేటాబేస్ నుండి సమాధానాలు' :
                        '📚 Answers from Kisan Call Centre Knowledge Base';
                const confHigh = lang === 'hi' ? 'उच्च मिलान' : lang === 'te' ? 'అధిక సరిపోలిక' : 'High Match';
                const confMed = lang === 'hi' ? 'मध्यम मिलान' : lang === 'te' ? 'మధ్యస్థ సరిపోలిక' : 'Partial Match';
                const confLow = lang === 'hi' ? 'कम मिलान' : lang === 'te' ? 'తక్కువ సరిపోలిక' : 'Low Match';

                let cards = `<p style="font-weight:600;margin-bottom:10px;color:#059669">${offlineTitle}</p>`;
                const seen = new Set();
                d.results.forEach((r, i) => {
                    if (seen.has(r.answer)) return;
                    seen.add(r.answer);
                    const conf = r.confidence;
                    let badge = conf >= 70 ? `🟢 ${confHigh} (${conf}%)` :
                        conf >= 40 ? `🟡 ${confMed} (${conf}%)` :
                            `🟠 ${confLow} (${conf}%)`;
                    const cropTag = r.crop ? `<span style="background:#f0fdf4;color:#166534;padding:2px 8px;border-radius:20px;font-size:0.7rem;margin-left:6px">🌱 ${r.crop}</span>` : '';
                    const stateTag = r.state ? `<span style="background:#eff6ff;color:#1e40af;padding:2px 8px;border-radius:20px;font-size:0.7rem;margin-left:4px">📍 ${r.state}</span>` : '';

                    cards += `<div style="background:rgba(5,150,105,0.06);border:1px solid rgba(5,150,105,0.15);border-radius:12px;padding:12px 14px;margin-bottom:8px">
                        <div style="display:flex;align-items:center;flex-wrap:wrap;gap:4px;margin-bottom:6px">
                            <span style="font-size:0.75rem;font-weight:600;color:#6b7280">${badge}</span>${cropTag}${stateTag}
                        </div>
                        <p style="font-size:0.85rem;color:#374151;line-height:1.5">${escapeHtml(r.answer)}</p>
                    </div>`;
                });
                answer = cards;
            } else {
                answer = d.offline_answer || 'No relevant results found. Try rephrasing your question.';
                answer = formatMarkdown(answer);
            }
        }

        // Build meta bar
        const modeLabel = isOffline ? '📴 Offline (FAISS)' : '🌐 Online (AI)';
        if (d.results && d.results.length > 0) {
            const top = d.results[0];
            const crops = [...new Set(d.results.map(r => r.crop).filter(Boolean))];
            meta = `<div class="bubble-meta">
                <span class="meta-tag conf">${modeLabel}</span>
                <span class="meta-tag conf">✅ ${top.confidence}% match</span>
                ${crops.length ? `<span class="meta-tag info">🌱 ${crops.join(', ')}</span>` : ''}
                <span class="meta-tag info">📍 ${serverLoc}</span>
                <span class="meta-tag info">📅 ${serverTime}</span>
                <span class="meta-tag info">⏱️ ${d.elapsed}s</span>
            </div>`;
        } else {
            meta = `<div class="bubble-meta">
                <span class="meta-tag conf">${modeLabel}</span>
                <span class="meta-tag info">📍 ${serverLoc}</span>
                <span class="meta-tag info">📅 ${serverTime}</span>
                <span class="meta-tag info">⏱️ ${d.elapsed}s</span>
            </div>`;
        }

        // For online mode, format markdown; offline already formatted above
        if (!isOffline && d.online_answer) {
            addBubble('ai', formatMarkdown(answer) + meta);
        } else {
            addBubble('ai', answer + meta);
        }

        history.unshift({ query, time: new Date() });
        updateHistory();
        addFeedItem('Asked: ' + query.substring(0, 50), 'dot-green');
    } catch {
        typingEl.remove();
        addBubble('ai', '❌ Cannot connect to API. Make sure <code>python api_server.py</code> is running.');
    }
}

function addBubble(type, content) {
    const chat = document.getElementById('chatArea');
    const ts = getFullTimestamp();
    const loc = getLocationName();
    const div = document.createElement('div');
    div.className = 'bubble-row ' + type;
    if (type === 'user') {
        div.innerHTML = `<div><div class="bubble user-b">${escapeHtml(content)}</div><p class="bubble-time">📍 ${loc} • ${ts}</p></div>`;
    } else {
        div.innerHTML = `<div class="bubble-avatar">🌾</div><div><div class="bubble ai-b">${content}</div><p class="bubble-time">${ts} • 📍 ${loc} • KrishiMind AI</p></div>`;
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

// ── PRICE PREDICTION & ADVISORY ─────────────────────────
let predictionChart = null;

function loadPricePrediction(crop = 'Wheat') {
    const stateSelect = document.getElementById('predStateSelect');
    const state = stateSelect && stateSelect.value ? stateSelect.value : getLocationState();

    // Synchronize UI dropdown if it's currently on "National" but we have a location
    if (stateSelect && !stateSelect.value && state) {
        stateSelect.value = state;
    }

    const stateParam = state ? `&state=${encodeURIComponent(state)}` : '';
    const endpoint = `/api/price-prediction?crop=${encodeURIComponent(crop)}&days=30${stateParam}`;
    fetch(endpoint)
        .then(r => r.json())
        .then(data => {
            if (data.error) { console.error('[Prediction]', data.error); return; }
            renderPredictionMetrics(data);
            renderPredictionChart(data);
            addFeedItem(`Price prediction loaded for ${crop}${state ? ' (' + state + ')' : ''}`, 'dot-amber');
        })
        .catch(e => console.error('[Prediction] Fetch error:', e));
}


function renderPredictionMetrics(data) {
    const el = (id) => document.getElementById(id);
    el('predCurrentPrice').textContent = `₹${data.current_price.toLocaleString('en-IN')}`;
    el('predMSP').textContent = data.msp ? `₹${data.msp.toLocaleString('en-IN')}` : 'N/A';
    el('predForecast').textContent = `₹${data.predicted_price.toLocaleString('en-IN')}`;

    const changePct = ((data.predicted_price - data.current_price) / data.current_price * 100).toFixed(1);
    const changeEl = el('predForecastChange');
    if (changePct > 0) {
        changeEl.textContent = `↑ ${changePct}% in 30 days`;
        changeEl.style.color = '#22c55e';
    } else if (changePct < 0) {
        changeEl.textContent = `↓ ${Math.abs(changePct)}% in 30 days`;
        changeEl.style.color = '#ef4444';
    } else {
        changeEl.textContent = 'Stable';
        changeEl.style.color = '#6b7280';
    }

    const trendIcons = { rising: '📈 Rising', falling: '📉 Falling', stable: '➡️ Stable' };
    el('predTrend').textContent = trendIcons[data.trend] || data.trend;
    // Replace misleading % confidence with honest label
    const confEl = el('predConfidence');
    if (confEl) {
        confEl.textContent = '±~15% estimate';
        confEl.title = 'Agricultural price models cannot reliably claim high confidence. This is a trend estimate, not a guarantee.';
        confEl.style.color = '#d97706';
    }

    // Update advisory location badge
    const advBadge = document.getElementById('advisoryLocationBadge');
    if (advBadge) {
        const state = getLocationState();
        advBadge.textContent = state ? `📍 ${state}` : '🇮🇳 India';
    }

    // Data Source Badge
    const sourceBadge = el('predSourceBadge');
    const sourceMetric = el('predSourceMetric');
    if (sourceBadge && data.source) {
        sourceBadge.textContent = data.source;
        if (data.source.includes('Synthetic')) {
            sourceBadge.classList.add('synthetic');
        } else {
            sourceBadge.classList.remove('synthetic');
        }
    }
    if (sourceMetric) {
        sourceMetric.textContent = `Source: ${data.source || 'AI Model'}`;
    }

    // Populate methodology panel
    if (data.last_updated) {
        const date = new Date(data.last_updated);
        el('predLastUpdated').textContent = `📊 Updated: ${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    } else {
        el('predLastUpdated').textContent = '';
    }

    renderMethodologyPanel(data);
}

function renderMethodologyPanel(data) {
    const el = (id) => document.getElementById(id);

    // Data Source card
    const dsEl = el('methodDataSource');
    if (dsEl) {
        if (data.source && data.source.includes('data.gov.in')) {
            dsEl.textContent = '🟢 Government Mandi (Real)';
            dsEl.style.color = '#16a34a';
        } else {
            dsEl.textContent = '🟡 Synthetic Model';
            dsEl.style.color = '#d97706';
        }
    }

    // AI Model card
    const modelEl = el('methodModel');
    if (modelEl && data.methodology) {
        modelEl.textContent = data.methodology.model || 'WMA + Linear Regression';
    }

    // Accuracy card — honest description, no fake %
    const accEl = el('methodAccuracy');
    if (accEl) {
        accEl.innerHTML = `<span style="color:#d97706;font-weight:700">±~15%</span> — Trend estimate only. 7-14 days most reliable. Policy shocks, rainfall, and supply cannot be modelled.`;
    }

    // Data Points card
    const dpEl = el('methodDataPoints');
    if (dpEl) {
        const pts = data.data_points || (data.history ? data.history.length : 0);
        dpEl.textContent = `${pts} historical records`;
    }

    // Dynamic feature tags based on methodology
    const featRow = el('predFeaturesRow');
    if (featRow && data.methodology && data.methodology.features) {
        featRow.innerHTML = data.methodology.features.map(f => {
            const shortName = f.split(' (')[0];
            return `<span class="pred-feature-tag">${shortName}</span>`;
        }).join('');
    }

    // Accuracy note
    const noteEl = el('predAccuracyNote');
    if (noteEl && data.methodology && data.methodology.accuracy_note) {
        noteEl.innerHTML = `<strong>📝 Note:</strong> ${data.methodology.accuracy_note}`;
    }
}

function renderPredictionChart(data) {
    const ctx = document.getElementById('predictionChart');
    if (!ctx) return;

    if (predictionChart) {
        predictionChart.destroy();
        predictionChart = null;
    }

    const historyLabels = data.history.map(h => {
        const d = new Date(h.date);
        return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
    });
    const historyPrices = data.history.map(h => h.price);

    const predLabels = data.prediction.map(p => {
        const d = new Date(p.date);
        return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
    });
    const predPrices = data.prediction.map(p => p.price);
    const predUpper = data.prediction.map(p => p.upper);
    const predLower = data.prediction.map(p => p.lower);

    const allLabels = [...historyLabels, ...predLabels];
    const gapFill = new Array(historyLabels.length).fill(null);
    const histGapFill = new Array(predLabels.length).fill(null);

    // Connect history to prediction with last history point
    const connectedPred = [historyPrices[historyPrices.length - 1], ...predPrices];
    const connectedPredLabelsGap = new Array(historyLabels.length - 1).fill(null);

    const mspLine = data.msp ? new Array(allLabels.length).fill(data.msp) : null;

    predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allLabels,
            datasets: [
                {
                    label: 'Historical Price',
                    data: [...historyPrices, ...histGapFill],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59,130,246,0.08)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                },
                {
                    label: 'Predicted Price',
                    data: [...connectedPredLabelsGap, ...connectedPred],
                    borderColor: '#22c55e',
                    borderDash: [6, 3],
                    borderWidth: 2.5,
                    fill: false,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                },
                {
                    label: 'Upper Band',
                    data: [...gapFill, ...predUpper],
                    borderColor: 'transparent',
                    backgroundColor: 'rgba(34,197,94,0.1)',
                    fill: '+1',
                    tension: 0.3,
                    pointRadius: 0,
                },
                {
                    label: 'Lower Band',
                    data: [...gapFill, ...predLower],
                    borderColor: 'transparent',
                    fill: false,
                    tension: 0.3,
                    pointRadius: 0,
                },
                ...(mspLine ? [{
                    label: 'MSP',
                    data: mspLine,
                    borderColor: '#ef4444',
                    borderWidth: 1.5,
                    borderDash: [4, 4],
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 0,
                }] : [])
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    padding: 10,
                    cornerRadius: 8,
                    titleFont: { size: 12 },
                    bodyFont: { size: 11 },
                    callbacks: {
                        label: function (ctx) {
                            if (ctx.dataset.label === 'Upper Band' || ctx.dataset.label === 'Lower Band') return null;
                            return `${ctx.dataset.label}: ₹${ctx.parsed.y?.toLocaleString('en-IN') || '--'}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        maxTicksLimit: 12,
                        font: { size: 10 },
                        color: '#9ca3af'
                    }
                },
                y: {
                    grid: { color: 'rgba(0,0,0,0.04)' },
                    ticks: {
                        font: { size: 10 },
                        color: '#9ca3af',
                        callback: v => `₹${v.toLocaleString('en-IN')}`
                    }
                }
            }
        }
    });
}

function loadPriceAdvisory() {
    const state = getLocationState();
    const stateParam = state ? `?state=${encodeURIComponent(state)}` : '';
    fetch('/api/price-advisory' + stateParam)
        .then(r => r.json())
        .then(data => {
            if (data.error || !data.advisories) return;
            const grid = document.getElementById('advisoryGrid');
            if (!grid) return;

            const locationLabel = state || 'India';
            grid.innerHTML = data.advisories.map(a => `
                <div class="advisory-card verdict-${a.action_color}">
                    <div class="advisory-card-header">
                        <div class="advisory-crop-info">
                            <span class="advisory-crop-icon">${a.icon}</span>
                            <span class="advisory-crop-name">${a.crop}</span>
                        </div>
                        <span class="advisory-verdict-badge badge-${a.action_color}">${a.verdict}</span>
                    </div>
                    <p class="advisory-reason">${a.reason}</p>
                    <div class="advisory-stats">
                        <div class="advisory-stat">
                            <span class="advisory-stat-label">Current</span>
                            <span class="advisory-stat-val">₹${a.current_price.toLocaleString('en-IN')}</span>
                        </div>
                        <div class="advisory-stat">
                            <span class="advisory-stat-label">Forecast</span>
                            <span class="advisory-stat-val">₹${a.predicted_price.toLocaleString('en-IN')}</span>
                        </div>
                        <div class="advisory-stat">
                            <span class="advisory-stat-label">MSP 2025-26</span>
                            <span class="advisory-stat-val">${a.msp ? '₹' + a.msp.toLocaleString('en-IN') : 'None'}</span>
                        </div>
                        <div class="advisory-stat">
                            <span class="advisory-stat-label">Data</span>
                            <span class="advisory-stat-val" style="font-size:0.7rem">${(a.source && a.source.includes('data.gov.in')) ? '📊 Agmarknet' : '🔢 Model'}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        })
        .catch(e => console.error('[Advisory] Error:', e));
}

function loadPredictionMini() {
    fetch('/api/price-advisory?crop=Wheat')
        .then(r => r.json())
        .then(data => {
            if (!data.advisories || !data.advisories.length) return;
            const a = data.advisories[0];
            const el = (id) => document.getElementById(id);
            el('predMiniCrop').textContent = `${a.icon} ${a.crop}`;
            el('predMiniPrice').innerHTML = `₹${a.current_price.toLocaleString('en-IN')}<span class="stat-unit">/qt</span>`;

            const trendStr = a.trend === 'rising' ? `↑ ${a.change_pct}%` :
                a.trend === 'falling' ? `↓ ${Math.abs(a.change_pct)}%` : `→ ${a.change_pct}%`;
            const trendColor = a.trend === 'rising' ? '#22c55e' : a.trend === 'falling' ? '#ef4444' : '#6b7280';
            const trendEl = el('predMiniTrend');
            trendEl.textContent = `${trendStr} forecast`;
            trendEl.className = `stat-delta ${a.trend === 'rising' ? 'up' : a.trend === 'falling' ? 'down' : ''}`;

            const verdictEl = el('predMiniVerdict');
            verdictEl.textContent = a.verdict;
            const badgeColors = {
                green: { bg: '#dcfce7', color: '#15803d' },
                red: { bg: '#fee2e2', color: '#b91c1c' },
                amber: { bg: '#fef3c7', color: '#92400e' },
                blue: { bg: '#dbeafe', color: '#1e40af' }
            };
            const bc = badgeColors[a.action_color] || badgeColors.amber;
            verdictEl.style.background = bc.bg;
            verdictEl.style.color = bc.color;
        })
        .catch(e => console.error('[PredMini] Error:', e));
}

// Load mini widget on dashboard init (delay to not block critical loads)
setTimeout(loadPredictionMini, 3000);

// ── LAZY LOAD SUB-PAGES ─────────────────────────────────
// Load sub-page data only when navigated to (avoid initial overload)
let marketLoaded = false, cropsLoaded = false, pestsLoaded = false, predictionLoaded = false;
const origNavigate = navigate;
navigate = function (page, el) {
    origNavigate(page, el);
    if (page === 'market' && !marketLoaded) { marketLoaded = true; loadMarketPrices(); }
    if (page === 'crops' && !cropsLoaded) { cropsLoaded = true; loadCropGuide(); }
    if (page === 'pests' && !pestsLoaded) { pestsLoaded = true; loadPestSolutions(); }
    if (page === 'prediction' && !predictionLoaded) {
        predictionLoaded = true;
        loadPricePrediction('Wheat');
        loadPriceAdvisory();
    }
};

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
