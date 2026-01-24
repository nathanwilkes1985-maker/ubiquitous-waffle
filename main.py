"""
Australian Horse Racing Betting Dashboard - FastAPI Backend v4.0
Enhanced with all Australian racetracks, AI predictions, and Roughies Tips
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os
import re
from openai import OpenAI

app = FastAPI(title="Horse Racing Dashboard API", version="4.0.0")

# Add CORS middleware to allow cross-origin requests from documentation site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize OpenAI client (optional - only if API key is available)
try:
    client = OpenAI()
    ai_enabled = True
except Exception as e:
    print(f"Warning: OpenAI client not initialized: {e}")
    client = None
    ai_enabled = False

# All Australian Racetracks with comprehensive race data
AUSTRALIAN_TRACKS = {
    "NSW": ["Randwick", "Rosehill", "Canterbury", "Warwick Farm", "Goulburn", "Canberra"],
    "VIC": ["Flemington", "Caulfield", "Moonee Valley", "Sandown", "Bendigo", "Ballarat"],
    "QLD": ["Eagle Farm", "Doomben", "Gold Coast", "Sunshine Coast", "Townsville", "Rockhampton"],
    "WA": ["Ascot", "Belmont", "Northam"],
    "SA": ["Morphettville", "Cheltenham", "Barossa Park"],
    "TAS": ["Hobart", "Launceston"],
    "ACT": ["Canberra Racecourse"]
}

# Comprehensive race data across all Australian tracks
SAMPLE_RACES = [
    # NSW Races
    {
        "id": "hr1",
        "race": "Royal Randwick - 2:15 PM",
        "track": "Randwick",
        "state": "NSW",
        "distance": "1600m",
        "class": "Class 2",
        "prize": "$125,000",
        "going": "Good",
        "featured": True,
        "horses": [
            {"name": "Thunder Strike", "number": 1, "odds": 3.20, "place_odds": 1.60, "jockey": "James McDonald", "trainer": "Chris Waller", "weight": "58kg", "form": "2-1-3", "trend": "up", "trendValue": "+0.4"},
            {"name": "Dancing Flame", "number": 2, "odds": 2.80, "place_odds": 1.40, "jockey": "Hugh Bowman", "trainer": "Gai Waterhouse", "weight": "57kg", "form": "1-2-1", "trend": "down", "trendValue": "-0.2"},
            {"name": "Silver Bullet", "number": 3, "odds": 4.50, "place_odds": 1.80, "jockey": "Tommy Berry", "trainer": "Peter Snowden", "weight": "56kg", "form": "3-2-2", "trend": "stable", "trendValue": "0.0"},
            {"name": "Golden Phoenix", "number": 4, "odds": 5.50, "place_odds": 2.20, "jockey": "Blake Shinn", "trainer": "John O'Shea", "weight": "55kg", "form": "4-3-2", "trend": "up", "trendValue": "+0.6"}
        ]
    },
    {
        "id": "hr2",
        "race": "Rosehill Gardens - 3:00 PM",
        "track": "Rosehill",
        "state": "NSW",
        "distance": "1400m",
        "class": "Class 1",
        "prize": "$150,000",
        "going": "Good to Firm",
        "featured": False,
        "horses": [
            {"name": "Midnight Runner", "number": 1, "odds": 2.40, "place_odds": 1.20, "jockey": "Kerrin McEvoy", "trainer": "Gai Waterhouse", "weight": "59kg", "form": "1-1-2", "trend": "up", "trendValue": "+0.8"},
            {"name": "Starlight Express", "number": 2, "odds": 1.85, "place_odds": 0.90, "jockey": "James McDonald", "trainer": "Chris Waller", "weight": "58kg", "form": "1-1-1", "trend": "up", "trendValue": "+1.2"},
            {"name": "Royal Ascot", "number": 3, "odds": 3.50, "place_odds": 1.75, "jockey": "Hugh Bowman", "trainer": "Gai Waterhouse", "weight": "57kg", "form": "2-1-2", "trend": "down", "trendValue": "-0.4"},
            {"name": "Lightning Storm", "number": 4, "odds": 6.50, "place_odds": 2.80, "jockey": "Corey Brown", "trainer": "Peter Snowden", "weight": "56kg", "form": "4-3-2", "trend": "stable", "trendValue": "0.0"}
        ]
    },
    # VIC Races
    {
        "id": "hr3",
        "race": "Moonee Valley - 3:45 PM",
        "track": "Moonee Valley",
        "state": "VIC",
        "distance": "1400m",
        "class": "Class 3",
        "prize": "$95,000",
        "going": "Good to Firm",
        "featured": False,
        "horses": [
            {"name": "Silver Bullet", "number": 5, "odds": 2.50, "place_odds": 1.25, "jockey": "Damien Oliver", "trainer": "Darren Weir", "weight": "59kg", "form": "1-1-2", "trend": "up", "trendValue": "+0.8"},
            {"name": "Golden Phoenix", "number": 6, "odds": 3.50, "place_odds": 1.75, "jockey": "Craig Williams", "trainer": "Michael Kent", "weight": "58kg", "form": "2-1-3", "trend": "down", "trendValue": "-0.3"},
            {"name": "Midnight Runner", "number": 7, "odds": 4.50, "place_odds": 2.00, "jockey": "Zac Purton", "trainer": "David Brideoake", "weight": "57kg", "form": "3-2-1", "trend": "up", "trendValue": "+0.5"},
            {"name": "Royal Ascot", "number": 8, "odds": 6.00, "place_odds": 2.40, "jockey": "Mark Zahra", "trainer": "Mick Price", "weight": "56kg", "form": "4-3-2", "trend": "stable", "trendValue": "0.0"}
        ]
    },
    {
        "id": "hr4",
        "race": "Flemington - 4:30 PM",
        "track": "Flemington",
        "state": "VIC",
        "distance": "2000m",
        "class": "Class 1",
        "prize": "$150,000",
        "going": "Good",
        "featured": True,
        "horses": [
            {"name": "Midnight Runner", "number": 9, "odds": 4.50, "place_odds": 2.25, "jockey": "Brett Prebble", "trainer": "Anthony Cummings", "weight": "60kg", "form": "1-2-1", "trend": "up", "trendValue": "+0.9"},
            {"name": "Starlight Express", "number": 10, "odds": 1.95, "place_odds": 0.97, "jockey": "Kerrin McEvoy", "trainer": "Gai Waterhouse", "weight": "59kg", "form": "1-1-1", "trend": "up", "trendValue": "+1.2"},
            {"name": "Royal Ascot", "number": 11, "odds": 2.25, "place_odds": 1.07, "jockey": "William Pike", "trainer": "Chris Waller", "weight": "58kg", "form": "2-1-2", "trend": "down", "trendValue": "-0.4"},
            {"name": "Thunder Strike", "number": 12, "odds": 3.75, "place_odds": 1.65, "jockey": "Corey Brown", "trainer": "Peter Snowden", "weight": "57kg", "form": "3-2-1", "trend": "stable", "trendValue": "0.0"}
        ]
    },
    {
        "id": "hr5",
        "race": "Caulfield - 5:15 PM",
        "track": "Caulfield",
        "state": "VIC",
        "distance": "1200m",
        "class": "Class 2",
        "prize": "$110,000",
        "going": "Firm",
        "featured": False,
        "horses": [
            {"name": "Royal Ascot", "number": 13, "odds": 2.15, "place_odds": 1.07, "jockey": "Damien Oliver", "trainer": "John O'Shea", "weight": "59kg", "form": "1-1-2", "trend": "up", "trendValue": "+0.7"},
            {"name": "Lightning Storm", "number": 14, "odds": 4.20, "place_odds": 2.10, "jockey": "James McDonald", "trainer": "Darren Weir", "weight": "58kg", "form": "2-3-1", "trend": "down", "trendValue": "-0.5"},
            {"name": "Starlight Express", "number": 15, "odds": 3.00, "place_odds": 1.50, "jockey": "Craig Williams", "trainer": "Michael Kent", "weight": "57kg", "form": "1-2-2", "trend": "up", "trendValue": "+0.3"},
            {"name": "Dancing Flame", "number": 16, "odds": 5.00, "place_odds": 2.00, "jockey": "Hugh Bowman", "trainer": "Chris Waller", "weight": "56kg", "form": "3-2-3", "trend": "stable", "trendValue": "0.0"}
        ]
    },
    # QLD Races
    {
        "id": "hr6",
        "race": "Eagle Farm - 2:00 PM",
        "track": "Eagle Farm",
        "state": "QLD",
        "distance": "1600m",
        "class": "Class 2",
        "prize": "$120,000",
        "going": "Good",
        "featured": True,
        "horses": [
            {"name": "Desert Storm", "number": 1, "odds": 3.80, "place_odds": 1.90, "jockey": "Jim Byrne", "trainer": "Tony Gollan", "weight": "58kg", "form": "2-2-1", "trend": "up", "trendValue": "+0.5"},
            {"name": "Tropical Heat", "number": 2, "odds": 2.60, "place_odds": 1.30, "jockey": "Damien Browne", "trainer": "Steve Tregea", "weight": "57kg", "form": "1-1-2", "trend": "up", "trendValue": "+0.8"},
            {"name": "Sunshine Gold", "number": 3, "odds": 5.00, "place_odds": 2.00, "jockey": "Robbie Fradd", "trainer": "Toby Edmonds", "weight": "56kg", "form": "3-2-3", "trend": "down", "trendValue": "-0.3"},
            {"name": "Reef Runner", "number": 4, "odds": 4.20, "place_odds": 1.80, "jockey": "Ryan Maloney", "trainer": "Michael Costa", "weight": "55kg", "form": "2-1-2", "trend": "stable", "trendValue": "0.0"}
        ]
    },
    {
        "id": "hr7",
        "race": "Doomben - 3:30 PM",
        "track": "Doomben",
        "state": "QLD",
        "distance": "1350m",
        "class": "Class 3",
        "prize": "$90,000",
        "going": "Good to Firm",
        "featured": False,
        "horses": [
            {"name": "Outback Express", "number": 1, "odds": 3.40, "place_odds": 1.70, "jockey": "Jim Byrne", "trainer": "Tony Gollan", "weight": "58kg", "form": "1-2-1", "trend": "up", "trendValue": "+0.6"},
            {"name": "Coast Runner", "number": 2, "odds": 2.80, "place_odds": 1.40, "jockey": "Damien Browne", "trainer": "Steve Tregea", "weight": "57kg", "form": "2-1-2", "trend": "down", "trendValue": "-0.2"},
            {"name": "Bush Fire", "number": 3, "odds": 4.80, "place_odds": 2.10, "jockey": "Robbie Fradd", "trainer": "Toby Edmonds", "weight": "56kg", "form": "3-3-2", "trend": "stable", "trendValue": "0.0"},
            {"name": "Coral Reef", "number": 4, "odds": 6.50, "place_odds": 2.50, "jockey": "Ryan Maloney", "trainer": "Michael Costa", "weight": "55kg", "form": "4-2-3", "trend": "up", "trendValue": "+0.4"}
        ]
    },
    # WA Races
    {
        "id": "hr8",
        "race": "Ascot - 1:45 PM",
        "track": "Ascot",
        "state": "WA",
        "distance": "1800m",
        "class": "Class 1",
        "prize": "$140,000",
        "going": "Good",
        "featured": False,
        "horses": [
            {"name": "Western Star", "number": 1, "odds": 2.90, "place_odds": 1.45, "jockey": "Peter Hall", "trainer": "Grant Williams", "weight": "59kg", "form": "1-1-2", "trend": "up", "trendValue": "+0.7"},
            {"name": "Perth Pride", "number": 2, "odds": 3.50, "place_odds": 1.75, "jockey": "Shaun McGruddy", "trainer": "Adam Durrant", "weight": "58kg", "form": "2-1-1", "trend": "up", "trendValue": "+0.9"},
            {"name": "Swan Valley", "number": 3, "odds": 4.80, "place_odds": 2.00, "jockey": "Chris Parnham", "trainer": "Simon Miller", "weight": "57kg", "form": "3-2-2", "trend": "down", "trendValue": "-0.4"},
            {"name": "Wildflower", "number": 4, "odds": 5.50, "place_odds": 2.20, "jockey": "William Pike", "trainer": "Michael Freedman", "weight": "56kg", "form": "2-3-1", "trend": "stable", "trendValue": "0.0"}
        ]
    },
    # SA Races
    {
        "id": "hr9",
        "race": "Morphettville - 2:30 PM",
        "track": "Morphettville",
        "state": "SA",
        "distance": "1400m",
        "class": "Class 2",
        "prize": "$100,000",
        "going": "Good",
        "featured": False,
        "horses": [
            {"name": "Adelaide Ace", "number": 1, "odds": 3.20, "place_odds": 1.60, "jockey": "Barend Vorster", "trainer": "Grant Matheson", "weight": "58kg", "form": "1-2-1", "trend": "up", "trendValue": "+0.5"},
            {"name": "Barossa Pride", "number": 2, "odds": 2.70, "place_odds": 1.35, "jockey": "Shaun Parnham", "trainer": "Phillip Stokes", "weight": "57kg", "form": "2-1-2", "trend": "up", "trendValue": "+0.8"},
            {"name": "South Coast", "number": 3, "odds": 4.50, "place_odds": 1.90, "jockey": "Jason Holder", "trainer": "Darren Weir", "weight": "56kg", "form": "3-2-3", "trend": "down", "trendValue": "-0.3"},
            {"name": "Hills Runner", "number": 4, "odds": 5.80, "place_odds": 2.30, "jockey": "Declan Bates", "trainer": "Cliff Brown", "weight": "55kg", "form": "4-3-2", "trend": "stable", "trendValue": "0.0"}
        ]
    }
]

# Roughies Tips - Outsider recommendations with higher odds
ROUGHIES_TIPS = [
    {
        "rank": 1,
        "horse": "Golden Phoenix",
        "track": "Moonee Valley",
        "odds": 5.50,
        "confidence": 65,
        "analysis": "Strong form in recent races. Good track record at Moonee Valley. Outsider value pick.",
        "tip": "EACH WAY",
        "reason": "Improving form with solid jockey"
    },
    {
        "rank": 2,
        "horse": "Lightning Storm",
        "track": "Caulfield",
        "odds": 4.20,
        "confidence": 72,
        "analysis": "Consistent performer with improving odds. Favorable track conditions.",
        "tip": "WIN",
        "reason": "Value play at current odds"
    },
    {
        "rank": 3,
        "horse": "Bush Fire",
        "track": "Doomben",
        "odds": 4.80,
        "confidence": 68,
        "analysis": "Good form at Doomben. Outsider with potential.",
        "tip": "PLACE",
        "reason": "Track specialist"
    },
    {
        "rank": 4,
        "horse": "Coral Reef",
        "track": "Doomben",
        "odds": 6.50,
        "confidence": 55,
        "analysis": "Long shot with improving trend. Could surprise.",
        "tip": "EACH WAY",
        "reason": "High odds outsider"
    },
    {
        "rank": 5,
        "horse": "Wildflower",
        "track": "Ascot",
        "odds": 5.50,
        "confidence": 70,
        "analysis": "Consistent performer at Ascot. Good value at current odds.",
        "tip": "WIN",
        "reason": "Track form specialist"
    },
    {
        "rank": 6,
        "horse": "South Coast",
        "track": "Morphettville",
        "odds": 4.50,
        "confidence": 62,
        "analysis": "Outsider with potential. Favorable conditions expected.",
        "tip": "PLACE",
        "reason": "Value pick for place betting"
    }
]

# Market Movers
MARKET_MOVERS = [
    {"rank": 1, "horse": "Thunder Strike", "track": "Randwick", "movement": "+0.40", "direction": "up", "current_odds": 3.20, "previous_odds": 2.80, "volume": "High"},
    {"rank": 2, "horse": "Starlight Express", "track": "Flemington", "movement": "+1.20", "direction": "up", "current_odds": 1.95, "previous_odds": 1.50, "volume": "Very High"},
    {"rank": 3, "horse": "Golden Phoenix", "track": "Moonee Valley", "movement": "-0.30", "direction": "down", "current_odds": 3.50, "previous_odds": 3.80, "volume": "Medium"},
    {"rank": 4, "horse": "Lightning Storm", "track": "Caulfield", "movement": "-0.50", "direction": "down", "current_odds": 4.20, "previous_odds": 4.70, "volume": "Medium"}
]

# Expert Predictions
PREDICTIONS = [
    {"rank": 1, "horse": "Thunder Strike", "track": "Randwick", "confidence": 87, "prediction": "Strong Recent Form", "analysis": "Excellent track record at Randwick with consistent wins.", "tip": "WIN"},
    {"rank": 2, "horse": "Silver Bullet", "track": "Moonee Valley", "confidence": 82, "prediction": "Consistent Performer", "analysis": "Reliable performer with 1-1-2 form.", "tip": "PLACE"},
    {"rank": 3, "horse": "Starlight Express", "track": "Flemington", "confidence": 91, "prediction": "Strong Favorite", "analysis": "Exceptional form with 1-1-1 record.", "tip": "WIN"},
    {"rank": 4, "horse": "Royal Ascot", "track": "Caulfield", "confidence": 78, "prediction": "Good Value Bet", "analysis": "Solid performer with improving form.", "tip": "EACH WAY"}
]


# ========================================
# AI Functions
# ========================================

def generate_ai_prediction(race_data: dict) -> dict:
    """Generate AI-powered prediction for a race using OpenAI"""
    if not client or not ai_enabled:
        # Generate intelligent sample prediction based on race data
        horses = race_data.get('horses', [])
        if horses:
            # Pick the horse with best odds as primary pick
            top_pick = min(horses, key=lambda h: h.get('odds', 999))
            second_pick = sorted(horses, key=lambda h: h.get('odds', 999))[1] if len(horses) > 1 else horses[0]
            confidence = 65 + (hash(race_data.get('id', '')) % 20)  # 65-85% confidence
            
            return {
                "top_pick": top_pick['name'],
                "second_pick": second_pick['name'],
                "confidence": confidence,
                "analysis": f"{top_pick['name']} shows strong form with {top_pick['jockey']} in the saddle. Trainer {top_pick['trainer']} has excellent track record at {race_data.get('track', 'this track')}.",
                "bet_type": "WIN",
                "model": "sample_intelligent"
            }
        
        return {
            "analysis": "AI predictions are not available. Using sample data instead.",
            "confidence": 0,
            "model": "sample"
        }
    
    try:
        horses_info = "\n".join([
            f"- {h['name']}: Odds {h['odds']}, Jockey: {h['jockey']}, Trainer: {h['trainer']}, Form: {h['form']}, Trend: {h['trend']}"
            for h in race_data.get('horses', [])[:4]
        ])
        
        prompt = f"""Analyze this horse racing race and provide a brief, confident prediction:

