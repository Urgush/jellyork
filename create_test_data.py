#!/usr/bin/env python3
"""
Creates a test directory with sample NFO files and images
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def create_test_structure():
    """Creates a test directory structure"""
    
    base = Path("test_jellyfin")
    base.mkdir(exist_ok=True)
    
    # Movies
    movies = base / "Movies"
    movies.mkdir(exist_ok=True)
    
    # Movie 1
    movie1 = movies / "Inception (2010)"
    movie1.mkdir(exist_ok=True)
    create_movie_nfo(
        movie1 / "movie.nfo",
        title="Inception",
        year="2010",
        plot="A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O."
    )
    create_poster(movie1 / "poster.jpg", "Inception", "2010")
    
    # Movie 2
    movie2 = movies / "The Matrix (1999)"
    movie2.mkdir(exist_ok=True)
    create_movie_nfo(
        movie2 / "movie.nfo",
        title="The Matrix",
        year="1999",
        plot="A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers."
    )
    create_poster(movie2 / "poster.jpg", "The Matrix", "1999")
    
    # Movie 3
    movie3 = movies / "Interstellar (2014)"
    movie3.mkdir(exist_ok=True)
    create_movie_nfo(
        movie3 / "movie.nfo",
        title="Interstellar",
        year="2014",
        plot="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."
    )
    create_poster(movie3 / "poster.jpg", "Interstellar", "2014")
    
    # Movie 4 - German article
    movie4 = movies / "Das Boot (1981)"
    movie4.mkdir(exist_ok=True)
    create_movie_nfo(
        movie4 / "movie.nfo",
        title="Das Boot",
        year="1981",
        plot="The claustrophobic world of a WWII German U-boat; boredom, filth and sheer terror."
    )
    create_poster(movie4 / "poster.jpg", "Das Boot", "1981")
    
    # Movie 5 - French article
    movie5 = movies / "Le Fabuleux Destin d'Amélie Poulain (2001)"
    movie5.mkdir(exist_ok=True)
    create_movie_nfo(
        movie5 / "movie.nfo",
        title="Le Fabuleux Destin d'Amélie Poulain",
        year="2001",
        plot="Amélie is an innocent and naive girl in Paris with her own sense of justice. She decides to help those around her and, along the way, discovers love."
    )
    create_poster(movie5 / "poster.jpg", "Le Fabuleux", "2001")
    
    # Movie 6 - Spanish article
    movie6 = movies / "El Laberinto del Fauno (2006)"
    movie6.mkdir(exist_ok=True)
    create_movie_nfo(
        movie6 / "movie.nfo",
        title="El Laberinto del Fauno",
        year="2006",
        plot="In the Falangist Spain of 1944, the bookish young stepdaughter of a sadistic army officer escapes into an eerie but captivating fantasy world."
    )
    create_poster(movie6 / "poster.jpg", "El Laberinto", "2006")
    
    # Movie 7 - English indefinite article
    movie7 = movies / "A Beautiful Mind (2001)"
    movie7.mkdir(exist_ok=True)
    create_movie_nfo(
        movie7 / "movie.nfo",
        title="A Beautiful Mind",
        year="2001",
        plot="After John Nash, a brilliant but asocial mathematician, accepts secret work in cryptography, his life takes a turn for the nightmarish."
    )
    create_poster(movie7 / "poster.jpg", "A Beautiful", "2001")
    
    # TV Shows
    shows = base / "TV Shows"
    shows.mkdir(exist_ok=True)
    
    # TV Show 1
    show1 = shows / "Breaking Bad"
    show1.mkdir(exist_ok=True)
    create_tvshow_nfo(
        show1 / "tvshow.nfo",
        title="Breaking Bad",
        year="2008",
        plot="A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family's future."
    )
    create_poster(show1 / "poster.jpg", "Breaking Bad", "2008-2013")
    
    # Seasons for Breaking Bad
    for season_num in range(1, 6):  # 5 seasons
        season_dir = show1 / f"Season {season_num:02d}"
        season_dir.mkdir(exist_ok=True)
        
        # Season poster
        create_poster(season_dir / f"season{season_num:02d}-poster.jpg", 
                     f"Season {season_num}", "")
        
        # Create some episode NFOs
        episodes_in_season = 13 if season_num < 5 else 16  # Last season has more
        for ep_num in range(1, episodes_in_season + 1):
            create_episode_nfo(
                season_dir / f"S{season_num:02d}E{ep_num:02d}.nfo",
                title=f"Episode {ep_num}",
                season=season_num,
                episode=ep_num
            )
    
    # TV Show 2
    show2 = shows / "Stranger Things"
    show2.mkdir(exist_ok=True)
    create_tvshow_nfo(
        show2 / "tvshow.nfo",
        title="Stranger Things",
        year="2016",
        plot="When a young boy disappears, his mother, a police chief and his friends must confront terrifying supernatural forces in order to get him back."
    )
    create_poster(show2 / "poster.jpg", "Stranger Things", "2016")
    
    # Seasons for Stranger Things
    for season_num in range(1, 5):  # 4 seasons
        season_dir = show2 / f"Season {season_num:02d}"
        season_dir.mkdir(exist_ok=True)
        
        # Season poster
        create_poster(season_dir / "poster.jpg", 
                     f"Season {season_num}", "")
        
        # Create episode NFOs
        episodes_in_season = 8 if season_num < 3 else 9
        for ep_num in range(1, episodes_in_season + 1):
            create_episode_nfo(
                season_dir / f"S{season_num:02d}E{ep_num:02d}.nfo",
                title=f"Episode {ep_num}",
                season=season_num,
                episode=ep_num
            )
    
    print(f"✓ Test directory created: {base.absolute()}")
    print(f"  - {len(list(movies.iterdir()))} movies")
    print(f"  - {len(list(shows.iterdir()))} TV shows")
    
    # Count seasons and episodes
    total_seasons = 0
    total_episodes = 0
    for show_dir in shows.iterdir():
        if show_dir.is_dir():
            seasons = [d for d in show_dir.iterdir() if d.is_dir() and d.name.startswith('Season')]
            total_seasons += len(seasons)
            for season_dir in seasons:
                episodes = list(season_dir.glob("*.nfo"))
                total_episodes += len(episodes)
    
    print(f"  - {total_seasons} seasons")
    print(f"  - {total_episodes} episodes")
    print(f"\nTest with: python jellork_catalog.py {base.absolute()}")


def create_movie_nfo(path: Path, title: str, year: str, plot: str):
    """Creates a movie NFO file"""
    nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>{title}</title>
    <year>{year}</year>
    <plot>{plot}</plot>
    <outline>{plot[:100]}...</outline>
    <fileinfo>
        <streamdetails>
            <audio>
                <codec>DTS</codec>
                <language>eng</language>
                <channels>6</channels>
            </audio>
            <audio>
                <codec>AC3</codec>
                <language>ger</language>
                <channels>6</channels>
            </audio>
            <subtitle>
                <language>eng</language>
            </subtitle>
            <subtitle>
                <language>ger</language>
            </subtitle>
            <subtitle>
                <language>fra</language>
            </subtitle>
        </streamdetails>
    </fileinfo>
</movie>"""
    path.write_text(nfo_content, encoding='utf-8')


