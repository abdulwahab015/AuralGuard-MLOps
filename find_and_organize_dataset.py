"""
Script to find and organize your dataset automatically.
This will search for dataset folders and organize them.
"""

import os
import shutil
from pathlib import Path
import sys


def find_dataset_folders(base_dir='.'):
    """Find potential dataset folders."""
    base_path = Path(base_dir)
    potential_folders = []
    
    # Common dataset folder names
    search_names = [
        'dataset', 'Dataset', 'DATASET', 'data', 'Data', 'DATA',
        'audio', 'Audio', 'AUDIO', 'audios', 'Audios',
        'kaggle', 'Kaggle', 'KAGGLE'
    ]
    
    # Search in current directory and subdirectories
    for item in base_path.rglob('*'):
        if item.is_dir():
            folder_name = item.name
            # Check if folder name contains dataset keywords
            if any(name in folder_name for name in search_names):
                # Check if it contains audio files
                audio_files = list(item.rglob('*.wav')) + list(item.rglob('*.mp3')) + \
                             list(item.rglob('*.flac')) + list(item.rglob('*.ogg'))
                if len(audio_files) > 0:
                    potential_folders.append((item, len(audio_files)))
    
    return potential_folders


def analyze_folder_structure(folder_path):
    """Analyze the structure of a folder to understand its organization."""
    folder = Path(folder_path)
    
    # Check for common structures
    real_folders = []
    fake_folders = []
    audio_files = []
    
    # Look for real/fake folders
    for item in folder.rglob('*'):
        if item.is_dir():
            name_lower = item.name.lower()
            if any(x in name_lower for x in ['real', 'authentic', 'genuine', 'original']):
                real_folders.append(item)
            elif any(x in name_lower for x in ['fake', 'synthetic', 'deepfake', 'clone']):
                fake_folders.append(item)
        elif item.is_file():
            if item.suffix.lower() in {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}:
                audio_files.append(item)
    
    return {
        'real_folders': real_folders,
        'fake_folders': fake_folders,
        'audio_files': audio_files,
        'has_structure': len(real_folders) > 0 or len(fake_folders) > 0
    }


def organize_to_target(source_path, target_dir='Audio Dataset/KAGGLE/AUDIO'):
    """Organize dataset from source to target structure."""
    target_path = Path(target_dir)
    real_target = target_path / 'REAL'
    fake_target = target_path / 'FAKE'
    
    real_target.mkdir(parents=True, exist_ok=True)
    fake_target.mkdir(parents=True, exist_ok=True)
    
    analysis = analyze_folder_structure(source_path)
    
    real_count = 0
    fake_count = 0
    
    # If structured (has real/fake folders)
    if analysis['has_structure']:
        # Copy from real folders
        for real_folder in analysis['real_folders']:
            for audio_file in real_folder.rglob('*'):
                if audio_file.is_file() and audio_file.suffix.lower() in {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}:
                    shutil.copy2(audio_file, real_target / audio_file.name)
                    real_count += 1
        
        # Copy from fake folders
        for fake_folder in analysis['fake_folders']:
            for audio_file in fake_folder.rglob('*'):
                if audio_file.is_file() and audio_file.suffix.lower() in {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}:
                    shutil.copy2(audio_file, fake_target / audio_file.name)
                    fake_count += 1
    
    # If flat structure, check filenames
    else:
        for audio_file in analysis['audio_files']:
            filename_lower = audio_file.name.lower()
            if any(x in filename_lower for x in ['real', 'authentic', 'genuine', 'original']):
                shutil.copy2(audio_file, real_target / audio_file.name)
                real_count += 1
            elif any(x in filename_lower for x in ['fake', 'synthetic', 'deepfake', 'clone']):
                shutil.copy2(audio_file, fake_target / audio_file.name)
                fake_count += 1
            else:
                # Ask user or put in a default folder
                print(f"  ⚠️  Could not determine label for: {audio_file.name}")
    
    return real_count, fake_count


def main():
    print("=" * 60)
    print("Dataset Finder and Organizer")
    print("=" * 60)
    print()
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"Searching in: {current_dir}")
    print()
    
    # Find potential dataset folders
    print("Searching for dataset folders...")
    folders = find_dataset_folders(current_dir)
    
    if not folders:
        print("❌ No dataset folders found with audio files.")
        print()
        print("Please ensure:")
        print("  1. Your dataset folder is in the project directory")
        print("  2. It contains .wav, .mp3, .flac, or .ogg files")
        print()
        print("You can also manually specify the path:")
        print("  python3 find_and_organize_dataset.py /path/to/your/dataset")
        return
    
    print(f"Found {len(folders)} potential dataset folder(s):")
    print()
    
    for i, (folder, file_count) in enumerate(folders, 1):
        print(f"{i}. {folder}")
        print(f"   Contains {file_count} audio files")
        
        # Analyze structure
        analysis = analyze_folder_structure(folder)
        if analysis['has_structure']:
            print(f"   Structure: Has real/fake folders")
        else:
            print(f"   Structure: Flat (checking filenames)")
        print()
    
    # If multiple, let user choose
    if len(folders) > 1:
        choice = input(f"Which folder to organize? (1-{len(folders)}) or 'all': ").strip()
        if choice.lower() == 'all':
            selected_folders = [f[0] for f in folders]
        else:
            try:
                idx = int(choice) - 1
                selected_folders = [folders[idx][0]]
            except:
                print("Invalid choice. Using first folder.")
                selected_folders = [folders[0][0]]
    else:
        selected_folders = [folders[0][0]]
    
    # Organize each selected folder
    total_real = 0
    total_fake = 0
    
    for folder in selected_folders:
        print(f"\nOrganizing: {folder}")
        print("-" * 60)
        
        real_count, fake_count = organize_to_target(folder)
        total_real += real_count
        total_fake += fake_count
        
        print(f"  ✅ Organized {real_count} real files")
        print(f"  ✅ Organized {fake_count} fake files")
    
    print()
    print("=" * 60)
    print("✅ Organization Complete!")
    print("=" * 60)
    print(f"Total files organized:")
    print(f"  Real: {total_real}")
    print(f"  Fake: {total_fake}")
    print()
    print("Dataset structure:")
    print("  Audio Dataset/KAGGLE/AUDIO/REAL/")
    print("  Audio Dataset/KAGGLE/AUDIO/FAKE/")
    print()
    print("Next step: Verify with check_dataset.py")
    print("  python3 check_dataset.py")


if __name__ == '__main__':
    # Check if path provided as argument
    if len(sys.argv) > 1:
        source_path = Path(sys.argv[1])
        if source_path.exists():
            print(f"Organizing: {source_path}")
            real_count, fake_count = organize_to_target(source_path)
            print(f"✅ Organized {real_count} real files and {fake_count} fake files")
        else:
            print(f"❌ Path not found: {source_path}")
    else:
        main()

