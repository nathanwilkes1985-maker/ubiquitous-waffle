/**
 * Australian Horse Racing Betting Dashboard - Frontend
 * Real-time odds, market movers, and predictions
 */

// ========================================
// Configuration
// ========================================

const CONFIG = {
    API_BASE: '/api',
    REFRESH_INTERVAL: 10000, // 10 seconds
    ANIMATION_DURATION: 300,
};

// ========================================
// State Management
// ========================================

const state = {
    races: [],
    movers: [],
    predictions: [],
    currentFilter: 'all',
    lastUpdate: null,
};

// ========================================
// DOM Elements
// ========================================

const elements = {
    racesGrid: document.getElementById('racesGrid'),
    moversContainer: document.getElementById('moversContainer'),
    predictionsContainer: document.getElementById('predictionsContainer'),
    lastUpdate: document.getElementById('lastUpdate'),
    filterButtons: document.querySelectorAll('.filter-btn'),
    raceCardTemplate: document.getElementById('raceCardTemplate'),
    moverCardTemplate: document.getElementById('moverCardTemplate'),
    predictionCardTemplate: document.getElementById('predictionCardTemplate'),
};

// ========================================
// API Functions
// ========================================

/**
 * Fetch racing odds from backend
 */
async function fetchOdds() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/odds`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        state.races = data.events || [];
        state.lastUpdate = new Date(data.timestamp);
        return true;
    } catch (error) {
        console.error('Error fetching odds:', error);
        return false;
    }
}

/**
 * Fetch market movers from backend
 */
async function fetchMarketMovers() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/market-movers`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        state.movers = data.movers || [];
        return true;
    } catch (error) {
        console.error('Error fetching market movers:', error);
        return false;
    }
}

/**
 * Fetch expert predictions from backend
 */
async function fetchPredictions() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/predictions`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        state.predictions = data.predictions || [];
        return true;
    } catch (error) {
        console.error('Error fetching predictions:', error);
        return false;
    }
}

/**
 * Fetch all data in parallel
 */
async function fetchAllData() {
    await Promise.all([
        fetchOdds(),
        fetchMarketMovers(),
        fetchPredictions(),
    ]);
}

// ========================================
// Rendering Functions
// ========================================

/**
 * Render race cards to the grid
 */
function renderRaceCards() {
    const container = elements.racesGrid;
    container.innerHTML = '';

    // Filter races based on current filter
    const filteredRaces = filterRaces(state.races, state.currentFilter);

    if (filteredRaces.length === 0) {
        container.innerHTML = '<div class="loading-spinner">No races found</div>';
        return;
    }

    filteredRaces.forEach((race) => {
        const card = createRaceCard(race);
        container.appendChild(card);
    });

    updateTimestamp();
}

/**
 * Create a race card element from template
 */
function createRaceCard(race) {
    const template = elements.raceCardTemplate.content.cloneNode(true);
    const card = template.querySelector('.race-card');

    // Header
    template.querySelector('.race-name').textContent = race.race;
    template.querySelector('.track-badge').textContent = race.track;

    // Featured badge
    if (race.featured) {
        template.querySelector('.featured-badge').style.display = 'block';
    }

    // Horse 1
    const horse1Card = template.querySelector('.horse-1');
    horse1Card.querySelector('.horse-name').textContent = race.horse1;
    horse1Card.querySelector('.odds-value').textContent = race.odds1.toFixed(2);
    horse1Card.querySelector('.place-value').textContent = (race.odds1 / 2).toFixed(2);

    // Horse 2
    const horse2Card = template.querySelector('.horse-2');
    horse2Card.querySelector('.horse-name').textContent = race.horse2;
    horse2Card.querySelector('.odds-value').textContent = race.odds2.toFixed(2);
    horse2Card.querySelector('.place-value').textContent = (race.odds2 / 2).toFixed(2);

    // Trend
    const trendIcon = template.querySelector('.trend-icon');
    const trendValue = template.querySelector('.trend-value');
    trendValue.textContent = race.trendValue;
    trendValue.classList.add(race.trend);

    if (race.trend === 'up') {
        trendIcon.textContent = '📈';
    } else if (race.trend === 'down') {
        trendIcon.textContent = '📉';
    } else {
        trendIcon.textContent = '➡️';
    }

    // Buttons
    const betBtn = template.querySelector('.bet-btn');
    const detailsBtn = template.querySelector('.details-btn');

    betBtn.addEventListener('click', () => {
        showNotification(`Bet placed on ${race.horse1} vs ${race.horse2}`);
    });

    detailsBtn.addEventListener('click', () => {
        showNotification(`Details: ${race.race} at ${race.track}`);
    });

    // Add animation
    card.classList.add('fade-in');

    return template;
}

/**
 * Render market movers
 */
function renderMarketMovers() {
    const container = elements.moversContainer;
    container.innerHTML = '';

    if (state.movers.length === 0) {
        container.innerHTML = '<div class="loading-spinner">No movers available</div>';
        return;
    }

    state.movers.forEach((mover) => {
        const card = createMoverCard(mover);
        container.appendChild(card);
    });
}

/**
 * Create a market mover card element from template
 */
function createMoverCard(mover) {
    const template = elements.moverCardTemplate.content.cloneNode(true);

    template.querySelector('.mover-rank').textContent = `#${mover.position}`;
    template.querySelector('.mover-horse').textContent = mover.horse;
    template.querySelector('.mover-track').textContent = mover.track;
    template.querySelector('.mover-odds').textContent = mover.currentOdds.toFixed(2);

    const changeValue = template.querySelector('.change-value');
    changeValue.textContent = mover.change;
    changeValue.classList.add(mover.direction);

    const changeIcon = template.querySelector('.change-icon');
    changeIcon.textContent = mover.direction === 'up' ? '▲' : '▼';

    template.querySelector('.mover-card').classList.add('fade-in');

    return template;
}