def create_tvshow_nfo(path: Path, title: str, year: str, plot: str):
    """Creates a TV show NFO file"""
    nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<tvshow>
    <title>{title}</title>
    <year>{year}</year>
    <plot>{plot}</plot>
    <overview>{plot}</overview>
</tvshow>"""
    path.write_text(nfo_content, encoding='utf-8')


def create_episode_nfo(path: Path, title: str, season: int, episode: int):
    """Creates an episode NFO file"""
    nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<episodedetails>
    <title>{title}</title>
    <season>{season}</season>
    <episode>{episode}</episode>
    <fileinfo>
        <streamdetails>
            <audio>
                <codec>AAC</codec>
                <language>eng</language>
                <channels>2</channels>
            </audio>
            <audio>
                <codec>AAC</codec>
                <language>ger</language>
                <channels>2</channels>
            </audio>
            <subtitle>
                <language>eng</language>
            </subtitle>
            <subtitle>
                <language>ger</language>
            </subtitle>
        </streamdetails>
    </fileinfo>
</episodedetails>"""
    path.write_text(nfo_content, encoding='utf-8')


def create_poster(path: Path, title: str, year: str):
    """Creates a simple poster image"""
    import sys
    
    # Create image
    width, height = 300, 450
    img = Image.new('RGB', (width, height), color='#2C3E50')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([10, 10, width-10, height-10], outline='#ECF0F1', width=3)
    
    # Platform-specific font loading
    font_title = None
    font_year = None
    
    try:
        if sys.platform == "darwin":  # macOS
            font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 24)
            font_year = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
        elif sys.platform == "linux":  # Linux
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_year = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        elif sys.platform == "win32":  # Windows
            font_title = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 24)
            font_year = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 18)
        else:
            # Unknown platform - use default
            font_title = ImageFont.load_default()
            font_year = ImageFont.load_default()
    except Exception as e:
        # Fallback to default font if platform-specific font fails
        print(f"  Note: Using default font (platform font not found: {e})")
        font_title = ImageFont.load_default()
        font_year = ImageFont.load_default()
    
    # Title centered
    bbox_title = draw.textbbox((0, 0), title, font=font_title)
    text_width = bbox_title[2] - bbox_title[0]
    text_height = bbox_title[3] - bbox_title[1]
    x = (width - text_width) / 2
    y = height / 2 - 20
    
    draw.text((x, y), title, fill='#ECF0F1', font=font_title)
    
    # Year
    if year:
        bbox_year = draw.textbbox((0, 0), year, font=font_year)
        year_width = bbox_year[2] - bbox_year[0]
        x_year = (width - year_width) / 2
        draw.text((x_year, y + 40), year, fill='#BDC3C7', font=font_year)
    
    # Save
    img.save(path, quality=85)


if __name__ == "__main__":
    create_test_structure()
