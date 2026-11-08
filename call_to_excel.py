#!/usr/bin/env python3
"""
call_to_excel.py - Call recording (or transcript) -> Excel summary sheet.

Fully offline: this program makes no network calls. Fields are pulled out with plain
regex and keyword rules, and audio is converted to text by a local speech model
(faster-whisper) loaded from a folder on disk. A .txt transcript needs no speech model.

Columns: Name | Phone | Email | Objectives | Budget | Follow-up | Action Items

  Setup (once, needs internet):  pip install openpyxl faster-whisper
                                 python download_model.py medium
  Run (offline):                 python call_to_excel.py call1.mp3 notes.txt --out leads.xlsx
"""

import argparse
import re
import sys
from functools import lru_cache
from pathlib import Path

from openpyxl import Workbook, load_workbook

COLUMNS = ["Name", "Phone", "Email", "Objectives", "Budget", "Follow-up", "Action Items"]
NA = "Not mentioned"

# sentence keywords per field, plus max words kept
RULES = {
    "objectives": (r"looking for|looking to|want|need|require|interested in|goal|objective|plan to|prefer", 20),
    "followup": (r"follow up|follow-up|call (?:you )?back|touch base|next week|tomorrow|schedule|meet(?:ing)?\b|"
                 r"monday|tuesday|wednesday|thursday|friday|by (?:end of|next)", 15),
    "actions": (r"\b(?:i'll|i will|we'll|we will|please|can you|could you)\b|\bsend\b|\bshare\b|"
                r"\bprepare\b|\bdraft\b|\breview\b|\barrange\b", 25),
}

# --- names ---------------------------------------------------------------------------
TITLE = r"(?:(?:Mr|Mrs|Ms|Dr)\.?\s+)?"
PERSON = r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)"
NAME_RES = [  # tried in order: self-introduction, then a greeting such as "Hello Jim Costanzo,"
    re.compile(r"\b(?i:my name is|this is|i am|i'm|name's)\s+" + TITLE + PERSON),
    re.compile(r"\b(?i:hello|hi|hey|dear|good\s+(?:morning|afternoon|evening))\b,?\s+" + TITLE + PERSON),
]
NOT_NAMES = {"This", "There", "Thank", "Thanks", "I", "My", "It", "Okay", "Ok", "Yes", "Sorry"}