/**
 * Render expert predictions
 */
function renderPredictions() {
    const container = elements.predictionsContainer;
    container.innerHTML = '';

    if (state.predictions.length === 0) {
        container.innerHTML = '<div class="loading-spinner">No predictions available</div>';
        return;
    }

    state.predictions.forEach((prediction) => {
        const card = createPredictionCard(prediction);
        container.appendChild(card);
    });
}

/**
 * Create a prediction card element from template
 */
function createPredictionCard(prediction) {
    const template = elements.predictionCardTemplate.content.cloneNode(true);

    template.querySelector('.prediction-tip').textContent = prediction.tip;
    template.querySelector('.prediction-track').textContent = prediction.track;
    template.querySelector('.prediction-reason').textContent = prediction.reason;

    const confidenceBadge = template.querySelector('.confidence-badge');
    confidenceBadge.textContent = `${prediction.confidence}%`;

    // Color code confidence
    if (prediction.confidence >= 75) {
        confidenceBadge.style.background = 'var(--success-color)';
    } else if (prediction.confidence >= 60) {
        confidenceBadge.style.background = 'var(--accent-teal)';
    } else {
        confidenceBadge.style.background = 'var(--warning-color)';
    }

    template.querySelector('.prediction-card').classList.add('fade-in');

    return template;
}

/**
 * Update timestamp display
 */
function updateTimestamp() {
    if (state.lastUpdate) {
        const hours = String(state.lastUpdate.getHours()).padStart(2, '0');
        const minutes = String(state.lastUpdate.getMinutes()).padStart(2, '0');
        const seconds = String(state.lastUpdate.getSeconds()).padStart(2, '0');
        elements.lastUpdate.textContent = `${hours}:${minutes}:${seconds}`;
    }
}

// ========================================
// Filtering Functions
// ========================================

/**
 * Filter races based on current filter
 */
function filterRaces(races, filter) {
    if (filter === 'all') return races;
    if (filter === 'featured') return races.filter((r) => r.featured);

    // Filter by track
    const trackMap = {
        randwick: 'Randwick',
        'moonee-valley': 'Moonee Valley',
        flemington: 'Flemington',
        caulfield: 'Caulfield',
    };

    const trackName = trackMap[filter];
    return races.filter((r) => r.track === trackName);
}

/**
 * Handle filter button clicks
 */
function setupFilterButtons() {
    elements.filterButtons.forEach((btn) => {
        btn.addEventListener('click', () => {
            // Update active state
            elements.filterButtons.forEach((b) => b.classList.remove('active'));
            btn.classList.add('active');

            // Update filter and re-render
            state.currentFilter = btn.dataset.filter;
            renderRaceCards();
        });
    });
}

// ========================================
// Utility Functions
// ========================================

/**
 * Show notification (simple toast-like message)
 */
function showNotification(message) {
    // For now, just log and show in console
    console.log('Notification:', message);
    // In production, you might use a toast library or custom notification
    alert(message);
}

/**
 * Initialize real-time updates
 */
function startAutoRefresh() {
    // Refresh immediately
    refreshAllData();

    // Then refresh at intervals
    setInterval(refreshAllData, CONFIG.REFRESH_INTERVAL);
}

/**
 * Refresh all data and re-render
 */
async function refreshAllData() {
    await fetchAllData();
    renderRaceCards();
    renderMarketMovers();
    renderPredictions();
}

// ========================================
// Initialization
// ========================================

/**
 * Initialize the dashboard
 */
async function init() {
    console.log('Initializing Horse Racing Dashboard...');

    // Setup filter buttons
    setupFilterButtons();

    // Load initial data
    await fetchAllData();

    // Render all sections
    renderRaceCards();
    renderMarketMovers();
    renderPredictions();

    // Start auto-refresh
    startAutoRefresh();

    console.log('Dashboard initialized successfully');
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