Race: {race_data.get('race', 'Unknown')}
Track: {race_data.get('track', 'Unknown')}
Distance: {race_data.get('distance', 'Unknown')}
Class: {race_data.get('class', 'Unknown')}
Going: {race_data.get('going', 'Unknown')}

Horses:
{horses_info}

Provide:
1. Top 2 horse predictions (horse name and confidence %)
2. Brief analysis (1-2 sentences)
3. Recommended bet type (WIN/PLACE/EACH WAY)

Format as JSON with keys: top_pick, second_pick, confidence, analysis, bet_type"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert horse racing analyst. Provide confident, data-driven predictions based on form, odds, and track conditions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        ai_response = response.choices[0].message.content
        
        try:
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "analysis": ai_response,
            "confidence": 75,
            "model": "gpt-4.1-mini"
        }
    except Exception as e:
        print(f"Error generating AI prediction: {e}")
        return {
            "error": str(e),
            "analysis": "AI analysis temporarily unavailable"
        }


def generate_ai_insights(query: str) -> dict:
    """Generate AI insights for user queries about horse racing"""
    if not client or not ai_enabled:
        return {
            "response": "AI insights are not available at this time. Please try again later.",
            "model": "sample"
        }
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Australian horse racing analyst and betting advisor. Provide helpful, accurate insights about horse racing, betting strategies, and race analysis."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "response": response.choices[0].message.content,
            "model": "gpt-4.1-mini"
        }
    except Exception as e:
        print(f"Error generating AI insights: {e}")
        return {
            "error": str(e),
            "response": "AI insights temporarily unavailable"
        }


