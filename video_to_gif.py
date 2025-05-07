#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from pathlib import Path

def convert_video_to_gif(input_file, output_file=None, width=None, fps=10, quality=90, loop=0, speed=1.0):
    """
    Convert a video file to a looping GIF using FFmpeg.
    
    Args:
        input_file (str): Path to the input video file
        output_file (str, optional): Path to the output GIF file
        width (int, optional): Width to resize the GIF to (aspect ratio is maintained)
        fps (int, optional): Frames per second for the GIF
        quality (int, optional): Quality of the GIF (1-100)
        loop (int, optional): Loop count (0 = infinite loop)
        speed (float, optional): Speed multiplier (>1 speeds up, <1 slows down)
    
    Returns:
        str: Path to the created GIF
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # If no output file is specified, use the same name with .gif extension
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.gif'
    
    # Build the FFmpeg command
    cmd = ['ffmpeg', '-i', input_file, '-f', 'gif']
    
    # Add filters based on parameters
    filters = []
    
    # Add speed adjustment filter if needed
    if speed != 1.0:
        if speed > 1.0:
            # Speed up: setpts=PTS/speed
            filters.append(f"setpts=PTS/{speed}")
        else:
            # Slow down: setpts=PTS*(1/speed)
            filters.append(f"setpts=PTS*{1/speed}")
    
    # Add scale filter if width is specified
    if width:
        filters.append(f"scale={width}:-1:flags=lanczos")
    
    # Add fps filter
    filters.append(f"fps={fps}")
    
    # Set palatteuse to improve quality
    palette_file = os.path.splitext(output_file)[0] + "_palette.png"
    
    # Generate a palette first for better quality
    # For palette generation, we need to apply the speed and scale filters, but not the fps filter yet
    palette_filters = [f for f in filters if not f.startswith("fps=")]
    
    palette_cmd = [
        'ffmpeg', '-i', input_file
    ]
    
    if palette_filters:
        palette_cmd.extend(['-vf', ','.join(palette_filters) + f",palettegen=max_colors={quality}"])
    else:
        palette_cmd.extend(['-vf', f"palettegen=max_colors={quality}"])
    
    palette_cmd.extend(['-y', palette_file])
    
    # Then use the palette to create the GIF
    final_cmd = [
        'ffmpeg', '-i', input_file, '-i', palette_file
    ]
    
    if filters:
        final_cmd.extend(['-lavfi', f"{','.join(filters)}[x];[x][1:v]paletteuse"])
    else:
        final_cmd.extend(['-lavfi', "[0:v][1:v]paletteuse"])
    
    final_cmd.extend(['-loop', str(loop), '-y', output_file])
    
    try:
        # Create palette
        subprocess.run(palette_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Create GIF
        subprocess.run(final_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Remove the temporary palette file
        os.remove(palette_file)
        
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error converting video to GIF: {e.stderr.decode() if e.stderr else str(e)}")
        if os.path.exists(palette_file):
            os.remove(palette_file)
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        if os.path.exists(palette_file):
            os.remove(palette_file)
        raise

def get_video_files(directory, recursive=False):
    """Get all video files in a directory"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
    video_files = []
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.splitext(file_path)[1].lower() in video_extensions:
                    video_files.append(file_path)
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and os.path.splitext(file_path)[1].lower() in video_extensions:
                video_files.append(file_path)
    
    return video_files

