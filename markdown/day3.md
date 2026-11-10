Day 3 — Trend Module (Month 1)
The first intelligence component of the GTA Content Engine.

1. Goal of Day 3
Build the Trend Module, which transforms raw GTA VI topic information into:

structured trend records

scored trends

ranked trends

This module is intentionally simple.
We are not scraping the internet yet.
We are defining the structure and logic that future automation will plug into.

2. What a Trend Is
A Trend Record contains:

title — name of the trend

source — where it came from (reddit, YouTube, X, etc.)

url — link to the source

description — short summary

velocity — how fast the topic is rising (1–10)

relevance — how relevant it is to GTA VI (1–10)

novelty — how fresh/unique the angle is (1–10)

score — velocity × relevance × novelty

Example:

json
{
  "title": "New GTA VI trailer detail discovered",
  "source": "reddit",
  "url": "https://example.com",
  "description": "Players noticed a previously overlooked detail...",
  "velocity": 8,
  "relevance": 10,
  "novelty": 7,
  "score": 560
}
This structure separates raw information from our judgment.

3. Why These Three Scores?
Velocity (1–10)
How fast the topic is gaining attention.

Relevance (1–10)
How directly it relates to GTA VI.

Novelty (1–10)
How fresh the angle is.

Trend Score Formula
Code
Trend Score = Velocity × Relevance × Novelty
Example:

Code
8 × 10 × 7 = 560
This is not “truth.”
It’s a ranking mechanism to help decide which trends deserve attention.

4. Trend Module Code (Day 3)
Create:

app/trend_module/trend.py

python
from dataclasses import dataclass


@dataclass
class Trend:
    title: str
    source: str
    url: str
    description: str
    velocity: int
    relevance: int
    novelty: int
    score: int

    @classmethod
    def create(
        cls,
        title: str,
        source: str,
        url: str,
        description: str,
        velocity: int,
        relevance: int,
        novelty: int,
    ):
        # Validate score ranges
        scores = [velocity, relevance, novelty]
        if not all(1 <= score <= 10 for score in scores):
            raise ValueError("Velocity, relevance, and novelty must be between 1 and 10.")

        # Calculate trend score
        score = velocity * relevance * novelty

        return cls(
            title=title,
            source=source,
            url=url,
            description=description,
            velocity=velocity,
            relevance=relevance,
            novelty=novelty,
            score=score,
        )
5. Test File
Create:

app/trend_module/test_trend.py

python
from trend import Trend

trend = Trend.create(
    title="GTA VI detail discovered",
    source="reddit",
    url="https://example.com",
    description="Players discovered an interesting detail in the GTA VI trailer.",
    velocity=8,
    relevance=10,
    novelty=7,
)

print(trend)
print(f"Trend Score: {trend.score}")
Run:

Code
python test_trend.py
Expected output:

Code
Trend(title='GTA VI detail discovered', source='reddit', ...)
Trend Score: 560
6. What We Have Built Today
Your Trend Module now:

defines a Trend object

validates score ranges

calculates trend scores

produces structured trend records

can be tested independently

Folder structure now includes:

Code
app/
└── trend_module/
    ├── trend.py
    └── test_trend.py
Conceptually:

Code
Trend
  ↓
Velocity, Relevance, Novelty
  ↓
Trend Score
  ↓
Ranking
This is the foundation for future automation.

7. What Comes Next (Still Day 3)
After confirming the Trend object works:

Part B
Build a simple Trend Collector that accepts multiple trend records.

Part C
Sort and save the top trends into:

data/trends/

Only after this will we connect real trend sources.

This keeps Day 3 simple and focused.

8. Day 3 Definition of Done
You have completed Day 3 when:

Trend class exists

validation works

scoring works

test file runs

trend prints correctly

score prints correctly

No AI.
No scraping.
No APIs.
No agents.
No complexity.

Just a clean, testable module.