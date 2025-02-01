from pydantic import BaseModel

class SentimentRequest(BaseModel):
    text: str
    context: str = "cryptocurrency market analysis"

class SentimentResponse(BaseModel):
    sentiment: str  # Positive, Neutral, Negative
    confidence: float
    key_terms: list[str]
    summary: str