def interactive_mode():
    """Run an interactive command-line interface to convert videos to GIFs"""
    print("\n=== Video to GIF Converter ===\n")
    
    # Ask for input type
    input_type = ""
    while input_type not in ["1", "2", "3"]:
        print("What would you like to convert?")
        print("1. A single video file")
        print("2. All videos in a directory")
        print("3. Select videos from a directory")
        input_type = input("Enter your choice (1/2/3): ")
    
    # Get input file or directory based on choice
    if input_type == "1":
        input_path = input("Enter the path to the video file: ")
        if not os.path.isfile(input_path):
            print(f"Error: File not found: {input_path}")
            return 1
        input_files = [input_path]
    elif input_type in ["2", "3"]:
        dir_path = input("Enter the directory path containing videos: ")
        if not os.path.isdir(dir_path):
            print(f"Error: Directory not found: {dir_path}")
            return 1
        
        # Ask about recursion
        recursive = input("Include videos in subdirectories? (y/n): ").lower() == 'y'
        
        # Get all video files in the directory
        all_videos = get_video_files(dir_path, recursive)
        
        if not all_videos:
            print(f"No video files found in {dir_path}")
            return 1
        
        if input_type == "2":
            # Use all videos
            input_files = all_videos
            print(f"Found {len(input_files)} videos to convert.")
        else:  # input_type == "3"
            # Let user select videos
            print("\nAvailable videos:")
            for i, video in enumerate(all_videos, 1):
                print(f"{i}. {os.path.basename(video)}")
            
            # Get user selection
            selection = input("\nEnter video numbers to convert (comma-separated, e.g., 1,3,5) or 'all': ")
            
            if selection.lower() == 'all':
                input_files = all_videos
            else:
                try:
                    selected_indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                    input_files = [all_videos[idx] for idx in selected_indices if 0 <= idx < len(all_videos)]
                    
                    if not input_files:
                        print("No valid files selected.")
                        return 1
                except (ValueError, IndexError):
                    print("Invalid selection.")
                    return 1
    
    # Get output directory
    output_choice = input("Convert to the same directory as the original files? (y/n): ").lower()
    if output_choice == 'y':
        output_dir = None
    else:
        output_dir = input("Enter the output directory path: ")
        if not os.path.exists(output_dir):
            create_dir = input(f"Directory {output_dir} doesn't exist. Create it? (y/n): ").lower()
            if create_dir == 'y':
                os.makedirs(output_dir, exist_ok=True)
            else:
                print("Operation cancelled.")
                return 1
    
    # Get conversion parameters
    try:
        width_input = input("Enter width in pixels (press Enter for original size): ")
        width = int(width_input) if width_input.strip() else None
        
        fps_input = input("Enter frames per second (press Enter for default 10): ")
        fps = int(fps_input) if fps_input.strip() else 10
        
        quality_input = input("Enter quality (1-100, press Enter for default 90): ")
        quality = int(quality_input) if quality_input.strip() else 90
        
        speed_input = input("Enter speed multiplier (e.g., 2.0 for 2x speed, 0.5 for half speed, press Enter for normal speed): ")
        speed = float(speed_input) if speed_input.strip() else 1.0
        
        loop = input("Enable infinite looping? (y/n): ").lower() != 'n'
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
        return 1
    
    # Calculate and show estimated file size
    if len(input_files) > 0:
        print(f"\nReady to convert {len(input_files)} video(s) with:")
        print(f"- Width: {width if width else 'Original'}")
        print(f"- FPS: {fps}")
        print(f"- Quality: {quality}")
        print(f"- Speed: {speed}x")
        print(f"- Looping: {'Enabled' if loop else 'Disabled'}")
        
        proceed = input("\nProceed with conversion? (y/n): ").lower()
        if proceed != 'y':
            print("Operation cancelled.")
            return 0
    
    # Convert each selected video
    print("\nStarting conversion...")
    success_count = 0
    
    for i, input_file in enumerate(input_files, 1):
        print(f"\n[{i}/{len(input_files)}] Converting: {os.path.basename(input_file)}")
        
        try:
            if output_dir:
                output_file = os.path.join(output_dir, os.path.basename(os.path.splitext(input_file)[0]) + '.gif')
            else:
                output_file = None
            
            result = convert_video_to_gif(
                input_file,
                output_file,
                width,
                fps,
                quality,
                0 if loop else 1,
                speed
            )
            
            print(f"Successfully created: {result}")
            success_count += 1
            
        except Exception as e:
            print(f"Error processing {input_file}: {str(e)}")
    
    # Show summary
    print(f"\nConversion complete: {success_count} of {len(input_files)} videos converted successfully.")
    return 0

