/**
 * Australian Horse Racing Betting Dashboard - Frontend v4.0
 * AI-powered predictions, chat interface, roughies tips, and all Australian tracks
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
    roughies: [],
    currentFilter: 'all',
    lastUpdate: null,
    aiChatOpen: false,
};

// ========================================
// DOM Elements
// ========================================

const elements = {
    racesGrid: document.getElementById('racesGrid'),
    moversContainer: document.getElementById('moversContainer'),
    predictionsContainer: document.getElementById('predictionsContainer'),
    roughiesContainer: document.getElementById('roughiesContainer'),
    lastUpdate: document.getElementById('lastUpdate'),
    filterButtons: document.querySelectorAll('.filter-btn'),
    raceCardTemplate: document.getElementById('raceCardTemplate'),
    moverCardTemplate: document.getElementById('moverCardTemplate'),
    predictionCardTemplate: document.getElementById('predictionCardTemplate'),
    roughiesCardTemplate: document.getElementById('roughiesCardTemplate'),
    aiChatToggle: document.getElementById('aiChatToggle'),
    aiChatPanel: document.getElementById('aiChatPanel'),
    aiChatClose: document.getElementById('aiChatClose'),
    aiChatMessages: document.getElementById('aiChatMessages'),
    aiChatInput: document.getElementById('aiChatInput'),
    aiChatSend: document.getElementById('aiChatSend'),
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
        if (!response.ok) throw new Error('Failed to fetch odds');
        const data = await response.json();
        state.races = data.events || [];
        state.lastUpdate = new Date();
        return state.races;
    } catch (error) {
        console.error('Error fetching odds:', error);
        return [];
    }
}

/**
 * Fetch market movers from backend
 */
async function fetchMarketMovers() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/market-movers`);
        if (!response.ok) throw new Error('Failed to fetch movers');
        const data = await response.json();
        state.movers = data.movers || [];
        return state.movers;
    } catch (error) {
        console.error('Error fetching movers:', error);
        return [];
    }
}

/**
 * Fetch expert predictions from backend
 */
async function fetchPredictions() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/predictions`);
        if (!response.ok) throw new Error('Failed to fetch predictions');
        const data = await response.json();
        state.predictions = data.predictions || [];
        return state.predictions;
    } catch (error) {
        console.error('Error fetching predictions:', error);
        return [];
    }
}

/**
 * Fetch roughies tips from backend
 */
async function fetchRoughies() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/roughies`);
        if (!response.ok) throw new Error('Failed to fetch roughies');
        const data = await response.json();
        state.roughies = data.roughies || [];
        return state.roughies;
    } catch (error) {
        console.error('Error fetching roughies:', error);
        return [];
    }
}

/**
 * Get AI prediction for a specific race
 */
async function getAIPrediction(raceId) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/ai-prediction/${raceId}`);
        if (!response.ok) throw new Error('Failed to get AI prediction');
        const data = await response.json();
        return data.ai_prediction;
    } catch (error) {
        console.error('Error getting AI prediction:', error);
        return { error: 'Failed to get AI prediction' };
    }
}

/**
 * Get AI insights for user query
 */
