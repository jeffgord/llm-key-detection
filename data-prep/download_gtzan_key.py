# python data-prep/download_gtzan_key.py

import argparse
import csv
import shutil
import subprocess
import tempfile
from pathlib import Path

AUDIO_REPO = "https://github.com/audiocontentanalysis/dataset-gtzan.git"
AUDIO_BRANCH = "main"
KEY_REPO = "https://github.com/audiocontentanalysis/dataset-gtzan-key.git"
KEY_BRANCH = "master"

GENRES = ["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop", "reggae", "rock"]
ROOTS = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]


def key_code_to_label(code: int) -> str:
    if code < 0:
        return ""
    root = ROOTS[code % 12]
    mode = "Major" if code < 12 else "Minor"
    return f"{root} {mode}"


def clone(repo_url: str, branch: str, dest: Path):
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", branch, repo_url, str(dest)],
        check=True,
    )


def download_gtzan_key(data_dir: Path):
    audio_dir = data_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        print("Cloning audio ...")
        audio_clone = tmp_path / "audio"
        clone(AUDIO_REPO, AUDIO_BRANCH, audio_clone)

        print("Cloning key annotations ...")
        key_clone = tmp_path / "key"
        clone(KEY_REPO, KEY_BRANCH, key_clone)

        rows = []
        for genre in GENRES:
            for wav_path in sorted((audio_clone / "genres" / genre).glob(f"{genre}.*.wav")):
                track_id = wav_path.stem
                key_path = key_clone / "gtzan_key" / "genres" / genre / f"{track_id}.lerch.txt"
                if not key_path.exists():
                    print(f"  no key annotation for {track_id}, skipping")
                    continue

                code = int(key_path.read_text().strip())
                shutil.copy(wav_path, audio_dir / wav_path.name)
                rows.append([track_id, genre, key_code_to_label(code), code])

    csv_path = data_dir / "gtzan_key.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["track_id", "genre", "key", "key_code"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} tracks to {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download the GTZAN key dataset")
    parser.add_argument("--data_dir", type=Path, default=Path("gtzan-key"), help="Directory to download the data to")
    args = parser.parse_args()

    args.data_dir.mkdir(parents=True, exist_ok=True)
    download_gtzan_key(args.data_dir)