def main():
    # Check if any arguments were provided
    if len(sys.argv) > 1:
        # If arguments were provided, use the original argument parser
        parser = argparse.ArgumentParser(description="Convert video files to looping GIFs")
        parser.add_argument("input", help="Input video file or directory containing videos")
        parser.add_argument("-o", "--output", help="Output GIF file or directory (defaults to same name with .gif extension)")
        parser.add_argument("-w", "--width", type=int, help="Width of the output GIF (aspect ratio is maintained)")
        parser.add_argument("-f", "--fps", type=int, default=10, help="Frames per second (default: 10)")
        parser.add_argument("-q", "--quality", type=int, default=90, help="Quality (1-100, default: 90)")
        parser.add_argument("-r", "--recursive", action="store_true", help="Process directories recursively")
        parser.add_argument("--no-loop", action="store_true", help="Disable infinite looping")
        parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
        parser.add_argument("-b", "--batch", help="Use a batch file containing a list of videos to convert, one per line")
        parser.add_argument("-s", "--speed", type=float, default=1.0, help="Speed multiplier (>1 speeds up, <1 slows down, default: 1.0)")
        
        args = parser.parse_args()
        
        # Check if interactive mode is requested
        if args.interactive:
            return interactive_mode()
        
        # Check if batch mode is requested
        if args.batch:
            if not os.path.isfile(args.batch):
                print(f"Error: Batch file not found: {args.batch}")
                return 1
            
            # Read the batch file
            with open(args.batch, 'r') as f:
                input_files = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            
            # Process each file in the batch
            success_count = 0
            for i, input_file in enumerate(input_files, 1):
                print(f"\n[{i}/{len(input_files)}] Processing: {input_file}")
                
                if not os.path.exists(input_file):
                    print(f"Error: File not found: {input_file}")
                    continue
                
                try:
                    output_file = None
                    if args.output:
                        if os.path.isdir(args.output):
                            output_file = os.path.join(args.output, os.path.basename(os.path.splitext(input_file)[0]) + '.gif')
                        else:
                            # For single file output, only use the specified output for the first file
                            output_file = args.output if i == 1 else None
                    
                    result = convert_video_to_gif(
                        input_file,
                        output_file,
                        args.width,
                        args.fps,
                        args.quality,
                        1 if args.no_loop else 0,
                        args.speed
                    )
                    
                    print(f"Successfully created: {result}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"Error processing {input_file}: {str(e)}")
            
            # Show summary
            print(f"\nBatch processing complete: {success_count} of {len(input_files)} videos converted successfully.")
            return 0
            
        # Check if the input is a file or directory
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input path does not exist: {input_path}")
            return 1
        
        # Determine loop value
        loop_value = 1 if args.no_loop else 0  # 0 means infinite loop
        
        # Process a single file
        if input_path.is_file():
            output_file = args.output
            try:
                result = convert_video_to_gif(
                    str(input_path), 
                    output_file, 
                    args.width, 
                    args.fps, 
                    args.quality,
                    loop_value,
                    args.speed
                )
                print(f"Successfully created: {result}")
            except Exception as e:
                print(f"Error processing {input_path}: {str(e)}")
                return 1
        
        # Process a directory
        elif input_path.is_dir():
            if args.output and not os.path.isdir(args.output):
                os.makedirs(args.output, exist_ok=True)
            
            # Get video file extensions
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
            
            # Function to process a single file within directory processing
            def process_file(file_path):
                if file_path.suffix.lower() in video_extensions:
                    output_dir = Path(args.output) if args.output else file_path.parent
                    output_file = output_dir / (file_path.stem + '.gif')
                    
                    try:
                        result = convert_video_to_gif(
                            str(file_path), 
                            str(output_file), 
                            args.width, 
                            args.fps, 
                            args.quality,
                            loop_value,
                            args.speed
                        )
                        print(f"Successfully created: {result}")
                        return True
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
                        return False
                return False
            
            # Walk through the directory structure if recursive
            processed_count = 0
            success_count = 0
            
            if args.recursive:
                for root, _, files in os.walk(input_path):
                    root_path = Path(root)
                    for file in files:
                        file_path = root_path / file
                        if file_path.suffix.lower() in video_extensions:
                            processed_count += 1
                            if process_file(file_path):
                                success_count += 1
            else:
                # Process only files in the top-level directory
                for file_path in input_path.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                        processed_count += 1
                        if process_file(file_path):
                            success_count += 1
            
            print(f"\nDirectory processing complete: {success_count} of {processed_count} videos converted successfully.")
    else:
        # If no arguments were provided, run in interactive mode
        return interactive_mode()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())