async function getAIInsights(query) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/ai-insights`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        if (!response.ok) throw new Error('Failed to get AI insights');
        const data = await response.json();
        return data.insights;
    } catch (error) {
        console.error('Error getting AI insights:', error);
        return { error: 'Failed to get AI insights' };
    }
}

// ========================================
// Rendering Functions
// ========================================

/**
 * Render race cards to the grid
 */
function renderRaces() {
    const filteredRaces = filterRaces(state.races, state.currentFilter);
    
    if (filteredRaces.length === 0) {
        elements.racesGrid.innerHTML = '<div class="loading-spinner">No races found</div>';
        return;
    }

    elements.racesGrid.innerHTML = '';
    
    filteredRaces.forEach(race => {
        const card = createRaceCard(race);
        elements.racesGrid.appendChild(card);
    });
}

/**
 * Create a race card element
 */
function createRaceCard(race) {
    const template = elements.raceCardTemplate.content.cloneNode(true);
    
    // Header
    template.querySelector('.race-name').textContent = race.race;
    template.querySelector('.track-badge').textContent = race.track;
    
    if (race.featured) {
        template.querySelector('.featured-badge').style.display = 'block';
    }

    // Race details
    template.querySelector('.distance').textContent = race.distance || 'N/A';
    template.querySelector('.class').textContent = race.class || 'N/A';
    template.querySelector('.prize').textContent = race.prize || 'N/A';

    // Horses (show first 2)
    const horses = race.horses || [];
    if (horses.length >= 2) {
        // First horse
        template.querySelector('.horse-1 .horse-name').textContent = horses[0].name;
        template.querySelector('.horse-1 .jockey').textContent = `Jockey: ${horses[0].jockey}`;
        template.querySelector('.horse-1 .trainer').textContent = `Trainer: ${horses[0].trainer}`;
        template.querySelector('.horse-1 .odds-value').textContent = horses[0].odds.toFixed(2);
        template.querySelector('.horse-1 .place-value').textContent = horses[0].place_odds.toFixed(2);

        // Second horse
        template.querySelector('.horse-2 .horse-name').textContent = horses[1].name;
        template.querySelector('.horse-2 .jockey').textContent = `Jockey: ${horses[1].jockey}`;
        template.querySelector('.horse-2 .trainer').textContent = `Trainer: ${horses[1].trainer}`;
        template.querySelector('.horse-2 .odds-value').textContent = horses[1].odds.toFixed(2);
        template.querySelector('.horse-2 .place-value').textContent = horses[1].place_odds.toFixed(2);

        // Trend
        const trendIcon = template.querySelector('.trend-icon');
        const trendValue = template.querySelector('.trend-value');
        const trend = horses[0].trend;
        
        if (trend === 'up') {
            trendIcon.textContent = '📈';
            trendIcon.classList.add('up');
        } else if (trend === 'down') {
            trendIcon.textContent = '📉';
            trendIcon.classList.add('down');
        } else {
            trendIcon.textContent = '➡️';
        }
        
        trendValue.textContent = horses[0].trendValue;
    }

    // Event listeners
    template.querySelector('.bet-btn').addEventListener('click', () => {
        showBetSlip(race, horses[0]);
    });

    template.querySelector('.ai-predict-btn').addEventListener('click', () => {
        showAIPrediction(race);
    });

    template.querySelector('.details-btn').addEventListener('click', () => {
        showRaceDetails(race);
    });

    const card = template.querySelector('.race-card');
    return card;
}

/**
 * Render market movers
 */
function renderMarketMovers() {
    if (state.movers.length === 0) {
        elements.moversContainer.innerHTML = '<div class="loading-spinner">No movers</div>';
        return;
    }

    elements.moversContainer.innerHTML = '';
    
    state.movers.forEach(mover => {
        const card = createMoverCard(mover);
        elements.moversContainer.appendChild(card);
    });
}

/**
 * Create a market mover card
 */
function createMoverCard(mover) {
    const template = elements.moverCardTemplate.content.cloneNode(true);
    
    template.querySelector('.mover-rank').textContent = `#${mover.rank}`;
    template.querySelector('.mover-horse').textContent = mover.horse;
    template.querySelector('.mover-track').textContent = mover.track;
    
    const changeValue = template.querySelector('.change-value');
    changeValue.textContent = mover.movement;
    changeValue.classList.add(mover.direction);
    
    const changeIcon = template.querySelector('.change-icon');
    changeIcon.textContent = mover.direction === 'up' ? '📈' : '📉';
    
    template.querySelector('.mover-odds').textContent = mover.current_odds.toFixed(2);
    
    return template.querySelector('.mover-card');
}

/**
 * Render expert predictions
 */
function renderPredictions() {
    if (state.predictions.length === 0) {
        elements.predictionsContainer.innerHTML = '<div class="loading-spinner">No predictions</div>';
        return;
    }

    elements.predictionsContainer.innerHTML = '';
    
    state.predictions.forEach(prediction => {
        const card = createPredictionCard(prediction);
        elements.predictionsContainer.appendChild(card);
    });
}

/**
 * Create a prediction card
 */
function createPredictionCard(prediction) {
    const template = elements.predictionCardTemplate.content.cloneNode(true);
    
    template.querySelector('.prediction-tip').textContent = `${prediction.tip} - ${prediction.horse}`;
    template.querySelector('.confidence-badge').textContent = `${prediction.confidence}% Confidence`;
    template.querySelector('.prediction-track').textContent = prediction.track;
    template.querySelector('.prediction-reason').textContent = prediction.analysis;
    
    return template.querySelector('.prediction-card');
}

/**
 * Render roughies tips
 */
function renderRoughies() {
    if (state.roughies.length === 0) {
        elements.roughiesContainer.innerHTML = '<div class="loading-spinner">No roughies</div>';
        return;
    }

    elements.roughiesContainer.innerHTML = '';
    
    state.roughies.forEach(roughie => {
        const card = createRoughiesCard(roughie);
        elements.roughiesContainer.appendChild(card);
    });
}

/**
 * Create a roughies card
 */
function createRoughiesCard(roughie) {
    const template = elements.roughiesCardTemplate.content.cloneNode(true);
    
    template.querySelector('.roughies-rank').textContent = `#${roughie.rank}`;
    template.querySelector('.roughies-horse').textContent = roughie.horse;
    template.querySelector('.roughies-track').textContent = roughie.track;
    template.querySelector('.roughies-odds').textContent = roughie.odds.toFixed(2);
    template.querySelector('.roughies-confidence').textContent = `${roughie.confidence}% Confidence`;
    template.querySelector('.roughies-reason').textContent = roughie.analysis;
    
    return template.querySelector('.roughies-card');
}

