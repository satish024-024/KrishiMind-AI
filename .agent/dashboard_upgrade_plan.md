---
description: Plan to upgrade dashboard homepage from empty to premium, widget-rich layout
---

# 🎯 Dashboard Homepage Upgrade Plan

## Problem
The current dashboard homepage feels **empty** — just 4 flat stat cards, a few buttons, and some text chips. 
There's too much whitespace, no visual depth, no charts/graphs, no activity indicators.

## Design Inspiration (from research)
- **Bento Grid Layout**: Japanese-inspired puzzle-like grid with varying card sizes (like Apple's WWDC design)
- **Dribbble Smart Farm Dashboards**: Rich with weather charts, crop calendars, gauge indicators, sparklines
- **Premium Admin Templates**: Activity timelines, progress rings, notification panels, mini charts

---

## 📐 New Layout: Bento Grid (2-column + sidebar feel)

```
┌─────────────────────────────────────────────────────────────┐
│ ROW 1: Hero Welcome Banner (gradient, current date/time,   │
│        greeting based on time of day, farm status summary)  │
├────────────┬────────────┬────────────┬──────────────────────┤
│ ROW 2:     │            │            │                      │
│ Wheat      │ Weather    │ Soil       │ AI Insights          │
│ Price      │ Widget     │ Health     │ (large card)         │
│ + sparkline│ + mini     │ Gauge Ring │ "Today's tip from    │
│            │ forecast   │            │  KrishiMind AI"      │
├────────────┴────────────┴────────────┤                      │
│ ROW 3:                               │                      │
│ 7-Day Weather Mini Chart             │                      │
│ (temperature line + rain bars)       ├──────────────────────┤
│                                      │ Crop Calendar        │
├──────────────────────────────────────┤ (current season      │
│ ROW 4:                               │  timeline with       │
│ Market Prices Ticker                 │  active crops)       │
│ (top 5 crops, horizontal scroll     │                      │
│  with sparklines)                    │                      │
├──────────────────────────────────────┼──────────────────────┤
│ ROW 5:                               │ Activity Feed        │
│ Quick Actions (improved with         │ (recent queries,     │
│ icons, descriptions, hover effects)  │  system events,      │
│                                      │  alerts with         │
├──────────────────────────────────────┤  timestamps)         │
│ ROW 6:                               │                      │
│ Popular Questions                    │                      │
│ (2-col grid, better cards)           │                      │
└──────────────────────────────────────┴──────────────────────┘
```

---

## 🧩 New Widgets to Add (11 total)

### Widget 1: Hero Welcome Banner
- **What**: Full-width gradient banner at top
- **Content**: Time-based greeting ("Good Evening, Farmer!"), date, farm summary
- **Style**: Green gradient, rounded corners, subtle pattern overlay
- **Data**: Static + JS Date

### Widget 2: Enhanced Stat Cards (4 existing, upgraded)
- **Wheat Price**: Add sparkline mini chart (7-day trend)
- **Weather**: Add mini 3-day forecast icons below temperature
- **Soil Health**: Replace text with circular progress/gauge ring
- **Alerts**: Add clickable dot indicators for each alert type

### Widget 3: AI Daily Tip Card (NEW - large)
- **What**: Auto-generated farming tip based on season/weather
- **Content**: Fetched from /api/query with a seasonal question
- **Style**: Card with 🌾 icon, glassmorphism background, "Ask more →" link
- **Size**: Spans 1 column, 2 rows (tall card)

### Widget 4: 7-Day Temperature Chart (NEW)
- **What**: Mini area/line chart showing 7-day temperature trend
- **Data**: From Open-Meteo (already loaded for weather page)
- **Style**: Gradient-filled area chart, drawn with Canvas
- **Interaction**: Hover to see individual day values

### Widget 5: Market Prices Ticker (NEW)
- **What**: Horizontal scrolling row of top 5 crop prices
- **Content**: Each has icon, name, price, % change, tiny sparkline
- **Style**: Cards in a horizontal flex, auto-scroll animation
- **Data**: From /api/market-prices

### Widget 6: Crop Calendar Timeline (NEW)
- **What**: Vertical timeline showing current Rabi/Kharif season
- **Content**: Key dates - sowing window, irrigation, harvest
- **Style**: Vertical line with dots, current date highlighted
- **Data**: Hardcoded seasonal data, highlighted programmatically

### Widget 7: Activity Feed (NEW)
- **What**: Real-time feed of recent queries and system events
- **Content**: Recent queries with timestamps, AI responses summary
- **Style**: Scrollable list with icons and relative time ("2 min ago")
- **Data**: From session history + system events

### Widget 8: Soil Health Gauge (NEW)
- **What**: Circular progress ring showing soil pH and moisture
- **Style**: SVG ring with animated fill + center value
- **Data**: From Open-Meteo soil moisture API

### Widget 9: Government Schemes Banner (NEW)
- **What**: Scrolling banner showing active Indian govt farming schemes
- **Content**: PM-KISAN, PM Fasal Bima Yojana, Soil Health Card, etc.
- **Style**: Horizontal auto-scroll, each scheme has icon + brief text
- **Interaction**: Click to ask AI about any scheme

### Widget 10: Knowledge Base Stats (NEW)
- **What**: Shows "2,000+ Q&A pairs | 15+ crops | 28+ states"
- **Style**: 3 mini stat counters with animated number count-up
- **Data**: Static (from known data)

### Widget 11: Quick Weather Alerts (NEW)
- **What**: If rain/storm predicted, show prominent alert banner
- **Content**: "🌧️ Rain expected tomorrow — Consider covering tomato beds"
- **Style**: Amber/red warning bar, dismissible
- **Data**: From weather forecast, programmatic alert logic

---

## 🎨 Design Improvements

### Animations (Minimal & Smooth)
1. **Staggered card entrance** — each card fades up with 50ms delay
2. **Number count-up** — stats animate from 0 to value on load
3. **Sparkline draw** — lines animate left-to-right
4. **Gauge ring fill** — circular progress animates from 0% to value
5. **Ticker auto-scroll** — smooth horizontal scroll for market prices
6. **Hover lift** — cards lift 3px with soft shadow on hover
7. **Page transitions** — existing fade, kept minimal

### Colors & Style
- Keep existing green palette
- Add **glassmorphism** on AI tip card (frosted glass effect)
- Use **CSS custom properties** for consistent theming
- **Subtle grid lines** between bento cells
- **Rounded everything** — 16-20px border radius

### Typography
- Already using Inter (good)
- Add number-specific styling (tabular-nums for prices)
- Larger stat values (2rem+), smaller labels (0.7rem)

---

## 🔧 Implementation Steps

### Step 1: Update `dashboard/index.html`
- Restructure dashboard page from simple grid to bento layout
- Add all new widget HTML containers with skeleton placeholders

### Step 2: Update `dashboard/styles.css`
- Add bento grid CSS (`grid-template-areas` with named regions)
- Add styles for all new widgets (gauge, timeline, ticker, chart)
- Add new animations (count-up, sparkline draw, gauge fill)
- Add glassmorphism for AI tip card

### Step 3: Update `dashboard/app.js`
- Add `loadDashboardWeatherChart()` — Canvas 7-day temperature chart
- Add `loadMarketTicker()` — Fetch & render price ticker
- Add `renderCropCalendar()` — Timeline with season data
- Add `renderActivityFeed()` — Show recent queries
- Add `renderGauge()` — SVG circular progress for soil health
- Add `animateCountUp()` — Animated number counters
- Add `loadAIDailyTip()` — Fetch seasonal farming tip
- Add `renderGovernmentSchemes()` — Scheme ticker

### Step 4: Update `api_server.py`
- Add `/api/daily-tip` endpoint — Returns seasonal farming tip
- Add `/api/schemes` endpoint — Returns government scheme data

### Step 5: Test & Polish
- Test all widgets load with real data
- Test responsive (mobile should stack widgets vertically)
- Test all click interactions navigate to correct pages
- Verify animations are smooth (60fps, no jank)

---

## 📊 Before vs After Comparison

| Aspect | Before (Current) | After (Planned) |
|--------|---------|-------|
| Widgets | 4 flat stat cards | 11 rich interactive widgets |
| Charts | None | Temperature chart + sparklines + gauge |
| Activity | None | Real-time activity feed |
| Data | Static numbers | Live weather, market, soil data |
| Visual Depth | Flat, lots of whitespace | Bento grid, glassmorphism, gradients |
| Animations | Basic fade | Count-up, sparkline draw, gauge fill, stagger |
| Interactivity | Basic buttons | Every widget clickable, hover effects |
| Information | Minimal | Weather alerts, crop calendar, govt schemes |

---

## ⏱️ Estimated Time
- HTML restructure: 10 min
- CSS bento + widgets: 15 min
- JS logic + charts: 20 min
- API updates: 5 min
- Testing: 5 min
- **Total: ~55 minutes**

---

## ✅ Ready to implement?
Say "go" and I'll start with Step 1.