# --- phone / email -------------------------------------------------------------------
PHONE_RE = re.compile(r"\(?\b\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
SPELLED_RE = re.compile(r"\b(?:[A-Za-z]-){2,}[A-Za-z]\b")  # E-G-A-R-D -> egard
DOMAIN = r"[A-Za-z0-9-]+(?:(?:\s+dot\s+|\.)[A-Za-z]+)+"  # gmail.com / gmail dot com
SPOKEN_EMAIL_RE = re.compile(r"([\w.+-]+(?:\s\d+)?)\s+at\s+(" + DOMAIN + ")", re.I)  # "name 85 at gmail.com"

# --- money ---------------------------------------------------------------------------
NUMBER_WORDS = ("zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
                "sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|point")
UNITS = dict(zip("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
                 "sixteen seventeen eighteen nineteen".split(), range(20)))
TENS = dict(zip("twenty thirty forty fifty sixty seventy eighty ninety".split(), range(20, 100, 10)))
SCALES = {"thousand": 10**3, "million": 10**6, "billion": 10**9}
MONEY = (r"(?:\$\s?\d[\d,]*(?:\.\d+)?\s?(?:k|m|million|thousand|billion)?(?:\s?(?:per|/)\s?(?:sq\.?\s?ft|sf|month|year))?"
         r"|\b\d[\d,.]*\s?(?:million|thousand|dollars)\b"
         rf"|\b(?:{NUMBER_WORDS})(?:[\s-]+(?:{NUMBER_WORDS}))*\s+(?:million|billion|thousand)(?:\s+dollars)?\b)")
MONEY_RE = re.compile(MONEY, re.I)
# an amount introduced by a budget-style phrase; the LAST one wins (latest position in a negotiation)
BUDGET_RE = re.compile(r"(?:budget(?:\s+(?:of|is|up\s+to))?|up\s+to|total(?:\s+of)?|max(?:imum)?(?:\s+of)?|"
                       r"no\s+more\s+than|cap(?:ped)?\s+at)\s+(" + MONEY + ")", re.I)

# where a long sentence is cut so the answer stays short ("..., and you're looking to ...")
CUT_RE = re.compile(r";|,?\s+(?:and|but|so)\s+(?:you|i|we|they|in)\b", re.I)


@lru_cache(maxsize=None)
def load_model(folder: str):
    folder_path = Path(folder)
    if not (folder_path / "model.bin").exists():
        sys.exit(f"Speech model not found in '{folder}'.\n"
                 f"Run once (needs internet):  python download_model.py medium")
    from faster_whisper import WhisperModel  # imported lazily: only audio needs it
    print(f"Loading local speech model from {folder} ...", flush=True)
    model = WhisperModel(folder, compute_type="int8", local_files_only=True)
    print("Model ready.", flush=True)
    return model


def transcribe(path: Path, model_name: str) -> str:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")
    segments, info = load_model(model_name).transcribe(str(path), vad_filter=True)
    print(f"Transcribing {path.name} ({info.duration / 60:.1f} min of audio)...", flush=True)
    parts = []
    for seg in segments:
        parts.append(seg.text.strip())
        print(f"  {seg.end / info.duration:4.0%}  {seg.end:7.0f}s", end="\r", flush=True)
    print(" " * 30, end="\r")
    return " ".join(parts)


def shorten(text: str, max_words: int) -> str:
    words = text.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")


def pick(sentences, pattern, max_words, limit=2, last=False):
    """`limit` sentences matching `pattern` (first ones, or last ones if last=True).
    Each is trimmed to start at the keyword, cut at the first clause break, and shortened."""
    hits = []
    for s in sentences:
        m = re.search(pattern, s, re.I)
        if m:
            phrase = CUT_RE.split(s[m.start():])[0].strip(" ,")
            hits.append(shorten(phrase, max_words))
    hits = hits[-limit:] if last else hits[:limit]
    return "; ".join(hits) or NA


def words_to_dollars(words: str) -> str:
    """'seven million dollars' -> '$7,000,000';  'one point five million' -> '$1,500,000'."""
    tokens = [t for t in re.split(r"[\s-]+", words.lower()) if t != "dollars"]
    scale = SCALES[tokens.pop()]

    def whole(ts):
        total = 0
        for t in ts:
            if t == "hundred":
                total = (total or 1) * 100
            else:
                total += UNITS.get(t, 0) + TENS.get(t, 0)
        return total

    if "point" in tokens:
        i = tokens.index("point")
        value = whole(tokens[:i]) + float("0." + "".join(str(UNITS.get(t, 0)) for t in tokens[i + 1:]))
    else:
        value = whole(tokens)
    return f"${round(value * scale):,}"


def money_text(amount: str) -> str:
    amount = amount.strip()
    return words_to_dollars(amount) if amount[0].isalpha() else amount


def spoken_email(m) -> str:
    local = m.group(1).replace(" ", "")
    domain = re.sub(r"\s+dot\s+", ".", m.group(2), flags=re.I)
    return f"{local}@{domain}"


def find_name(text: str) -> str:
    for rx in NAME_RES:
        for m in rx.finditer(text):
            if m.group(1).split()[0] not in NOT_NAMES:
                return m.group(1)
    return NA


def extract(text: str) -> list:
    # spelled-out letters ("E-G-A-R-D") and spoken emails ("name at gmail dot com") -> real text
    text = SPELLED_RE.sub(lambda m: m.group(0).replace("-", "").lower(), text)
    text = SPOKEN_EMAIL_RE.sub(spoken_email, text)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    phone = PHONE_RE.search(text)
    email = EMAIL_RE.search(text)

    # budget: the last "budget / up to / total of ..." amount; otherwise amounts in the last money sentence
    budget = NA
    keyed = BUDGET_RE.findall(text)
    if keyed:
        budget = money_text(keyed[-1])
    else:
        money = [s for s in sentences if MONEY_RE.search(s)]
        if money:
            budget = ", ".join(dict.fromkeys(money_text(m.group(0)) for m in MONEY_RE.finditer(money[-1])))

    return [
        find_name(text),
        phone.group(0) if phone else NA,
        email.group(0) if email else NA,
        pick(sentences, *RULES["objectives"]),
        budget,
        pick(sentences, *RULES["followup"], limit=1, last=True),
        pick(sentences, *RULES["actions"], limit=3),
    ]


def main():
    ap = argparse.ArgumentParser(description="Call recording/transcript -> Excel summary")
    ap.add_argument("inputs", nargs="+", type=Path, help="audio files or .txt transcripts")
    ap.add_argument("--out", type=Path, default=Path("call_summaries.xlsx"))
    ap.add_argument("--model", default="models/medium",
                    help="local model folder created by download_model.py (default: models/medium)")
    args = ap.parse_args()

    if args.out.exists():
        wb = load_workbook(args.out)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(COLUMNS)

    errors = 0
    for path in args.inputs:
        try:
            text = transcribe(path, args.model)
            if path.suffix.lower() != ".txt":  # audio input: keep the transcript next to it
                out_txt = path.with_name(f"{path.stem}_transcript.txt")
                out_txt.write_text(text, encoding="utf-8")
                print(f"transcript saved: {out_txt}")
            ws.append(extract(text))
            print(f"done: {path.name}")
        except Exception as e:
            print(f"error: {path.name}: {e}", file=sys.stderr)
            errors += 1

    wb.save(args.out)
    print(f"Saved {args.out}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()