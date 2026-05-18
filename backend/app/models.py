from pydantic import BaseModel, Field, model_validator


class BeatRequest(BaseModel):
    prompt: str = Field(default="", description="Natural language beat description")
    bars: int = Field(default=8, ge=4, le=32)
    open_in_logic: bool = Field(default=True)
    lucky: bool = Field(default=False, description="Roll a random genre, BPM, and mood")

    @model_validator(mode="after")
    def require_prompt_unless_lucky(self) -> "BeatRequest":
        if not self.lucky and len(self.prompt.strip()) < 3:
            raise ValueError("prompt must be at least 3 characters")
        return self


class BeatSpec(BaseModel):
    genre: str = "rnb"
    bpm: int = 120
    key: str = "A"
    scale: str = "minor"
    instruments: list[str] = Field(default_factory=lambda: ["kick", "snare", "hihat", "bass", "synth"])
    bars: int = 8
    mood: str = "smooth"
    variation: int = 0  # hash of prompt — picks drum/progression variants


class BeatResponse(BaseModel):
    spec: BeatSpec
    midi_path: str
    track_paths: dict[str, str]
    message: str
    adjustments: list[str] = Field(default_factory=list)
    original_prompt: str = ""
