"""
Helper script to organize downloaded Kaggle dataset into the required structure.
This script handles various dataset formats and organizes them automatically.
"""

import os
import shutil
import pandas as pd
from pathlib import Path
import argparse


def organize_from_folders(source_dir, target_dir='Audio Dataset/KAGGLE/AUDIO'):
    """
    Organize dataset when files are already in separate folders.
    
    Args:
        source_dir: Source directory with real/fake folders
        target_dir: Target directory structure
    """
    print(f"Organizing from folder structure: {source_dir}")
    
    # Common folder name variations
    real_names = ['real', 'REAL', 'Real', 'authentic', 'AUTHENTIC', 'genuine', 'GENUINE']
    fake_names = ['fake', 'FAKE', 'Fake', 'synthetic', 'SYNTHETIC', 'deepfake', 'DEEPFake']
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Create target directories
    real_target = target_path / 'REAL'
    fake_target = target_path / 'FAKE'
    real_target.mkdir(parents=True, exist_ok=True)
    fake_target.mkdir(parents=True, exist_ok=True)
    
    # Find real and fake folders
    real_folder = None
    fake_folder = None
    
    for folder in source_path.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            if any(name in folder_name for name in real_names):
                real_folder = folder
            elif any(name in folder_name for name in fake_names):
                fake_folder = folder
    
    # Copy files
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac'}
    
    if real_folder:
        print(f"  Found real folder: {real_folder}")
        count = 0
        for file in real_folder.rglob('*'):
            if file.suffix.lower() in audio_extensions:
                shutil.copy2(file, real_target / file.name)
                count += 1
        print(f"  Copied {count} real audio files")
    
    if fake_folder:
        print(f"  Found fake folder: {fake_folder}")
        count = 0
        for file in fake_folder.rglob('*'):
            if file.suffix.lower() in audio_extensions:
                shutil.copy2(file, fake_target / file.name)
                count += 1
        print(f"  Copied {count} fake audio files")
    
    if not real_folder and not fake_folder:
        print("  ⚠️  Could not find real/fake folders automatically")
        print("  Please organize manually or use CSV method")


