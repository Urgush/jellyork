<p align="center">
<img width="400" height="400" alt="jellyork" src="https://github.com/user-attachments/assets/71b4d7aa-4e97-4a84-89f2-ff1ff530da00" />
</p>

# JellyOrk Catalog Generator

Creates PDF catalogs from your Jellyfin media collection. New version is 1.1.0

## 🤖 Important Development Notes

This tool was created almost entirely through AI-assisted development (vibe coding with Claude). It works well for standard Jellyfin setups, but edge cases may exist. Always test with a small dataset first. Contributions and bug reports welcome!

This tool was tested exclusively on Windows 11, but it should be functional on Linux and macOS too. Feedback on Linux or macOS performance is welcome!

## Features

- ✅ Automatically scans NFO files (movies and TV shows)
- ✅ Extracts title, year, and description
- ✅ Includes poster images
- ✅ Flexible sorting (title, year, type)
- ✅ Clean PDF with statistics
- ✅ Professional layout
- ✅ Smart article handling for sorting (ignores "The", "Das", "Le", etc.)
- ✅ Audio and subtitle information
- ✅ TV show season overview
- ✅ Automatically optimizes images for PDF inclusion (new in v1.1.0)


## Installation

1. **Python Version**: Python 3.7 or higher required

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install reportlab Pillow
```
## Usage

### Basic Usage

```bash
python jellyork_catalog.py /path/to/your/jellyfin/directory
```

### With Sorting

**Sort by title (default)**:
```bash
python jellyork_catalog.py /path/to/jellyfin -s title
```

**Sort by year (newest first)**:
```bash
python jellyork_catalog.py /path/to/jellyfin -s year
```

**Sort by type (movies, then TV shows)**:
```bash
python jellyork_catalog.py /path/to/jellyfin -s type
```

### Specify Output File

```bash
python jellyork_catalog.py /path/to/jellyfin -o my_catalog.pdf
```

### Combine Options

```bash
python jellyork_catalog.py /path/to/jellyfin -s year -o collection_2024.pdf
```
### Image Quality and Size Control (new in 1.1.0)

Control image quality and size to balance PDF file size vs. quality:

**Lower quality for smaller files:**
```bash
python jellork_catalog.py /path/to/jellyfin -q 60
```

**Higher quality for better images:**
```bash
python jellork_catalog.py /path/to/jellyfin -q 85
```

**Larger posters:**
```bash
python jellork_catalog.py /path/to/jellyfin -w 5.0 --season-width 4.0
```

**Combine quality and size settings:**
```bash
python jellork_catalog.py /path/to/jellyfin -q 85 -w 5.0 -o high_quality.pdf
```

**Available image options:**
- `-q, --quality QUALITY`: JPEG quality (1-100, default: 75)
- `-w, --poster-width WIDTH`: Main poster width in cm (default: 4.0)
- `--season-width WIDTH`: Season poster width in cm (default: 3.0)

## Show Help

```bash
python jellyork_catalog.py --help
```

## Jellyfin Directory Structure

The script expects the standard Jellyfin structure:

```
Jellyfin-Media/
├── Movies/
│   ├── Movie1 (2020)/
│   │   ├── movie.nfo
│   │   ├── poster.jpg
│   │   └── Movie1.mkv
│   └── Movie2 (2021)/
│       ├── movie.nfo
│       └── poster.jpg
└── TV Shows/
    └── Show1/
        ├── tvshow.nfo
        ├── poster.jpg
        └── Season 01/
            ├── season01-poster.jpg
            └── S01E01.nfo
            └── ...
```

### NFO File Example (Movie)

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>Inception</title>
    <year>2010</year>
    <plot>A thief who steals corporate secrets...</plot>
    <fileinfo>
        <streamdetails>
            <audio>
                <codec>DTS</codec>
                <language>eng</language>
                <channels>6</channels>
            </audio>
            <subtitle>
                <language>eng</language>
            </subtitle>
        </streamdetails>
    </fileinfo>
</movie>
```

### NFO File Example (TV Show)

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<tvshow>
    <title>Breaking Bad</title>
    <year>2008</year>
    <plot>A high school chemistry teacher...</plot>
</tvshow>
```

## Poster Images

The script searches for images in this order:
1. `poster.jpg` / `poster.png`
2. `folder.jpg` / `folder.png`
3. `cover.jpg` / `cover.png`
4. First available image in directory

For TV show seasons:
1. `season01-poster.jpg` / `season01-poster.png`
2. `poster.jpg` / `poster.png`
3. First available image in season directory

## Smart Article Sorting

The catalog intelligently sorts titles while ignoring leading articles:

**Supported Languages:**
- 🇩🇪 German: der, die, das, ein, eine
- 🇬🇧 English: the, a, an
- 🇫🇷 French: le, la, les, un, une, des
- 🇪🇸 Spanish: el, la, los, las, un, una, unos, unas

**Example:**
- "Das Boot" → sorted under "B"
- "The Matrix" → sorted under "M"
- "A Beautiful Mind" → sorted under "B"

The titles are always displayed with their original article - only the sorting order changes.

## Output

The generated PDF contains:
- **Title page** with total count and creation date
- **Statistics page** with breakdown (movies/TV shows)
- **Catalog** with all media:
  - Title
  - Year and type (Movie/TV Show)
  - Audio tracks and subtitles
  - Poster image (if available)
  - Description
  - For TV shows: Season overview with posters
 
- Sample from testdata without proper poster images
<img width="400" height="400" alt="pdf" src="https://github.com/user-attachments/assets/f61ede88-faed-41d6-9005-cb116e373402" />

### PDF Optimization (new in v1.1.0)

Images are automatically optimized for PDF inclusion:
- Resized to appropriate dimensions (configurable via `-w` and `--season-width`)
- Compressed to JPEG (quality configurable via `-q`, default: 75)
- Alpha channels removed
- Reduces file size significantly while maintaining visual quality

**Example:** A collection with 100 movies typically produces a PDF of 5-15 MB instead of 50-100 MB with unoptimized images.

**Fine-tuning:**
- **Smaller files**: Use `-q 60` (slightly lower quality)
- **Better quality**: Use `-q 85` (larger files)
- **Larger posters**: Use `-w 5.0` (more detail but larger files)
- **Smaller posters**: Use `-w 3.0` (smaller files)

See "Image Quality and Size Control" section above for examples.

## Troubleshooting

### Drive not found
- Use UNC paths for network drives instead of local drive letters (Z:\Filme\JellyFin\movies => \\\server\share\Filme\JellyFin\movies)

### No NFO Files Found
- Check if the path is correct
- Make sure NFO files exist
- Jellyfin must have downloaded metadata already

### Images Not Showing
- Check if poster files exist
- Supported formats: JPG, JPEG, PNG
- Make sure images are not corrupted

### XML Parse Error
- Check if NFO files contain valid XML
- Some old or manually created NFO files may be malformed

## Testing

Create test data to try out the catalog generator:

```bash
# Create test data
python create_test_data.py

# Generate catalog
python jellyork_catalog.py test_jellyfin

# Open the PDF
```

The test data includes:
- 7 movies (including titles with articles in different languages)
- 2 TV shows with multiple seasons
- Sample audio/subtitle information

## System Requirements

- Python 3.7+
- ~50 MB free space for dependencies
- Sufficient RAM for image processing (depends on collection size)