# ========================================
# API Endpoints
# ========================================

@app.get("/")
async def serve_index():
    """Serve the main dashboard HTML"""
    return FileResponse("static/index.html", media_type="text/html")


@app.get("/api/odds")
async def get_odds():
    """Get current racing odds and events with detailed horse information"""
    return {
        "events": SAMPLE_RACES,
        "timestamp": datetime.now().isoformat(),
        "status": "live",
        "version": "4.0"
    }


@app.get("/api/filter")
async def filter_races(track: str = None, time_from: str = None, time_to: str = None, featured: bool = False):
    """Filter races by track, time range, and featured status"""
    filtered = SAMPLE_RACES.copy()
    
    # Filter by track
    if track and track.lower() != 'all':
        filtered = [r for r in filtered if r['track'].lower() == track.lower()]
    
    # Filter by featured
    if featured:
        filtered = [r for r in filtered if r.get('featured', False)]
    
    # Filter by time range
    if time_from or time_to:
        filtered_by_time = []
        for race in filtered:
            race_time = extract_time(race['race'])
            if race_time:
                if time_from and time_to:
                    if is_time_in_range(race_time, time_from, time_to):
                        filtered_by_time.append(race)
                elif time_from:
                    if is_time_after(race_time, time_from):
                        filtered_by_time.append(race)
                elif time_to:
                    if is_time_before(race_time, time_to):
                        filtered_by_time.append(race)
            else:
                filtered_by_time.append(race)
        filtered = filtered_by_time
    
    return {
        "events": filtered,
        "total": len(filtered),
        "filters": {
            "track": track,
            "time_from": time_from,
            "time_to": time_to,
            "featured": featured
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/market-movers")
async def get_market_movers():
    """Get top market movers - horses with significant odds changes"""
    return {
        "movers": MARKET_MOVERS,
        "timestamp": datetime.now().isoformat(),
        "total": len(MARKET_MOVERS)
    }


@app.get("/api/predictions")
async def get_predictions():
    """Get expert predictions and tips for upcoming races"""
    return {
        "predictions": PREDICTIONS,
        "timestamp": datetime.now().isoformat(),
        "total": len(PREDICTIONS)
    }


@app.get("/api/roughies")
async def get_roughies_tips():
    """Get roughies tips - outsider recommendations with higher odds"""
    return {
        "roughies": ROUGHIES_TIPS,
        "timestamp": datetime.now().isoformat(),
        "total": len(ROUGHIES_TIPS),
        "description": "Outsider picks with value odds"
    }


@app.get("/api/tracks")
async def get_all_tracks():
    """Get all Australian racetracks organized by state"""
    return {
        "tracks": AUSTRALIAN_TRACKS,
        "total_states": len(AUSTRALIAN_TRACKS),
        "total_tracks": sum(len(tracks) for tracks in AUSTRALIAN_TRACKS.values())
    }


@app.get("/api/ai-prediction/{race_id}")
async def get_ai_prediction(race_id: str):
    """Get AI-powered prediction for a specific race"""
    race = next((r for r in SAMPLE_RACES if r['id'] == race_id), None)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    prediction = generate_ai_prediction(race)
    return {
        "race_id": race_id,
        "race": race['race'],
        "ai_prediction": prediction,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/ai-insights")
async def get_ai_insights(request: dict):
    """Get AI insights for user queries"""
    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    insights = generate_ai_insights(query)
    return {
        "query": query,
        "insights": insights,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Horse Racing Dashboard API",
        "version": "4.0",
        "ai_enabled": ai_enabled,
        "total_races": len(SAMPLE_RACES),
        "total_tracks": sum(len(tracks) for tracks in AUSTRALIAN_TRACKS.values())
    }


# ========================================
# Helper Functions
# ========================================

def extract_time(race_name: str) -> str:
    """Extract time from race name (e.g., '2:15 PM' from 'Royal Randwick - 2:15 PM')"""
    match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))', race_name)
    return match.group(1) if match else None


def parse_time_to_minutes(time_str: str) -> int:
    """Convert time string to minutes since midnight"""
    match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)', time_str)
    if not match:
        return 0
    
    hours, minutes, period = match.groups()
    hours = int(hours)
    minutes = int(minutes)
    
    if period.upper() == 'PM' and hours != 12:
        hours += 12
    elif period.upper() == 'AM' and hours == 12:
        hours = 0
    
    return hours * 60 + minutes


def is_time_in_range(time_str: str, time_from: str, time_to: str) -> bool:
    """Check if time is within range"""
    time_minutes = parse_time_to_minutes(time_str)
    from_minutes = parse_time_to_minutes(time_from)
    to_minutes = parse_time_to_minutes(time_to)
    
    return from_minutes <= time_minutes <= to_minutes


def is_time_after(time_str: str, time_from: str) -> bool:
    """Check if time is after given time"""
    time_minutes = parse_time_to_minutes(time_str)
    from_minutes = parse_time_to_minutes(time_from)
    return time_minutes >= from_minutes


def is_time_before(time_str: str, time_to: str) -> bool:
    """Check if time is before given time"""
    time_minutes = parse_time_to_minutes(time_str)
    to_minutes = parse_time_to_minutes(time_to)
    return time_minutes <= to_minutes


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
