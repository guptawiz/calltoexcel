# Call Recording to Excel Summary Tool

Turns a recorded phone call into one row in an Excel sheet: who the contact is, what they want, their budget, and what happens next.

Everything runs on your own computer. After a one-time setup, it needs no internet and no AI service, so recordings never leave your machine.

## What you get

One row per call, with seven columns. If something is not said in the call, the cell reads "Not mentioned".

| Column | What goes in it | Example |
| --- | --- | --- |
| Name | The contact's name | Jim Costanzo |
| Phone | The phone number | 408-825-3243 |
| Email | The email address | egarduno85@gmail.com |
| Objectives | What the client wants (short) | looking to sell your McDonald's for five million dollars in Belfour, California |
| Budget | The latest money figure discussed | $7,000,000 |
| Follow-up | The next contact or meeting (short) | follow up with you December 5th, 2026 |
| Action items | Concrete tasks to do (short) | I will send you some comps to show you what has been selling in the area of Sarasota, Florida. |

Each recording also produces a text file with the full transcript, saved next to it (`call1.mp3` gives `call1_transcript.txt`). Use it to check any cell. New calls are added as new rows to the same Excel file.

Spoken amounts such as "seven million dollars" become `$7,000,000`, and an email spelled out letter by letter (E-G-A-R-D...) becomes a normal address.

## How it works

1. A small speech-to-text program on your computer turns the recording into text.
2. Simple key-word rules find the name, phone, email, budget, objectives, follow-up and action items.
3. The result is added as a new row in the Excel file.

You can also give it a typed transcript (a `.txt` file), which skips the first step.

## Files

| File | Purpose |
| --- | --- |
| `download_model.py` | One-time setup. Downloads the speech model into a local folder. The only step that needs internet. |
| `call_to_excel.py` | The program you run. Fully offline. |

## Setup (once)

These commands are for a Mac. Open Terminal and run them one at a time.

```
# 1. Install Python and audio support (skip if you already have them)
brew install python ffmpeg

# 2. Make a project folder and put both .py files in it
mkdir -p ~/call-summary
cd ~/call-summary

# 3. Create a private Python environment and install the two packages
python3 -m venv venv
source venv/bin/activate
python -m pip install faster-whisper openpyxl

# 4. Download the speech model (needs internet, one time)
python download_model.py medium
```

This guide uses the `medium` model (about 1.5 GB), so the download takes a while. It is saved in `models/medium`.

Each time you open a new Terminal window, run these two lines first:

```
cd ~/call-summary
source venv/bin/activate
```

The prompt should then start with `(venv)`.

## Daily use

```
python call_to_excel.py /path/to/call1.mp3 --model models/medium --out leads.xlsx
```

- Always include `--model models/medium`. Without it the program looks for the `tiny` model and stops with "Speech model not found".
- Give one or more recordings, or `.txt` transcripts.
- `medium` is the most accurate size here but also the slowest, and it uses a few GB of memory. A long call can take longer than the call itself, and the program prints progress while it works.
- Tip: type `python call_to_excel.py ` with a trailing space, then drag the file from Finder into Terminal to fill in its path.
- If the Excel file already exists, new rows are added to it.
- If one file fails, the program says which one and carries on with the rest.

Options:

| Option | Meaning | Default |
| --- | --- | --- |
| `--out FILE` | Excel file to write or add to | `call_summaries.xlsx` |
| `--model FOLDER` | Speech model folder | `models/tiny` (use `models/medium` for this guide) |

## Choosing a speech model size

Bigger models make fewer mistakes with names and numbers, but they are slower. Sizes are approximate.

| Size | Disk | Accuracy | Good for |
| --- | --- | --- | --- |
| tiny | about 75 MB | Lowest | Checking that setup works |
| base | about 145 MB | Fair | Clear, quiet calls |
| small | about 485 MB | Good | Everyday use, and a faster option if medium is too slow |
| medium | about 1.5 GB | Best of these four | Noisy calls, accents, important numbers (used in this guide) |

To use a smaller, faster size instead:

```
python download_model.py small
python call_to_excel.py call1.mp3 --model models/small --out leads.xlsx
```

Several sizes can sit side by side, because each one is saved in its own folder under `models/`.

## Privacy

- After setup, the program makes no internet connection. The recording, the transcript and the Excel file all stay on your computer.
- No AI service is used. The summary comes from simple rules.
- Only `download_model.py` goes online, and only to download the model. It sends no call data.
- To move to a computer with no internet, run the download step elsewhere and copy the `models` folder across.

## Limits (please read)

The sheet is a quick first draft. Check each row before acting on it.

- **It copies sentences; it does not understand them.** A long or rambling call can make it pick the wrong sentence.
- **Speech-to-text can mishear names, phone numbers and prices.** Check those cells against the transcript.
- **It does not know who is speaking.** The name comes from phrases like "my name is" or a greeting such as "Hello Jim Costanzo,". If the broker introduces themselves first, the wrong name may be picked.
- **Budget is the last amount introduced by words like "budget", "up to" or "total of".** Sale price and loan amounts do not get separate cells.
- **Spoken emails convert in two forms:** letters joined by hyphens (E-G-A-R-D) and "name at gmail dot com".
- **English only.**
- **Tested so far on typed transcripts.** Try it on a few real recordings before relying on it.

## Troubleshooting

| Message or problem | What it means and what to do |
| --- | --- |
| `No module named 'faster_whisper'` | The Python environment is not active or the packages are not installed. Run `source venv/bin/activate`, then `python -m pip install faster-whisper openpyxl`. |
| `can't open file ... download_model.py` | You are in the wrong folder. Run `cd ~/call-summary` and check with `ls`. |
| `Speech model not found in 'models/tiny'` | You ran the program without `--model models/medium`, so it looked for `tiny`. Add `--model models/medium`. |
| `Speech model not found in 'models/medium'` | The model is not downloaded yet, or you are in the wrong folder. Run `python download_model.py medium` once, with internet, from `~/call-summary`. |
| `No such file or directory: 'notes.txt'` | `notes.txt` was only an example name. Use the real path to your recording. |
| It seems stuck while loading or transcribing | `medium` is slow on a laptop, and a long recording can take longer than the call itself. The program prints progress while it works. Try a short clip first, or switch to `small`. |
| Phone, email or price looks wrong | Open the saved transcript and search for it. It shows whether the speech model misheard it or the rules picked the wrong sentence. |

## Ideas for later

- Separate the broker's voice from the client's, to get the right name.
- A review screen to correct a row before saving.
- Extra columns, such as property address or company, or separate price and financing cells.
- Export to a CRM.
