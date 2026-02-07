#!/usr/bin/env python3
"""
Jellyfin Catalog Generator
Creates PDF documentation from Jellyfin NFO files and images
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from PIL import Image
import argparse


@dataclass
class Season:
    """Represents a season of a TV show"""
    season_number: int
    episode_count: int
    poster_path: Optional[Path]


@dataclass
class MediaItem:
    """Represents a media item (movie or TV show)"""
    title: str
    year: Optional[str]
    description: Optional[str]
    media_type: str  # 'movie' or 'tvshow'
    poster_path: Optional[Path]
    nfo_path: Path
    audio_tracks: List[str]  # List of audio tracks (e.g., "German", "English")
    subtitle_tracks: List[str]  # List of subtitles (e.g., "German", "English")
    seasons: Optional[List[Season]] = None  # Only for TV shows: list of seasons
    
    def __repr__(self):
        if self.media_type == 'tvshow' and self.seasons:
            return f"TV SHOW: {self.title} ({self.year}) - {len(self.seasons)} seasons"
        return f"{self.media_type.upper()}: {self.title} ({self.year})"


class JellyfinScanner:
    """Scans Jellyfin directories and reads NFO files"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.items: List[MediaItem] = []
    
    def scan(self) -> List[MediaItem]:
        """Scans all NFO files in the base directory"""
        print(f"Scanning directory: {self.base_path}")
        
        # Find all NFO files
        nfo_files = list(self.base_path.rglob("*.nfo"))
        print(f"Found: {len(nfo_files)} NFO files")
        
        # Separate movies and TV show NFOs
        tvshow_nfos = []
        movie_nfos = []
        episode_nfos = []
        
        for nfo_file in nfo_files:
            filename = nfo_file.name.lower()
            if filename == 'tvshow.nfo':
                tvshow_nfos.append(nfo_file)
            elif filename.startswith('s') and filename.endswith('.nfo'):
                # Episode NFOs (e.g., S01E01.nfo) - skip
                episode_nfos.append(nfo_file)
            else:
                # Check root tag for movies
                try:
                    tree = ET.parse(nfo_file)
                    root = tree.getroot()
                    if root.tag == 'movie':
                        movie_nfos.append(nfo_file)
                    elif root.tag == 'episodedetails':
                        episode_nfos.append(nfo_file)
                except:
                    pass
        
        print(f"  - {len(movie_nfos)} movie NFOs")
        print(f"  - {len(tvshow_nfos)} TV show NFOs")
        print(f"  - {len(episode_nfos)} episode NFOs (will be skipped)")
        
        # Parse movies
        for nfo_file in movie_nfos:
            item = self._parse_nfo(nfo_file)
            if item:
                self.items.append(item)
        
        # Parse TV shows with season information
        for nfo_file in tvshow_nfos:
            item = self._parse_tvshow_with_seasons(nfo_file)
            if item:
                self.items.append(item)
        
        print(f"Successfully parsed: {len(self.items)} items")
        return self.items
    
    def _parse_tvshow_with_seasons(self, nfo_path: Path) -> Optional[MediaItem]:
        """Parses a TV show NFO and collects season information"""
        try:
            tree = ET.parse(nfo_path)
            root = tree.getroot()
            
            # Extract TV show information
            title = self._get_text(root, 'title')
            year = self._get_text(root, 'year')
            description = (self._get_text(root, 'plot') or 
                          self._get_text(root, 'outline') or
                          self._get_text(root, 'overview'))
            
            # Audio/subtitles from first episode of a season
            audio_tracks = self._extract_audio_tracks(root)
            subtitle_tracks = self._extract_subtitle_tracks(root)
            
            # Search for poster in same directory
            poster_path = self._find_poster(nfo_path.parent)
            
            # Collect season information
            seasons = self._collect_season_info(nfo_path.parent)
            
            # If no audio/subtitles in tvshow.nfo, get them from first episode
            if not audio_tracks and not subtitle_tracks and seasons:
                season_dir = nfo_path.parent / f"Season {seasons[0].season_number:02d}"
                if not season_dir.exists():
                    season_dir = nfo_path.parent / f"Season {seasons[0].season_number}"
                if season_dir.exists():
                    episode_nfos = list(season_dir.glob("*.nfo"))
                    if episode_nfos:
                        try:
                            ep_tree = ET.parse(episode_nfos[0])
                            ep_root = ep_tree.getroot()
                            audio_tracks = self._extract_audio_tracks(ep_root)
                            subtitle_tracks = self._extract_subtitle_tracks(ep_root)
                        except:
                            pass
            
            return MediaItem(
                title=title or "Unknown",
                year=year,
                description=description,
                media_type='tvshow',
                poster_path=poster_path,
                nfo_path=nfo_path,
                audio_tracks=audio_tracks,
                subtitle_tracks=subtitle_tracks,
                seasons=seasons
            )
            
        except Exception as e:
            print(f"Error parsing TV show {nfo_path}: {e}")
            return None
    
    def _collect_season_info(self, show_dir: Path) -> List[Season]:
        """Collects information about all seasons of a TV show"""
        seasons = []
        
        # Search for season directories
        season_dirs = []
        for item in show_dir.iterdir():
            if item.is_dir() and item.name.lower().startswith('season'):
                season_dirs.append(item)
        
        for season_dir in sorted(season_dirs):
            # Extract season number
            season_name = season_dir.name.lower()
            season_num = None
            
            # Try to extract number (e.g., "Season 01", "Season 1")
            import re
            match = re.search(r'season\s*(\d+)', season_name)
            if match:
                season_num = int(match.group(1))
            
            if season_num is None:
                continue
            
            # Count episode NFOs in this season
            episode_nfos = [f for f in season_dir.glob("*.nfo") 
                           if not f.name.lower().startswith('season')]
            episode_count = len(episode_nfos)
            
            # Search for season poster (pass show_dir for additional search locations)
            season_poster = self._find_season_poster(season_dir, season_num, show_dir)
            
            seasons.append(Season(
                season_number=season_num,
                episode_count=episode_count,
                poster_path=season_poster
            ))
        
        return sorted(seasons, key=lambda s: s.season_number)
    
    def _find_season_poster(self, season_dir: Path, season_num: int, show_dir: Path) -> Optional[Path]:
        """Searches for season poster in multiple locations"""
        # Priority 1: season01-poster files in show main directory (Jellyfin standard)
        show_poster_names = [
            f'season{season_num:02d}-poster.jpg',
            f'season{season_num:02d}-poster.png',
            f'season{season_num}-poster.jpg',
            f'season{season_num}-poster.png',
            f'season-{season_num:02d}-poster.jpg',
            f'season-{season_num:02d}-poster.png',
        ]
        
        for name in show_poster_names:
            poster = show_dir / name
            if poster.exists():
                return poster
        
        # Priority 2: Poster files in season directory
        season_poster_names = [
            'poster.jpg',
            'poster.png',
            'folder.jpg',
            'folder.png',
            f'season{season_num:02d}-poster.jpg',
            f'season{season_num:02d}-poster.png',
        ]
        
        for name in season_poster_names:
            poster = season_dir / name
            if poster.exists():
                return poster
        
        # Fallback: First image in directory
        for ext in ['.jpg', '.jpeg', '.png']:
            images = list(season_dir.glob(f'*{ext}'))
            if images:
                return images[0]
        
        return None
    
    def _parse_nfo(self, nfo_path: Path) -> Optional[MediaItem]:
        """Parses a single NFO file"""
        try:
            tree = ET.parse(nfo_path)
            root = tree.getroot()
            
            # Determine media type based on root tag
            media_type = root.tag  # 'movie' or 'tvshow'
            
            # Extract information
            title = self._get_text(root, 'title')
            year = self._get_text(root, 'year')
            
            # Description can be in different tags
            description = (self._get_text(root, 'plot') or 
                          self._get_text(root, 'outline') or
                          self._get_text(root, 'overview'))
            
            # Extract audio and subtitle information
            audio_tracks = self._extract_audio_tracks(root)
            subtitle_tracks = self._extract_subtitle_tracks(root)
            
            # Search for poster in same directory
            poster_path = self._find_poster(nfo_path.parent)
            
            return MediaItem(
                title=title or "Unknown",
                year=year,
                description=description,
                media_type=media_type,
                poster_path=poster_path,
                nfo_path=nfo_path,
                audio_tracks=audio_tracks,
                subtitle_tracks=subtitle_tracks
            )
            
        except ET.ParseError as e:
            print(f"Error parsing {nfo_path}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error at {nfo_path}: {e}")
            return None
    
    def _get_text(self, root: ET.Element, tag: str) -> Optional[str]:
        """Extracts text from an XML tag"""
        element = root.find(tag)
        return element.text.strip() if element is not None and element.text else None
    
    def _extract_audio_tracks(self, root: ET.Element) -> List[str]:
        """Extracts audio tracks from NFO file"""
        audio_tracks = []
        
        # Jellyfin/Kodi NFO format: <fileinfo><streamdetails><audio>
        fileinfo = root.find('fileinfo')
        if fileinfo is not None:
            streamdetails = fileinfo.find('streamdetails')
            if streamdetails is not None:
                for audio in streamdetails.findall('audio'):
                    language = audio.find('language')
                    codec = audio.find('codec')
                    channels = audio.find('channels')
                    
                    # Build audio info
                    parts = []
                    if language is not None and language.text:
                        lang = language.text.strip()
                        # Convert language codes
                        lang = self._convert_language_code(lang)
                        parts.append(lang)
                    if codec is not None and codec.text:
                        parts.append(codec.text.strip().upper())
                    if channels is not None and channels.text:
                        ch = channels.text.strip()
                        if ch:
                            parts.append(f"{ch}ch")
                    
                    if parts:
                        audio_tracks.append(" ".join(parts))
        
        return audio_tracks
    
    def _extract_subtitle_tracks(self, root: ET.Element) -> List[str]:
        """Extracts subtitles from NFO file"""
        subtitle_tracks = []
        
        # Jellyfin/Kodi NFO format: <fileinfo><streamdetails><subtitle>
        fileinfo = root.find('fileinfo')
        if fileinfo is not None:
            streamdetails = fileinfo.find('streamdetails')
            if streamdetails is not None:
                for subtitle in streamdetails.findall('subtitle'):
                    language = subtitle.find('language')
                    if language is not None and language.text:
                        lang = language.text.strip()
                        # Convert language codes
                        lang = self._convert_language_code(lang)
                        if lang not in subtitle_tracks:  # Avoid duplicates
                            subtitle_tracks.append(lang)
        
        return subtitle_tracks
    
    def _convert_language_code(self, code: str) -> str:
        """Converts language codes to readable names"""
        language_map = {
            'ger': 'German',
            'deu': 'German',
            'de': 'German',
            'eng': 'English',
            'en': 'English',
            'fra': 'French',
            'fre': 'French',
            'fr': 'French',
            'spa': 'Spanish',
            'es': 'Spanish',
            'ita': 'Italian',
            'it': 'Italian',
            'jpn': 'Japanese',
            'ja': 'Japanese',
            'rus': 'Russian',
            'ru': 'Russian',
            'chi': 'Chinese',
            'zh': 'Chinese',
            'por': 'Portuguese',
            'pt': 'Portuguese',
            'pol': 'Polish',
            'pl': 'Polish',
            'tur': 'Turkish',
            'tr': 'Turkish',
            'ara': 'Arabic',
            'ar': 'Arabic',
        }
        
        code_lower = code.lower()
        return language_map.get(code_lower, code.capitalize())
    
    def _find_poster(self, directory: Path) -> Optional[Path]:
        """Searches for poster images in directory"""
        # Typical Jellyfin poster names
        poster_names = ['poster.jpg', 'poster.png', 'folder.jpg', 'folder.png', 
                       'cover.jpg', 'cover.png']
        
        for name in poster_names:
            poster = directory / name
            if poster.exists():
                return poster
        
        # Fallback: First image in directory
        for ext in ['.jpg', '.jpeg', '.png']:
            images = list(directory.glob(f'*{ext}'))
            if images:
                return images[0]
        
        return None


