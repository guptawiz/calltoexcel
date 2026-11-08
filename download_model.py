#!/usr/bin/env python3
"""
download_model.py - ONE-TIME setup step. Needs internet.

Downloads a speech-to-text model into a local folder. After this, call_to_excel.py
runs fully offline and never touches the network. You can run this on any machine
and copy the resulting folder to the offline one.

Usage:

cd ~/call-summary
python3 -m venv venv
source venv/bin/activate
python -m pip install faster-whisper openpyxl
python download_model.py medium

Check that it worked

python -c "import faster_whisper; print('ok')"
"""

import argparse
from pathlib import Path

from faster_whisper.utils import download_model

ap = argparse.ArgumentParser(description="Download a speech model for offline use")
ap.add_argument("size", choices=["tiny", "base", "small", "medium"], help="model size")
ap.add_argument("--dir", type=Path, default=Path("models"), help="parent folder (default: ./models)")
args = ap.parse_args()

target = args.dir / args.size
target.mkdir(parents=True, exist_ok=True)
download_model(args.size, output_dir=str(target))
print(f"Model saved to {target.resolve()}")
print(f"Use it with: python call_to_excel.py call.mp3 --model {target}")


"""
*** sample output ***
cd call-summary
➜  call-summary python3 -m venv venv
source venv/bin/activate
(venv) ➜  call-summary python -m pip install faster-whisper openpyxl
python download_model.py base
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: faster-whisper in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (1.2.1)
Requirement already satisfied: openpyxl in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (3.1.5)
Requirement already satisfied: tqdm in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from faster-whisper) (4.70.1)
Requirement already satisfied: av>=11 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from faster-whisper) (15.1.0)
Requirement already satisfied: tokenizers<1,>=0.13 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from faster-whisper) (0.22.2)
Requirement already satisfied: ctranslate2<5,>=4.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from faster-whisper) (4.8.5)
Requirement already satisfied: huggingface-hub>=0.21 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from faster-whisper) (1.8.0)
Requirement already satisfied: onnxruntime<2,>=1.14 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from faster-whisper) (1.19.2)
Requirement already satisfied: et-xmlfile in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from openpyxl) (2.0.0)
Requirement already satisfied: numpy in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from ctranslate2<5,>=4.0->faster-whisper) (2.0.2)
Requirement already satisfied: pyyaml<7,>=5.3 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from ctranslate2<5,>=4.0->faster-whisper) (6.0.3)
Requirement already satisfied: typing-extensions>=4.1.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from huggingface-hub>=0.21->faster-whisper) (4.15.0)
Requirement already satisfied: packaging>=20.9 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from huggingface-hub>=0.21->faster-whisper) (25.0)
Requirement already satisfied: filelock>=3.10.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from huggingface-hub>=0.21->faster-whisper) (3.19.1)
Requirement already satisfied: hf-xet<2.0.0,>=1.4.2 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from huggingface-hub>=0.21->faster-whisper) (1.8.0)
Requirement already satisfied: typer in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from huggingface-hub>=0.21->faster-whisper) (0.23.2)
Requirement already satisfied: httpx<1,>=0.23.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from huggingface-hub>=0.21->faster-whisper) (0.28.1)
Requirement already satisfied: fsspec>=2023.5.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from huggingface-hub>=0.21->faster-whisper) (2025.10.0)
Requirement already satisfied: certifi in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from httpx<1,>=0.23.0->huggingface-hub>=0.21->faster-whisper) (2025.10.5)
Requirement already satisfied: httpcore==1.* in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from httpx<1,>=0.23.0->huggingface-hub>=0.21->faster-whisper) (1.0.9)
Requirement already satisfied: idna in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from httpx<1,>=0.23.0->huggingface-hub>=0.21->faster-whisper) (3.11)
Requirement already satisfied: anyio in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from httpx<1,>=0.23.0->huggingface-hub>=0.21->faster-whisper) (4.12.1)
Requirement already satisfied: h11>=0.16 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from httpcore==1.*->httpx<1,>=0.23.0->huggingface-hub>=0.21->faster-whisper) (0.16.0)
Requirement already satisfied: protobuf in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from onnxruntime<2,>=1.14->faster-whisper) (6.33.6)
Requirement already satisfied: coloredlogs in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from onnxruntime<2,>=1.14->faster-whisper) (15.0.1)
Requirement already satisfied: sympy in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from onnxruntime<2,>=1.14->faster-whisper) (1.14.0)
Requirement already satisfied: flatbuffers in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from onnxruntime<2,>=1.14->faster-whisper) (25.12.19)
Requirement already satisfied: exceptiongroup>=1.0.2 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from anyio->httpx<1,>=0.23.0->huggingface-hub>=0.21->faster-whisper) (1.3.0)
Requirement already satisfied: humanfriendly>=9.1 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from coloredlogs->onnxruntime<2,>=1.14->faster-whisper) (10.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from sympy->onnxruntime<2,>=1.14->faster-whisper) (1.3.0)
Requirement already satisfied: click>=8.0.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from typer->huggingface-hub>=0.21->faster-whisper) (8.1.8)
Requirement already satisfied: rich>=12.3.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from typer->huggingface-hub>=0.21->faster-whisper) (15.0.0)
Requirement already satisfied: annotated-doc>=0.0.2 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from typer->huggingface-hub>=0.21->faster-whisper) (0.0.5)
Requirement already satisfied: shellingham>=1.3.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from typer->huggingface-hub>=0.21->faster-whisper) (1.5.4)
Requirement already satisfied: pygments<3.0.0,>=2.13.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from rich>=12.3.0->typer->huggingface-hub>=0.21->faster-whisper) (2.19.2)
Requirement already satisfied: markdown-it-py>=2.2.0 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from rich>=12.3.0->typer->huggingface-hub>=0.21->faster-whisper) (3.0.0)
Requirement already satisfied: mdurl~=0.1 in /Users/prashantgupta/Library/Python/3.9/lib/python/site-packages (from markdown-it-py>=2.2.0->rich>=12.3.0->typer->huggingface-hub>=0.21->faster-whisper) (0.1.2)
...
Model saved to .../call-summary/models/base
Use it with: python call_to_excel.py call.mp3 --model models/base
(venv) ➜  call-summary
"""
