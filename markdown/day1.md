GTA Content Engine — Project Overview (Month 1)
A clear, durable reference for the entire system and current progress.
1. Project Goal
Build a GTA VI content machine capable of producing 2–4 high‑quality videos/day, using a simple Month 1 pipeline:
Trend → Idea/Script → Content Brief → Edit → You Review → Manual Post
Automation comes later.
Quality comes first.
2. Month 1 Objective
Produce one complete GTA VI video end‑to‑end, using the pipeline below:
Code
GTA VI trends
     ↓
Trend Module
     ↓
5–10 ideas
     ↓
Idea/Script Module
     ↓
1 Content Brief
     ↓
Edit Module
     ↓
1 finished Short
     ↓
YOU REVIEW
     ↓
Manual posting

This proves the system works before scaling.
3. Month 1 Modules
A. Trend Module
Purpose: Identify GTA VI topics worth making content about.
Outputs:
5–10 trend ideas
Trend score (Velocity × Relevance × Novelty)
Short explanation of why each trend matters
Status: To be built on Day 3
B. Idea + Script Module
Purpose: Turn a trend into:
Hooks
Concepts
Script
Recommended footage
Format selection
Outputs:
A Content Brief JSON
Status: To be built on Day 4–5
C. Edit Module
Purpose: Convert the Content Brief into a finished video.
Tasks:
Load footage
Cut clips
Add captions
Add voiceover
Add music
Format 9:16
Export MP4
Status: Manual editing first → automation later (Day 6+)
4. Content Brief (Core Contract)
Every video is defined by a single JSON file:
json
{
  "title": "GTA VI Detail Nobody Noticed",
  "format": "discovery",
  "hook": "Nobody noticed this GTA VI detail...",
  "script": "...",
  "length": 38,
  "footage": ["trailer_clip_01", "trailer_clip_02"],
  "voice": "energetic"
}

This is the bridge between the Script Module and Edit Module.
5. Format Library
Located in /formats/.
Initial formats:
breakdown
theory
discovery
meme
reaction
Each format defines:
structure
hook styles
pacing
length
Status: To be created on Day 2–3
6. Folder Structure (Completed Day 1)
Code
GTAContentEngine/
│
├── app/
│   ├── trend_module/
│   ├── script_module/
│   └── edit_module/
│
├── data/
│   ├── trends/
│   ├── ideas/
│   ├── rejected/
│   └── content_briefs/
│
├── media/
│   ├── raw/
│   ├── voice/
│   └── final/
│
├── formats/
├── database/
├── config/
│
├── .env
├── .gitignore
├── requirements.txt
├── main.py
└── MANIFESTO.txt

Status: DONE
7. Environment Setup (Completed Day 1)
Python virtual environment created
.env created
.gitignore configured
requirements.txt initialized
main.py runs successfully
Git repository initialized
Status: DONE
8. What NOT to Build in Month 1
To avoid complexity and delays:
❌ No publishing agent
❌ No analytics agent
❌ No optimization agent
❌ No Baby Universe account
❌ No experimental account
❌ No PostgreSQL
❌ No LangChain/LangGraph
❌ No multi-agent orchestration
❌ No auto-posting
❌ No complex dashboards
Month 1 is about one working pipeline, not a full AI company.
9. Day-by-Day Plan (Month 1)
Day 0 — DONE
GTA VI Channel Manifesto
Brand identity
Content style rules
Day 1 — DONE
Project folder structure
Virtual environment
Git setup
Basic main.py
Requirements file
.env
.gitignore
Day 2
Format Library
Brand rules
First manual trend list
Day 3
Trend Module (simple version)
Trend scoring
Day 4
Idea Module
Hook generation
Concept generation
Day 5
Script Module
Content Brief JSON generation
Day 6
Manual editing of first video
Collect editing requirements
Day 7
Review pipeline
Improve modules
Prepare for automation
10. Month 1 Milestone
By the end of Month 1, you should be able to run:
Code
python main.py

And get:
A trend
5–10 ideas
A selected concept
A generated script
A content brief
A manually edited video
A posted GTA VI short
This proves the pipeline works.
11. Month 2 Preview (Not part of Month 1)
Automate editing
Add Quality Module
Add Publishing Module
Add Analytics Module
Begin Baby Universe development
12. Guiding Principle
Don’t automate anything until you’ve proven it’s worth automating.
This keeps the project fast, simple, and successful.