class CatalogSorter:
    """Sorts media items by various criteria"""
    
    # Articles to ignore when sorting
    ARTICLES = {
        # German
        'der', 'die', 'das', 'ein', 'eine',
        # English
        'the', 'a', 'an',
        # French
        'le', 'la', 'les', 'un', 'une', 'des',
        # Spanish
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'
    }
    
    @staticmethod
    def _get_sort_key(title: str) -> str:
        """
        Creates a sort key that ignores articles at the beginning.
        Example: "The Matrix" becomes "matrix" for sorting
        """
        if not title:
            return ""
        
        # Convert to lowercase
        title_lower = title.lower().strip()
        
        # Split into words
        words = title_lower.split()
        if not words:
            return title_lower
        
        first_word = words[0]
        
        # Check if first word is an article
        if first_word in CatalogSorter.ARTICLES and len(words) > 1:
            # Remove article and return rest
            return ' '.join(words[1:])
        
        return title_lower
    
    @staticmethod
    def sort_by_title(items: List[MediaItem]) -> List[MediaItem]:
        """Sorts by title (alphabetically), ignoring articles at the beginning"""
        return sorted(items, key=lambda x: CatalogSorter._get_sort_key(x.title))
    
    @staticmethod
    def sort_by_year(items: List[MediaItem]) -> List[MediaItem]:
        """Sorts by year (newest first), alphabetically for same year"""
        return sorted(items, 
                     key=lambda x: (x.year or "0000", CatalogSorter._get_sort_key(x.title)), 
                     reverse=True)
    
    @staticmethod
    def sort_by_type(items: List[MediaItem]) -> List[MediaItem]:
        """Sorts by type (movies, then TV shows), then alphabetically"""
        return sorted(items, 
                     key=lambda x: (x.media_type, CatalogSorter._get_sort_key(x.title)))


