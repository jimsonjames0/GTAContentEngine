import json
from pathlib import Path
from typing import Union, Dict, Any


class MetadataGenerator:

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]
        self.briefs_dir = self.root_dir / "data" / "content_briefs"
        self.metadata_dir = self.root_dir / "data" / "metadata"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def format_youtube_title(title: str, hook: str = "", fmt: str = "BREAKDOWN") -> str:
        clean = title.strip('"\'“”‘’ ')
        clean = clean.replace('“', '"').replace('”', '"')
        
        suffix = " | GTA 6 #Shorts"
        max_subject_len = 60 - len(suffix)  # 44 characters

        candidate = clean.strip().rstrip(".:!,; ")

        if len(candidate) > max_subject_len:
            truncated = candidate[:max_subject_len - 3]
            if " " in truncated:
                truncated = truncated.rsplit(" ", 1)[0]
            candidate = truncated.rstrip(",.:;! ") + "..."

        final_title = f"{candidate}{suffix}"
        if len(final_title) > 60:
            final_title = final_title[:57] + "..."

        return final_title

    def generate_metadata(
        self,
        brief_data: Union[dict, Path, str],
        brief_id: str = "short_001"
    ) -> Dict[str, Any]:
        """Generate platform-optimized metadata for YouTube Shorts, TikTok, and Instagram Reels."""
        if isinstance(brief_data, (str, Path)):
            brief_path = Path(brief_data)
            if not brief_path.is_absolute():
                brief_path = self.briefs_dir / brief_path
            with open(brief_path, "r", encoding="utf-8") as f:
                brief = json.load(f)
        elif isinstance(brief_data, dict):
            brief = brief_data
        elif hasattr(brief_data, "__dict__"):
            brief = brief_data.__dict__
        else:
            raise ValueError("Invalid brief_data format. Expected dict, Path, or object with attributes.")

        title = brief.get("title", "GTA VI Update")
        hook = brief.get("hook", "")
        fmt = brief.get("format", "breakdown").upper()

        # 1. YouTube Shorts: High-CTR descriptive title (<60 chars)
        yt_title = self.format_youtube_title(title, hook, fmt)

        yt_description = (
            f"{hook}\n\n"
            f"Format: {fmt}\n"
            f"Key Takeaways:\n"
            f"• What this means for the release of GTA VI\n"
            f"• Full breakdown of recent trailer and community findings\n"
            f"• Rockstar Games official community details\n\n"
            f"Subscribe for daily verified GTA VI news and frame breakdowns.\n\n"
            f"#GTA6 #GTAVI #RockstarGames #GamingNews #Shorts"
        )

        yt_tags = ["GTA6", "GTAVI", "RockstarGames", "GamingNews", "Shorts", fmt.lower()]

        # 2. TikTok: Punchy caption (<150 chars), engagement question, relevant tags
        tt_question = "Will you be playing on day one? Drop your thoughts below 👇"
        tt_caption = f"{hook} {tt_question} #gta6 #gtavi #rockstargames #gaming"
        if len(tt_caption) > 150:
            clean_subject = title.strip('"\'“”‘’ ')[:40]
            tt_caption = f"{clean_subject}... {tt_question} #gta6 #gtavi #gaming"[:145] + "..."

        # 3. Instagram Reels: Narrative caption with topic tags
        ig_caption = (
            f"{hook}\n\n"
            f"Here is everything you need to know about this latest GTA VI update. "
            f"Rockstar is raising the bar with world details and launch preparation.\n\n"
            f"Thoughts on this? Let us know in the comments!\n\n"
            f"#GTA6 #GTAVI #RockstarGames #ViceCity #GamingCommunity #Gamer #Reels"
        )

        # 4. Contextual Monetization & Affiliate Pinned Comment
        topic_lower = f"{title} {hook}".lower()
        if any(w in topic_lower for w in ["preload", "storage", "download", "size", "gb", "install"]):
            affiliate_cat = "console_storage_expansion"
            pinned_cta = "🚨 Preload files are massive—ensure your PS5 / console has at least 150GB ready! Check our top-rated high-speed SSDs in the bio link 👇"
        elif any(w in topic_lower for w in ["order", "store", "buy", "edition", "playstation"]):
            affiliate_cat = "preorder_giftcards"
            pinned_cta = "🎮 Which edition are you getting? Grab official PlayStation & Xbox digital gift cards via the link in our bio for instant delivery 👇"
        elif any(w in topic_lower for w in ["theory", "leak", "secret"]):
            affiliate_cat = "gaming_vpn_and_privacy"
            pinned_cta = "🔒 Protect your network and stay updated on the latest Vice City news. Check our verified community link in the bio 👇"
        else:
            affiliate_cat = "gaming_hardware"
            pinned_cta = "Will you be playing GTA VI on Day 1 on PS5, Xbox, or waiting for PC? Drop your setup below 👇"

        metadata = {
            "brief_id": brief_id,
            "original_title": title,
            "format": fmt,
            "platforms": {
                "youtube_shorts": {
                    "title": yt_title,
                    "description": yt_description,
                    "tags": yt_tags,
                },
                "tiktok": {
                    "caption": tt_caption,
                    "sound": "Original Voiceover",
                    "tags": ["gta6", "gtavi", "rockstargames", "gaming"],
                },
                "instagram_reels": {
                    "caption": ig_caption,
                    "tags": ["GTA6", "GTAVI", "RockstarGames", "ViceCity", "GamingCommunity"],
                },
            },
            "monetization": {
                "recommended_affiliate_category": affiliate_cat,
                "pinned_comment_cta": pinned_cta,
                "utm_campaign": f"gtavi_{brief_id}_{fmt.lower()}",
                "monetization_tier": "affiliate_and_shorts_revshare"
            }
        }

        out_file = self.metadata_dir / f"{brief_id}_metadata.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return metadata