def organize_from_csv(csv_path, audio_dir, target_dir='Audio Dataset/KAGGLE/AUDIO'):
    """
    Organize dataset from CSV file with labels.
    
    Args:
        csv_path: Path to CSV file with audio file names and labels
        audio_dir: Directory containing audio files
        target_dir: Target directory structure
    """
    print(f"Organizing from CSV: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        print(f"  Loaded CSV with {len(df)} rows")
        
        # Common column name variations
        file_col = None
        label_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if any(x in col_lower for x in ['file', 'filename', 'path', 'audio', 'name']):
                file_col = col
            if any(x in col_lower for x in ['label', 'class', 'type', 'category']):
                label_col = col
        
        if not file_col:
            print("  ⚠️  Could not find file column. Available columns:", df.columns.tolist())
            return
        
        if not label_col:
            print("  ⚠️  Could not find label column. Available columns:", df.columns.tolist())
            return
        
        print(f"  Using file column: {file_col}")
        print(f"  Using label column: {label_col}")
        
        target_path = Path(target_dir)
        real_target = target_path / 'REAL'
        fake_target = target_path / 'FAKE'
        real_target.mkdir(parents=True, exist_ok=True)
        fake_target.mkdir(parents=True, exist_ok=True)
        
        audio_path = Path(audio_dir)
        real_count = 0
        fake_count = 0
        
        for _, row in df.iterrows():
            filename = row[file_col]
            label = str(row[label_col]).lower()
            
            # Find source file
            source_file = None
            if os.path.isabs(filename) or os.path.exists(filename):
                source_file = Path(filename)
            else:
                # Try in audio_dir
                source_file = audio_path / filename
                if not source_file.exists():
                    # Try recursive search
                    for f in audio_path.rglob(filename):
                        source_file = f
                        break
            
            if source_file and source_file.exists():
                # Determine target
                if 'real' in label or 'authentic' in label or 'genuine' in label or label == '1':
                    target = real_target / source_file.name
                    shutil.copy2(source_file, target)
                    real_count += 1
                elif 'fake' in label or 'synthetic' in label or 'deepfake' in label or label == '0':
                    target = fake_target / source_file.name
                    shutil.copy2(source_file, target)
                    fake_count += 1
        
        print(f"  ✅ Organized {real_count} real files and {fake_count} fake files")
        
    except Exception as e:
        print(f"  ❌ Error reading CSV: {e}")


def organize_flat_structure(source_dir, target_dir='Audio Dataset/KAGGLE/AUDIO'):
    """
    Organize when all files are in one folder (requires manual labeling or filename patterns).
    
    Args:
        source_dir: Directory with all audio files
        target_dir: Target directory structure
    """
    print(f"Organizing flat structure: {source_dir}")
    print("  ⚠️  This method requires files to have 'real' or 'fake' in filename")
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    real_target = target_path / 'REAL'
    fake_target = target_path / 'FAKE'
    real_target.mkdir(parents=True, exist_ok=True)
    fake_target.mkdir(parents=True, exist_ok=True)
    
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac'}
    real_count = 0
    fake_count = 0
    
    for file in source_path.iterdir():
        if file.is_file() and file.suffix.lower() in audio_extensions:
            filename_lower = file.name.lower()
            if any(x in filename_lower for x in ['real', 'authentic', 'genuine', 'original']):
                shutil.copy2(file, real_target / file.name)
                real_count += 1
            elif any(x in filename_lower for x in ['fake', 'synthetic', 'deepfake', 'clone']):
                shutil.copy2(file, fake_target / file.name)
                fake_count += 1
    
    print(f"  ✅ Organized {real_count} real files and {fake_count} fake files")
    if real_count == 0 and fake_count == 0:
        print("  ⚠️  No files matched patterns. You may need to organize manually.")


def main():
    parser = argparse.ArgumentParser(
        description='Organize Kaggle dataset into required structure'
    )
    parser.add_argument(
        'source',
        help='Source directory or CSV file path'
    )
    parser.add_argument(
        '--csv',
        action='store_true',
        help='Source is a CSV file'
    )
    parser.add_argument(
        '--audio-dir',
        help='Directory containing audio files (when using CSV)'
    )
    parser.add_argument(
        '--target',
        default='Audio Dataset/KAGGLE/AUDIO',
        help='Target directory (default: Audio Dataset/KAGGLE/AUDIO)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Dataset Organizer")
    print("=" * 60)
    print()
    
    source_path = Path(args.source)
    
    if not source_path.exists():
        print(f"❌ Error: Source path does not exist: {args.source}")
        return
    
    if args.csv:
        # Organize from CSV
        if not args.audio_dir:
            print("❌ Error: --audio-dir required when using --csv")
            return
        organize_from_csv(args.source, args.audio_dir, args.target)
    elif source_path.is_file() and source_path.suffix == '.csv':
        # Auto-detect CSV
        if not args.audio_dir:
            # Try to find audio directory
            audio_dir = source_path.parent
            print(f"  Using parent directory as audio directory: {audio_dir}")
            organize_from_csv(args.source, str(audio_dir), args.target)
        else:
            organize_from_csv(args.source, args.audio_dir, args.target)
    else:
        # Try folder structure first
        organize_from_folders(args.source, args.target)
        # If that doesn't work well, try flat structure
        # (This is a fallback - you might need to adjust)
    
    print()
    print("=" * 60)
    print("✅ Organization complete!")
    print("=" * 60)
    print()
    print("Verify structure:")
    print(f"  Real files: {Path(args.target) / 'REAL'}")
    print(f"  Fake files: {Path(args.target) / 'FAKE'}")
    print()
    print("Next step: Run training")
    print("  python3 complete_training.py --epochs 10")


if __name__ == '__main__':
    main()

