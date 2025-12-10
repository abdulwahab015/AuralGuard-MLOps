"""
Quick script to check if your dataset is properly organized.
"""

import os
from pathlib import Path


def check_dataset():
    """Check if dataset is properly organized."""
    print("=" * 60)
    print("Dataset Structure Checker")
    print("=" * 60)
    print()
    
    base_path = Path('Audio Dataset/KAGGLE/AUDIO')
    real_path = base_path / 'REAL'
    fake_path = base_path / 'FAKE'
    
    # Check if directories exist
    if not base_path.exists():
        print("❌ Base directory not found: Audio Dataset/KAGGLE/AUDIO")
        print()
        print("Expected structure:")
        print("  Audio Dataset/")
        print("    └── KAGGLE/")
        print("        └── AUDIO/")
        print("            ├── REAL/")
        print("            └── FAKE/")
        return False
    
    # Check real folder
    if not real_path.exists():
        print(f"❌ Real audio folder not found: {real_path}")
    else:
        real_files = list(real_path.glob('*'))
        audio_files = [f for f in real_files if f.suffix.lower() in {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}]
        print(f"✅ Real folder found: {len(audio_files)} audio files")
        if len(audio_files) > 0:
            print(f"   Example: {audio_files[0].name}")
    
    # Check fake folder
    if not fake_path.exists():
        print(f"❌ Fake audio folder not found: {fake_path}")
    else:
        fake_files = list(fake_path.glob('*'))
        audio_files = [f for f in fake_files if f.suffix.lower() in {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}]
        print(f"✅ Fake folder found: {len(audio_files)} audio files")
        if len(audio_files) > 0:
            print(f"   Example: {audio_files[0].name}")
    
    # Summary
    print()
    if real_path.exists() and fake_path.exists():
        real_count = len([f for f in real_path.glob('*') if f.suffix.lower() in {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}])
        fake_count = len([f for f in fake_path.glob('*') if f.suffix.lower() in {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}])
        
        print("=" * 60)
        print("Summary:")
        print(f"  Real audio files: {real_count}")
        print(f"  Fake audio files: {fake_count}")
        print(f"  Total: {real_count + fake_count}")
        print()
        
        if real_count > 0 and fake_count > 0:
            print("✅ Dataset is ready for training!")
            print()
            print("Next step:")
            print("  python3 complete_training.py --epochs 10")
            return True
        else:
            print("⚠️  Dataset structure exists but no audio files found")
            print("   Make sure audio files are in the REAL and FAKE folders")
            return False
    else:
        print("❌ Dataset structure is incomplete")
        print()
        print("To organize your dataset, run:")
        print("  python3 organize_dataset.py /path/to/your/downloaded/dataset")
        return False


if __name__ == '__main__':
    check_dataset()

