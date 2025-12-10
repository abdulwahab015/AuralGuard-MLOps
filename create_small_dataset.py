"""
Script to create a smaller dataset subset for faster training/testing.
This samples a subset of files from the full dataset.
"""

import os
import shutil
import random
from pathlib import Path

def create_small_dataset(
    source_real='Audio Dataset/KAGGLE/AUDIO/REAL',
    source_fake='Audio Dataset/KAGGLE/AUDIO/FAKE',
    target_real='Audio Dataset/KAGGLE/AUDIO/REAL_SMALL',
    target_fake='Audio Dataset/KAGGLE/AUDIO/FAKE_SMALL',
    num_samples=50  # Number of files per class
):
    """
    Create a smaller dataset by sampling files.
    
    Args:
        source_real: Source directory for real audio files
        source_fake: Source directory for fake audio files
        target_real: Target directory for sampled real files
        target_fake: Target directory for sampled fake files
        num_samples: Number of files to sample from each class
    """
    print("=" * 60)
    print("Creating Small Dataset Subset")
    print("=" * 60)
    print()
    
    # Create target directories
    Path(target_real).mkdir(parents=True, exist_ok=True)
    Path(target_fake).mkdir(parents=True, exist_ok=True)
    
    # Get all audio files
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    # Real files
    real_files = []
    if os.path.exists(source_real):
        for file in Path(source_real).iterdir():
            if file.is_file() and file.suffix.lower() in audio_extensions:
                real_files.append(file)
    
    # Fake files
    fake_files = []
    if os.path.exists(source_fake):
        for file in Path(source_fake).iterdir():
            if file.is_file() and file.suffix.lower() in audio_extensions:
                fake_files.append(file)
    
    print(f"Found {len(real_files)} real files")
    print(f"Found {len(fake_files)} fake files")
    print()
    
    # Sample files
    num_real = min(num_samples, len(real_files))
    num_fake = min(num_samples, len(fake_files))
    
    sampled_real = random.sample(real_files, num_real) if real_files else []
    sampled_fake = random.sample(fake_files, num_fake) if fake_files else []
    
    # Copy sampled files
    print(f"Copying {num_real} real files...")
    for file in sampled_real:
        shutil.copy2(file, Path(target_real) / file.name)
    
    print(f"Copying {num_fake} fake files...")
    for file in sampled_fake:
        shutil.copy2(file, Path(target_fake) / file.name)
    
    print()
    print("=" * 60)
    print("✅ Small dataset created!")
    print("=" * 60)
    print(f"Real files: {num_real} in {target_real}")
    print(f"Fake files: {num_fake} in {target_fake}")
    print(f"Total: {num_real + num_fake} files")
    print()
    print("To use this dataset, update paths in complete_training.py")
    print("Or temporarily rename folders:")
    print(f"  mv '{source_real}' '{source_real}_BACKUP'")
    print(f"  mv '{source_fake}' '{source_fake}_BACKUP'")
    print(f"  mv '{target_real}' '{source_real}'")
    print(f"  mv '{target_fake}' '{source_fake}'")
    print()
    
    return num_real, num_fake


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Create small dataset subset')
    parser.add_argument(
        '--samples',
        type=int,
        default=50,
        help='Number of files to sample from each class (default: 50)'
    )
    parser.add_argument(
        '--use-small',
        action='store_true',
        help='Automatically switch to use small dataset'
    )
    
    args = parser.parse_args()
    
    # Create small dataset
    num_real, num_fake = create_small_dataset(num_samples=args.samples)
    
    # Optionally switch to use small dataset
    if args.use_small:
        print("Switching to small dataset...")
        
        real_source = Path('Audio Dataset/KAGGLE/AUDIO/REAL')
        fake_source = Path('Audio Dataset/KAGGLE/AUDIO/FAKE')
        real_small = Path('Audio Dataset/KAGGLE/AUDIO/REAL_SMALL')
        fake_small = Path('Audio Dataset/KAGGLE/AUDIO/FAKE_SMALL')
        
        # Backup original
        if real_source.exists():
            real_backup = Path('Audio Dataset/KAGGLE/AUDIO/REAL_FULL')
            if not real_backup.exists():
                real_source.rename(real_backup)
                print(f"  Backed up real files to {real_backup}")
        
        if fake_source.exists():
            fake_backup = Path('Audio Dataset/KAGGLE/AUDIO/FAKE_FULL')
            if not fake_backup.exists():
                fake_source.rename(fake_backup)
                print(f"  Backed up fake files to {fake_backup}")
        
        # Use small dataset
        if real_small.exists():
            real_small.rename(real_source)
            print(f"  Using small real dataset ({num_real} files)")
        
        if fake_small.exists():
            fake_small.rename(fake_source)
            print(f"  Using small fake dataset ({num_fake} files)")
        
        print()
        print("✅ Switched to small dataset!")
        print("Original dataset backed up to REAL_FULL and FAKE_FULL")
        print()
        print("Now you can run training:")
        print("  python3 complete_training.py --epochs 10")

