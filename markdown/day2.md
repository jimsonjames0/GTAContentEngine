GTA Content Engine — Project Overview (Month 1)
A complete snapshot of the idea, architecture, and current progress.
1. Vision
Build a GTA VI media brand powered by a simple Month‑1 pipeline:
Trend → Idea/Script → Content Brief → Edit → You Review → Manual Post
The goal for Month 1 is one complete, high‑quality video produced end‑to‑end.
Automation comes later.
2. Month 1 Objective
Create a working content engine capable of producing 2–4 good videos/day, even if you only produce 1/day during Month 1.
The Month 1 pipeline:
Code
GTA VI trends
     ↓
Trend Module
     ↓
5–10 ideas
     ↓
Idea + Script Module
     ↓
Content Brief
     ↓
Edit Module
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
Trend score
Short explanation of relevance
Status: Scheduled for Day 3
B. Idea + Script Module
Purpose: Turn a trend into:
hooks
concepts
selected format
script
recommended footage
Outputs:
Content Brief JSON
Status:
Day 4 → ideas + format selection
Day 5 → script + content brief
C. Edit Module
Purpose: Convert the Content Brief into a finished video.
Tasks:
load footage
cut clips
add captions
add voiceover
add music
format 9:16
export MP4
Status:
Manual editing first → automation later.
4. Content Brief (Core Contract)
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

This is the bridge between the Idea + Script Module and the Edit Module.
5. Format Library (Completed Day 2)
Located in /formats/.
Five formats:
breakdown
theory
discovery
meme
reaction
Each format includes:
name
recommended length
structure
hook styles
editing_style
Example:
json
{
  "name": "discovery",
  "length": "20-40",
  "structure": [
    "hook",
    "show_discovery",
    "explain",
    "impact"
  ],
  "hook_styles": [
    "Nobody is talking about this...",
    "Look at this GTA VI detail..."
  ],
  "editing_style": {
    "pace": "fast",
    "caption_style": "highlighted",
    "visual_changes": "frequent"
  }
}

Status: DONE
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
Virtual environment created
.env created
.gitignore configured
requirements.txt initialized
main.py runs
Git repository initialized
Status: DONE
8. What We Are Not Building in Month 1
To avoid complexity:
❌ No publishing agent
❌ No analytics agent
❌ No optimization agent
❌ No Baby Universe account
❌ No experimental account
❌ No PostgreSQL
❌ No LangChain/LangGraph
❌ No multi-agent orchestration
❌ No auto-posting
❌ No dashboards
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
Day 2 — DONE
Format Library created
Five formats with editing_style
Day 3
Build Trend Module
Trend scoring
First trend inputs
Day 4
Build Idea + Script Module foundation
Generate hooks
Generate concepts
Select format
Day 5
Generate script
Generate Content Brief JSON
Validate Content Brief
Day 6
Manual editing of first video
Collect editing requirements
Day 7
Review pipeline
Improve modules
Prepare for automation
10. Month 1 Milestone
By the end of Month 1, the architecture should allow:
Code
python main.py

to orchestrate:
Trend → Ideas → Script → Content Brief
Edit → Review → Manual Post
But we do not build full orchestration yet.
We build modules independently and connect them only once they work.
11. Month 2 Preview
(Not part of Month 1)
Automate editing
Add Quality Module
Add Publishing Module
Add Analytics Module
Begin Baby Universe development
12. Guiding Principle
Don’t automate anything until you’ve proven it’s worth automating.
This keeps the project fast, simple, and successful.

