# Video to GIF Converter

A simple tool to convert video files to looping GIFs suitable for embedding in emails.

## Requirements

- Python 3.6+
- FFmpeg

## Usage

### Interactive Mode

For an easy, guided experience, simply run the script without arguments:

```
python video_to_gif.py
```

This launches an interactive interface that walks you through the conversion process with step-by-step prompts.

### Command Line Mode

Convert a single video file to a GIF:

```
python video_to_gif.py video.mp4
```

This will create `video.gif` in the same directory.

### Batch Conversion

Convert multiple videos listed in a text file:

```
python video_to_gif.py -b video_list.txt -o output_folder/
```

The batch file should contain one video path per line. Lines starting with # are treated as comments.

Example batch file (`video_list.txt`):
```
# Videos to convert
/path/to/video1.mp4
/path/to/video2.mov
/path/to/video3.avi
```

### Options

```
python video_to_gif.py [options] input_file_or_directory
```

Options:
- `-o, --output` - Output file or directory name
- `-w, --width` - Width of the output GIF (height is calculated automatically)
- `-f, --fps` - Frames per second (default: 10)
- `-q, --quality` - Quality of the GIF (1-100, default: 90)
- `-r, --recursive` - Process directories recursively
- `--no-loop` - Disable infinite looping
- `-i, --interactive` - Run in interactive mode
- `-b, --batch` - Use a batch file containing a list of videos to convert
- `-s, --speed` - Speed multiplier (>1 speeds up, <1 slows down, default: 1.0)

### Examples

Convert a video with custom settings:
```
python video_to_gif.py -w 320 -f 15 -q 95 video.mp4
```

Create a 2x speed GIF:
```
python video_to_gif.py -s 2.0 video.mp4
```

Slow down a video to half speed:
```
python video_to_gif.py -s 0.5 video.mp4
```

Convert all videos in a directory:
```
python video_to_gif.py -o output_folder/ -w 400 videos_folder/
```

Convert videos recursively:
```
python video_to_gif.py -r -o gifs/ videos_folder/
```

Use interactive mode explicitly:
```
python video_to_gif.py -i
```

## Tips for Email-Friendly GIFs

1. **Keep them small**: Use lower fps (8-12) and width (300-500px)
2. **Optimize file size**: Lower quality slightly (80-90) for better email compatibility
3. **Trim your videos**: Convert only the necessary segments to keep file sizes manageable
4. **Test your GIFs**: Check how they appear in various email clients before sending
5. **Speed adjustment**: Consider speeding up videos (1.5x-2x) to create more concise GIFs 