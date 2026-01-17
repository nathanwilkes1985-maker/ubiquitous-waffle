"""
Australian Horse Racing Betting Dashboard - FastAPI Backend v3.0
Enhanced with AI-powered predictions, analysis, and intelligent recommendations
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import json
import os
from openai import OpenAI

app = FastAPI(title="Horse Racing Dashboard API", version="3.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize OpenAI client
client = OpenAI()

# Enhanced sample data with detailed horse information
SAMPLE_RACES = [
    {
        "id": "hr1",
        "race": "Royal Randwick - 2:15 PM",
        "track": "Randwick",
        "state": "NSW",
        "distance": "1600m",
        "class": "Class 2",
        "prize": "$125,000",
        "going": "Good",
        "horses": [
            {
                "name": "Thunder Strike",
                "number": 1,
                "odds": 3.20,
                "place_odds": 1.60,
                "jockey": "James McDonald",
                "trainer": "Chris Waller",
                "weight": "58kg",
                "form": "2-1-3",
                "trend": "up",
                "trendValue": "+0.4"
            },
            {
                "name": "Dancing Flame",
                "number": 2,
                "odds": 2.80,
                "place_odds": 1.40,
                "jockey": "Hugh Bowman",
                "trainer": "Gai Waterhouse",
                "weight": "57kg",
                "form": "1-2-1",
                "trend": "down",
                "trendValue": "-0.2"
            },
            {
                "name": "Silver Bullet",
                "number": 3,
                "odds": 4.50,
                "place_odds": 1.80,
                "jockey": "Tommy Berry",
                "trainer": "Peter Snowden",
                "weight": "56kg",
                "form": "3-2-2",
                "trend": "stable",
                "trendValue": "0.0"
            },
            {
                "name": "Golden Phoenix",
                "number": 4,
                "odds": 5.50,
                "place_odds": 2.20,
                "jockey": "Blake Shinn",
                "trainer": "John O'Shea",
                "weight": "55kg",
                "form": "4-3-2",
                "trend": "up",
                "trendValue": "+0.6"
            }
        ],
        "featured": True
    },
    {
        "id": "hr2",
        "race": "Moonee Valley - 3:45 PM",
        "track": "Moonee Valley",
        "state": "VIC",
        "distance": "1400m",
        "class": "Class 3",
        "prize": "$95,000",
        "going": "Good to Firm",
        "horses": [
            {
                "name": "Silver Bullet",
                "number": 5,
                "odds": 2.50,
                "place_odds": 1.25,
                "jockey": "Damien Oliver",
                "trainer": "Darren Weir",
                "weight": "59kg",
                "form": "1-1-2",
                "trend": "up",
                "trendValue": "+0.8"
            },
            {
                "name": "Golden Phoenix",
                "number": 6,
                "odds": 3.50,
                "place_odds": 1.75,
                "jockey": "Craig Williams",
                "trainer": "Michael Kent",
                "weight": "58kg",
                "form": "2-1-3",
                "trend": "down",
                "trendValue": "-0.3"
            },
            {
                "name": "Midnight Runner",
                "number": 7,
                "odds": 4.50,
                "place_odds": 2.00,
                "jockey": "Zac Purton",
                "trainer": "David Brideoake",
                "weight": "57kg",
                "form": "3-2-1",
                "trend": "up",
                "trendValue": "+0.5"
            },
            {
                "name": "Royal Ascot",
                "number": 8,
                "odds": 6.00,
                "place_odds": 2.40,
                "jockey": "Mark Zahra",
                "trainer": "Mick Price",
                "weight": "56kg",
                "form": "4-3-2",
                "trend": "stable",
                "trendValue": "0.0"
            }
        ],
        "featured": False
    },
    {
        "id": "hr3",
        "race": "Flemington - 4:30 PM",
        "track": "Flemington",
        "state": "VIC",
        "distance": "2000m",
        "class": "Class 1",
        "prize": "$150,000",
        "going": "Good",
        "horses": [
            {
                "name": "Midnight Runner",
                "number": 9,
                "odds": 4.50,
                "place_odds": 2.25,
                "jockey": "Brett Prebble",
                "trainer": "Anthony Cummings",
                "weight": "60kg",
                "form": "1-2-1",
                "trend": "up",
                "trendValue": "+0.9"
            },
            {
                "name": "Starlight Express",
                "number": 10,
                "odds": 1.95,
                "place_odds": 0.97,
                "jockey": "Kerrin McEvoy",
                "trainer": "Gai Waterhouse",
                "weight": "59kg",
                "form": "1-1-1",
                "trend": "up",
                "trendValue": "+1.2"
            },
            {
                "name": "Royal Ascot",
                "number": 11,
                "odds": 2.25,
                "place_odds": 1.07,
                "jockey": "William Pike",
                "trainer": "Chris Waller",
                "weight": "58kg",
                "form": "2-1-2",
                "trend": "down",
                "trendValue": "-0.4"
            },
            {
                "name": "Thunder Strike",
                "number": 12,
                "odds": 3.75,
                "place_odds": 1.65,
                "jockey": "Corey Brown",
                "trainer": "Peter Snowden",
                "weight": "57kg",
                "form": "3-2-1",
                "trend": "stable",
                "trendValue": "0.0"
            }
        ],
        "featured": True
    },
    {
        "id": "hr4",
        "race": "Caulfield - 5:15 PM",
        "track": "Caulfield",
        "state": "VIC",
        "distance": "1200m",
        "class": "Class 2",
        "prize": "$110,000",
        "going": "Firm",
        "horses": [
            {
                "name": "Royal Ascot",
                "number": 13,
                "odds": 2.15,
                "place_odds": 1.07,
                "jockey": "Damien Oliver",
                "trainer": "John O'Shea",
                "weight": "59kg",
                "form": "1-1-2",
                "trend": "up",
                "trendValue": "+0.7"
            },
            {
                "name": "Lightning Storm",
                "number": 14,
                "odds": 4.20,
                "place_odds": 2.10,
                "jockey": "James McDonald",
                "trainer": "Darren Weir",
                "weight": "58kg",
                "form": "2-3-1",
                "trend": "down",
                "trendValue": "-0.5"
            },
            {
                "name": "Starlight Express",
                "number": 15,
                "odds": 3.00,
                "place_odds": 1.50,
                "jockey": "Craig Williams",
                "trainer": "Michael Kent",
                "weight": "57kg",
                "form": "1-2-2",
                "trend": "up",
                "trendValue": "+0.3"
            },
            {
                "name": "Dancing Flame",
                "number": 16,
                "odds": 5.00,
                "place_odds": 2.00,
                "jockey": "Hugh Bowman",
                "trainer": "Chris Waller",
                "weight": "56kg",
                "form": "3-2-3",
                "trend": "stable",
                "trendValue": "0.0"
            }
        ],
        "featured": False
    }
]

MARKET_MOVERS = [
    {
        "rank": 1,
        "horse": "Thunder Strike",
        "track": "Randwick",
        "movement": "+0.40",
        "direction": "up",
        "current_odds": 3.20,
        "previous_odds": 2.80,
        "volume": "High"
    },
    {
        "rank": 2,
        "horse": "Starlight Express",
        "track": "Flemington",
        "movement": "+1.20",
        "direction": "up",
        "current_odds": 1.95,
        "previous_odds": 1.50,
        "volume": "Very High"
    },
    {
        "rank": 3,
        "horse": "Golden Phoenix",
        "track": "Moonee Valley",
        "movement": "-0.30",
        "direction": "down",
        "current_odds": 3.50,
        "previous_odds": 3.80,
        "volume": "Medium"
    },
    {
        "rank": 4,
        "horse": "Lightning Storm",
        "track": "Caulfield",
        "movement": "-0.50",
        "direction": "down",
        "current_odds": 4.20,
        "previous_odds": 4.70,
        "volume": "Medium"
    }
]

PREDICTIONS = [
    {
        "rank": 1,
        "horse": "Thunder Strike",
        "track": "Randwick",
        "confidence": 87,
        "prediction": "Strong Recent Form",
        "analysis": "Excellent track record at Randwick with consistent wins. Form line shows 2-1-3 with recent improvement.",
        "tip": "WIN"
    },
    {
        "rank": 2,
        "horse": "Silver Bullet",
        "track": "Moonee Valley",
        "confidence": 82,
        "prediction": "Consistent Performer",
        "analysis": "Reliable performer with 1-1-2 form. Favorable track conditions expected.",
        "tip": "PLACE"
    },
    {
        "rank": 3,
        "horse": "Starlight Express",
        "track": "Flemington",
        "confidence": 91,
        "prediction": "Strong Favorite",
        "analysis": "Exceptional form with 1-1-1 record. Top jockey and trainer combination. Odds value.",
        "tip": "WIN"
    },
    {
        "rank": 4,
        "horse": "Royal Ascot",
        "track": "Caulfield",
        "confidence": 78,
        "prediction": "Good Value Bet",
        "analysis": "Solid performer with improving form. Good odds for the quality of horse.",
        "tip": "EACH WAY"
    }
]


# ========================================
# AI Functions
# ========================================

def generate_ai_prediction(race_data: dict) -> dict:
    """Generate AI-powered prediction for a race using OpenAI"""
    try:
        # Format race data for AI analysis
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
        
        # Parse AI response
        ai_response = response.choices[0].message.content
        
        # Try to extract JSON from response
        try:
            import re
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
        "version": "3.0"
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


@app.get("/api/racecourses")
async def get_racecourses():
    """Get list of Australian racecourses"""
    return {
        "racecourses": [
            {"name": "Randwick", "state": "NSW", "code": "RAN"},
            {"name": "Moonee Valley", "state": "VIC", "code": "MVL"},
            {"name": "Flemington", "state": "VIC", "code": "FLE"},
            {"name": "Caulfield", "state": "VIC", "code": "CAU"}
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Horse Racing Dashboard API",
        "version": "3.0",
        "ai_enabled": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
