"""
Australian Horse Racing Betting Dashboard - FastAPI Backend
Production-ready API serving racing odds, market movers, and predictions
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import json

app = FastAPI(title="Horse Racing Dashboard API", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Sample data for Australian horse racing
SAMPLE_RACES = [
    {
        "id": "hr1",
        "race": "Royal Randwick - 2:15 PM",
        "track": "Randwick",
        "horse1": "Thunder Strike",
        "horse2": "Dancing Flame",
        "odds1": 3.20,
        "odds2": 2.80,
        "position1st": 4.10,
        "trend": "up",
        "trendValue": "+0.4",
        "featured": True
    },
    {
        "id": "hr2",
        "race": "Moonee Valley - 3:45 PM",
        "track": "Moonee Valley",
        "horse1": "Silver Bullet",
        "horse2": "Golden Phoenix",
        "odds1": 2.50,
        "odds2": 3.50,
        "position1st": 5.20,
        "trend": "down",
        "trendValue": "-0.15",
        "featured": False
    },
    {
        "id": "hr3",
        "race": "Flemington - 4:30 PM",
        "track": "Flemington",
        "horse1": "Midnight Runner",
        "horse2": "Starlight Express",
        "odds1": 4.50,
        "odds2": 1.95,
        "position1st": 3.80,
        "trend": "up",
        "trendValue": "+0.25",
        "featured": True
    },
    {
        "id": "hr4",
        "race": "Caulfield - 5:15 PM",
        "track": "Caulfield",
        "horse1": "Royal Ascot",
        "horse2": "Lightning Storm",
        "odds1": 2.15,
        "odds2": 4.20,
        "position1st": 6.50,
        "trend": "stable",
        "trendValue": "0.00",
        "featured": False
    }
]

MARKET_MOVERS = [
    {
        "position": 1,
        "horse": "Thunder Strike",
        "track": "Randwick",
        "change": "+0.40",
        "direction": "up",
        "currentOdds": 3.20
    },
    {
        "position": 2,
        "horse": "Midnight Runner",
        "track": "Flemington",
        "change": "+0.25",
        "direction": "up",
        "currentOdds": 4.50
    },
    {
        "position": 3,
        "horse": "Golden Phoenix",
        "track": "Moonee Valley",
        "change": "-0.30",
        "direction": "down",
        "currentOdds": 3.50
    },
    {
        "position": 4,
        "horse": "Lightning Storm",
        "track": "Caulfield",
        "change": "+0.15",
        "direction": "up",
        "currentOdds": 4.20
    }
]

PREDICTIONS = [
    {
        "id": "pred1",
        "race": "Royal Randwick - 2:15 PM",
        "track": "Randwick",
        "tip": "Thunder Strike",
        "confidence": 78,
        "reason": "Strong recent form, excellent track record at Randwick"
    },
    {
        "id": "pred2",
        "race": "Moonee Valley - 3:45 PM",
        "track": "Moonee Valley",
        "tip": "Silver Bullet",
        "confidence": 65,
        "reason": "Consistent performer, favorable track conditions"
    },
    {
        "id": "pred3",
        "race": "Flemington - 4:30 PM",
        "track": "Flemington",
        "tip": "Starlight Express",
        "confidence": 82,
        "reason": "Outstanding recent wins, perfect jockey-horse combination"
    },
    {
        "id": "pred4",
        "race": "Caulfield - 5:15 PM",
        "track": "Caulfield",
        "tip": "Royal Ascot",
        "confidence": 71,
        "reason": "Strong field position, excellent barrier draw"
    }
]


@app.get("/")
async def serve_index():
    """Serve the main dashboard HTML"""
    return FileResponse("static/index.html", media_type="text/html")


@app.get("/api/odds")
async def get_odds():
    """
    Get current racing odds and events
    Returns sample data with Australian decimal odds format
    """
    return {
        "events": SAMPLE_RACES,
        "timestamp": datetime.now().isoformat(),
        "status": "live"
    }


@app.get("/api/market-movers")
async def get_market_movers():
    """
    Get top market movers - horses with significant odds changes
    Useful for identifying value bets and market sentiment
    """
    return {
        "movers": MARKET_MOVERS,
        "timestamp": datetime.now().isoformat(),
        "total": len(MARKET_MOVERS)
    }


@app.get("/api/predictions")
async def get_predictions():
    """
    Get expert predictions and tips for upcoming races
    Includes confidence levels and reasoning
    """
    return {
        "predictions": PREDICTIONS,
        "timestamp": datetime.now().isoformat(),
        "total": len(PREDICTIONS)
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Horse Racing Dashboard API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
