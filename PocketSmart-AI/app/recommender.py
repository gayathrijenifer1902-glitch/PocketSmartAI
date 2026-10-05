import json
from typing import Any
from .config import settings

def _fallback(kind: str, data: dict[str, Any]) -> dict:
    budget = float(data["budget"])
    if kind == "home":
        labels = [("Furniture", .45, "IKEA / Amazon"), ("Lighting", .2, "IKEA / Amazon"), ("Decor", .2, "Amazon / Flipkart"), ("Contingency", .15, "Keep unspent")]
        context = f"{', '.join(data['rooms'])} in a {data['style']} style"
    elif kind == "party":
        labels = [("Catering", .45, "Swiggy / Zomato"), ("Venue", .25, "OYO / local venues"), ("Decor", .18, "Amazon / local vendors"), ("Entertainment", .12, "Local performers")]
        context = f"{data['event_type']} for {data['guests']} guests" + (f" at {data['venue']}" if data.get('venue') else "")
    else:
        labels = [("Main piece", .55, "Amazon / Flipkart"), ("Complementary pieces", .25, "Local jeweler"), ("Finishing & gift box", .1, "Amazon"), ("Reserve", .1, "Keep unspent")]
        context = f"{data['style']} jewelry for {data['occasion']}" + (f"; outfit: {data['outfit_description']}" if data.get('outfit_description') else "")
    items = [{"category": n, "allocation": round(budget*p,2), "platform": platform, "tip": f"Compare {n.lower()} listings and keep the total within its allocation."} for n,p,platform in labels]
    return {"planner": kind, "source": "fallback", "summary": f"A practical {kind} plan for {context}.", "budget": budget, "items": items, "advice": "Prices are planning estimates, not live listings. Confirm availability and final taxes before purchasing."}

def recommend(kind: str, data: dict, image_bytes: bytes | None = None) -> dict:
    fallback = _fallback(kind, data)
    if not settings.gemini_api_key: return fallback
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = "Return only JSON with keys summary, items (array of category, allocation, platform, tip), and advice. Allocate no more than the stated budget. Do not claim live prices or availability. Planning input: " + json.dumps(data)
        contents: list = [prompt]
        if image_bytes: contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
        response = client.models.generate_content(model=settings.gemini_model, contents=contents, config=types.GenerateContentConfig(response_mime_type="application/json", temperature=.35))
        ai = json.loads(response.text)
        if not isinstance(ai.get("items"), list): raise ValueError("missing items")
        return {**fallback, **ai, "planner": kind, "budget": float(data['budget']), "source": "gemini"}
    except Exception:
        return fallback