def main():
    """Main function"""
    import time
    start_time = time.time()
    
    parser = argparse.ArgumentParser(
        description='Creates PDF catalog from Jellyfin media'
    )
    parser.add_argument('path', 
                       help='Path to Jellyfin media directory')
    parser.add_argument('-s', '--sort', 
                       choices=['title', 'year', 'type'],
                       default='title',
                       help='Sorting: title, year or type (default: title)')
    parser.add_argument('-o', '--output',
                       default='jellyfin_catalog.pdf',
                       help='Output PDF name (default: jellyfin_catalog.pdf)')
    parser.add_argument('-q', '--quality',
                       type=int,
                       default=75,
                       choices=range(1, 101),
                       metavar='QUALITY',
                       help='JPEG quality for images, 1-100 (default: 75, higher=better quality but larger file)')
    parser.add_argument('-w', '--poster-width',
                       type=float,
                       default=4.0,
                       metavar='WIDTH',
                       help='Maximum poster width in cm (default: 4.0)')
    parser.add_argument('--season-width',
                       type=float,
                       default=3.0,
                       metavar='WIDTH',
                       help='Maximum season poster width in cm (default: 3.0)')
    
    args = parser.parse_args()
    
    # Validate poster widths
    if args.poster_width < 1.0 or args.poster_width > 10.0:
        print("Error: Poster width must be between 1.0 and 10.0 cm")
        return
    if args.season_width < 1.0 or args.season_width > 10.0:
        print("Error: Season poster width must be between 1.0 and 10.0 cm")
        return
    
    # Scan directory
    scanner = JellyfinScanner(args.path)
    items = scanner.scan()
    
    if not items:
        print("No media found!")
        return
    
    # Sort items
    sorter = CatalogSorter()
    if args.sort == 'title':
        items = sorter.sort_by_title(items)
    elif args.sort == 'year':
        items = sorter.sort_by_year(items)
    elif args.sort == 'type':
        items = sorter.sort_by_type(items)
    
    # Output for verification
    print("\n" + "="*50)
    print(f"Found media ({len(items)}):")
    print("="*50)
    for item in items[:10]:  # Show first 10
        print(f"  {item}")
    if len(items) > 10:
        print(f"  ... and {len(items) - 10} more")
    
    # Create PDF
    from pdf_generator import PDFGenerator
    
    pdf_gen = PDFGenerator(
        args.output,
        image_quality=args.quality,
        poster_width_cm=args.poster_width,
        season_width_cm=args.season_width
    )
    pdf_gen.generate(items, args.sort)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Format time nicely
    if elapsed_time < 60:
        time_str = f"{elapsed_time:.1f} seconds"
    else:
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        time_str = f"{minutes}m {seconds:.1f}s"
    
    print(f"\n✓ Catalog successfully created: {args.output}")
    print(f"  Image quality: {args.quality}%, Poster width: {args.poster_width}cm, Season width: {args.season_width}cm")
    print(f"  Processing time: {time_str}")



if __name__ == "__main__":
    main()
