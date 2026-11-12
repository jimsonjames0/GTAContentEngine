from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List


@dataclass
class ContentBrief:
    # Legacy fields (kept for full backwards compatibility with Month 1 downstream modules)
    title: str
    format: str
    hook: str
    script: str
    length: int
    footage: List[str]
    voice: str = "energetic"

    # Month 2 editorial & traceability fields (defaults for legacy loading)
    central_angle: str = ""
    narration: str = ""
    verified_claims: List[str] = field(default_factory=list)
    speculation: List[str] = field(default_factory=list)
    source_references: List[str] = field(default_factory=list)
    visual_cues: List[str] = field(default_factory=list)
    payoff: str = ""
    call_to_action: str = ""
    model_id: str = "scriptwriter-v2-deterministic"
    prompt_version: str = "v2.0-editorial"
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    approval_status: str = "pending_review"

    VALID_FORMATS = {"breakdown", "theory", "discovery", "meme", "reaction"}

    @classmethod
    def create(
        cls,
        title: str,
        format: str,
        hook: str,
        script: str,
        length: int,
        footage: List[str],
        voice: str = "energetic",
        central_angle: str = "",
        narration: str = "",
        verified_claims: List[str] = None,
        speculation: List[str] = None,
        source_references: List[str] = None,
        visual_cues: List[str] = None,
        payoff: str = "",
        call_to_action: str = "",
        model_id: str = "scriptwriter-v2-deterministic",
        prompt_version: str = "v2.0-editorial",
        generated_at: str = None,
        approval_status: str = "pending_review",
    ):
        fmt = format.lower().strip()
        if fmt not in cls.VALID_FORMATS:
            raise ValueError(
                f"Invalid format '{format}'. Must be one of: {cls.VALID_FORMATS}"
            )

        if not title or not title.strip():
            raise ValueError("Title cannot be empty.")

        if not hook or not hook.strip():
            raise ValueError("Hook cannot be empty.")

        if not script or not script.strip():
            raise ValueError("Script cannot be empty.")

        if not isinstance(footage, list) or len(footage) == 0:
            raise ValueError("Footage must contain at least 1 valid string tag.")

        for tag in footage:
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError("All footage tags must be non-empty strings.")

        if not isinstance(length, int) or not (10 <= length <= 60):
            raise ValueError(f"Length must be an integer between 10 and 60 seconds inclusive, got {length}.")

        if not voice or not voice.strip():
            raise ValueError("Voice cannot be empty.")

        # Sync narration with script if not provided
        if not narration:
            narration = script.strip()

        # Sync visual_cues with footage if not provided
        if not visual_cues:
            visual_cues = [tag.strip() for tag in footage]

        now = generated_at or datetime.now(timezone.utc).isoformat()

        return cls(
            title=title.strip(),
            format=fmt,
            hook=hook.strip(),
            script=script.strip(),
            length=length,
            footage=[tag.strip() for tag in footage],
            voice=voice.strip(),
            central_angle=central_angle.strip(),
            narration=narration.strip(),
            verified_claims=verified_claims or [],
            speculation=speculation or [],
            source_references=source_references or [],
            visual_cues=[tag.strip() for tag in visual_cues],
            payoff=payoff.strip(),
            call_to_action=call_to_action.strip(),
            model_id=model_id.strip(),
            prompt_version=prompt_version.strip(),
            generated_at=now,
            approval_status=approval_status.strip(),
        )

    @property
    def footage_needed(self) -> List[str]:
        """Backwards-compatible alias for footage."""
        return self.footage

    @property
    def length_seconds(self) -> int:
        """Backwards-compatible alias for length."""
        return self.length