// ========================================
// Filter Functions
// ========================================

/**
 * Filter races based on current filter
 */
function filterRaces(races, filter) {
    if (filter === 'all') return races;
    if (filter === 'featured') return races.filter(r => r.featured);
    
    // Filter by track (case-insensitive, handle hyphenated names)
    const trackName = filter.replace('-', ' ').toLowerCase();
    return races.filter(r => r.track.toLowerCase() === trackName);
}

/**
 * Handle filter button clicks
 */
function setupFilterButtons() {
    elements.filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            elements.filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.currentFilter = btn.dataset.filter;
            renderRaces();
        });
    });
}

// ========================================
// UI Functions
// ========================================

/**
 * Update last update timestamp
 */
function updateTimestamp() {
    if (state.lastUpdate) {
        const hours = String(state.lastUpdate.getHours()).padStart(2, '0');
        const minutes = String(state.lastUpdate.getMinutes()).padStart(2, '0');
        const seconds = String(state.lastUpdate.getSeconds()).padStart(2, '0');
        elements.lastUpdate.textContent = `${hours}:${minutes}:${seconds}`;
    }
}

/**
 * Show bet slip modal
 */
function showBetSlip(race, horse) {
    alert(`Bet placed on ${horse.name} in ${race.race}\n\nNote: This is a demo. Real betting integration coming soon!`);
}

/**
 * Show AI prediction for a race
 */
async function showAIPrediction(race) {
    const prediction = await getAIPrediction(race.id);
    if (prediction.error) {
        alert('Could not get AI prediction. Please try again.');
    } else {
        const analysis = prediction.analysis || 'AI analysis not available';
        alert(`AI Prediction for ${race.race}:\n\n${analysis}`);
    }
}

/**
 * Show race details modal
 */
function showRaceDetails(race) {
    const details = `
Race: ${race.race}
Track: ${race.track}
Distance: ${race.distance}
Class: ${race.class}
Prize: ${race.prize}
Going: ${race.going}

Runners:
${race.horses.map(h => `- ${h.name} (${h.odds.toFixed(2)})`).join('\n')}
    `;
    alert(details);
}

// ========================================
// AI Chat Functions
// ========================================

/**
 * Toggle AI chat panel
 */
function toggleAIChat() {
    state.aiChatOpen = !state.aiChatOpen;
    if (state.aiChatOpen) {
        elements.aiChatPanel.classList.remove('hidden');
        elements.aiChatInput.focus();
    } else {
        elements.aiChatPanel.classList.add('hidden');
    }
}

/**
 * Add message to chat
 */
function addChatMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = isUser ? 'user-message' : 'ai-message';
    
    const p = document.createElement('p');
    p.textContent = text;
    messageDiv.appendChild(p);
    
    elements.aiChatMessages.appendChild(messageDiv);
    elements.aiChatMessages.scrollTop = elements.aiChatMessages.scrollHeight;
}

/**
 * Handle AI chat message
 */
async function handleAIChatMessage() {
    const query = elements.aiChatInput.value.trim();
    if (!query) return;
    
    // Add user message
    addChatMessage(query, true);
    elements.aiChatInput.value = '';
    
    // Get AI response
    const insights = await getAIInsights(query);
    if (insights.error) {
        addChatMessage('Sorry, I encountered an error. Please try again.');
    } else {
        addChatMessage(insights.response || 'No response available');
    }
}

/**
 * Setup AI chat event listeners
 */
function setupAIChat() {
    elements.aiChatToggle.addEventListener('click', toggleAIChat);
    elements.aiChatClose.addEventListener('click', toggleAIChat);
    elements.aiChatSend.addEventListener('click', handleAIChatMessage);
    elements.aiChatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleAIChatMessage();
    });
}

// ========================================
// Data Refresh
// ========================================

/**
 * Refresh all data from API
 */
async function refreshData() {
    try {
        await Promise.all([
            fetchOdds(),
            fetchMarketMovers(),
            fetchPredictions(),
            fetchRoughies()
        ]);
        
        renderRaces();
        renderMarketMovers();
        renderPredictions();
        renderRoughies();
        updateTimestamp();
    } catch (error) {
        console.error('Error refreshing data:', error);
    }
}

/**
 * Setup auto-refresh interval
 */
function setupAutoRefresh() {
    // Initial load
    refreshData();
    
    // Refresh every 10 seconds
    setInterval(refreshData, CONFIG.REFRESH_INTERVAL);
}

// ========================================
// Initialization
// ========================================

/**
 * Initialize the dashboard
 */
function init() {
    setupFilterButtons();
    setupAIChat();
    setupAutoRefresh();
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
