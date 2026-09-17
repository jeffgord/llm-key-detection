import argparse
import csv
from pathlib import Path

RAW_DIR = Path(__file__).parent / "raw"
OUTPUT_FILE = Path(__file__).parent / "chords.csv"


def parse_lab(path: Path) -> list[tuple[float, float, str]]:
    segments = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            start, end, chord = float(parts[0]), float(parts[1]), parts[2]
            segments.append((start, end, chord))
    return segments


def merge_consecutive(segments: list[tuple[float, float, str]]) -> list[tuple[float, float, str]]:
    if not segments:
        return []
    merged = [segments[0]]
    for start, end, chord in segments[1:]:
        if chord == merged[-1][2]:
            merged[-1] = (merged[-1][0], end, chord)
        else:
            merged.append((start, end, chord))
    return merged


def format_chords(segments: list[tuple[float, float, str]]) -> str:
    parts = []
    for start, end, chord in segments:
        duration = round(end - start, 1)
        parts.append(f"{chord} {duration}s")
    return ", ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Collapse raw .lab chord output into a compact per-track CSV")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR, help="Directory of .lab files")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE, help="Output CSV path")
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    lab_files = sorted(args.raw_dir.glob("*.lab"), key=lambda p: p.stem)

    with open(args.output, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["track_id", "chords"])
        for lab_path in lab_files:
            track_id = lab_path.stem
            segments = parse_lab(lab_path)
            segments = merge_consecutive(segments)
            chords_str = format_chords(segments)
            writer.writerow([track_id, chords_str])

    print(f"Wrote {len(lab_files)} tracks to {args.output}")


if __name__ == "__main__":
    main()
