"""
PDF Generator for Jellyfin Catalog
"""

from pathlib import Path
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, 
    PageBreak, Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from PIL import Image as PILImage
import io


class PDFGenerator:
    """Creates PDF documents from media items"""
    
    def __init__(self, output_path: str, image_quality: int = 75, 
                 poster_width_cm: float = 4.0, season_width_cm: float = 3.0):
        self.output_path = output_path
        self.image_quality = image_quality
        self.poster_width_cm = poster_width_cm
        self.season_width_cm = season_width_cm
        
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.story = []
    
    def _setup_custom_styles(self):
        """Creates custom styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Media title style
        self.styles.add(ParagraphStyle(
            name='MediaTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=6,
            spaceBefore=12
        ))
        
        # Year/type style
        self.styles.add(ParagraphStyle(
            name='MediaInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7F8C8D'),
            spaceAfter=8
        ))
        
        # Description style
        self.styles.add(ParagraphStyle(
            name='Description',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_LEFT,
            spaceAfter=20
        ))
    
    def generate(self, items: List, sort_method: str = 'title'):
        """Generates the PDF document"""
        # Title page
        self._add_title_page(len(items), sort_method)
        
        # Statistics
        self._add_statistics(items)
        
        # Media items
        self._add_media_items(items)
        
        # Create PDF
        print(f"\nCreating PDF: {self.output_path}")
        self.doc.build(self.story)
        print(f"PDF successfully created!")
    
    def _add_title_page(self, item_count: int, sort_method: str):
        """Adds title page"""
        self.story.append(Spacer(1, 3*cm))
        
        title = Paragraph("Jellyfin Media Catalog", self.styles['CustomTitle'])
        self.story.append(title)
        
        self.story.append(Spacer(1, 1*cm))
        
        info_text = f"""
        <para alignment="center">
        <b>Number of media:</b> {item_count}<br/>
        <b>Sorting:</b> {self._get_sort_name(sort_method)}<br/>
        <b>Created on:</b> {self._get_current_date()}
        </para>
        """
        info = Paragraph(info_text, self.styles['Normal'])
        self.story.append(info)
        
        self.story.append(PageBreak())
    
    def _add_statistics(self, items: List):
        """Adds statistics page"""
        # Count movies and TV shows
        movies = sum(1 for item in items if item.media_type == 'movie')
        shows = sum(1 for item in items if item.media_type == 'tvshow')
        
        # Year statistics
        years = {}
        for item in items:
            if item.year:
                year = item.year
                years[year] = years.get(year, 0) + 1
        
        stats_title = Paragraph("Statistics", self.styles['Heading1'])
        self.story.append(stats_title)
        self.story.append(Spacer(1, 0.5*cm))
        
        # Statistics table
        data = [
            ['Category', 'Count'],
            ['Movies', str(movies)],
            ['TV Shows', str(shows)],
            ['Total', str(len(items))],
        ]
        
        table = Table(data, colWidths=[8*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table)
        self.story.append(PageBreak())
    
    def _add_media_items(self, items: List):
        """Adds all media items"""
        catalog_title = Paragraph("Media Catalog", self.styles['Heading1'])
        self.story.append(catalog_title)
        self.story.append(Spacer(1, 0.5*cm))
        
        for item in items:
            self._add_media_item(item)
    
    def _add_media_item(self, item):
        """Adds a single media item"""
        elements = []
        
        # Title without numbering
        title_text = item.title
        title = Paragraph(title_text, self.styles['MediaTitle'])
        elements.append(title)
        
        # Year and type
        type_name = "Movie" if item.media_type == 'movie' else "TV Show"
        info_text = f"<i>{type_name} • {item.year or 'Year unknown'}</i>"
        
        # For TV shows: Add number of seasons
        if item.media_type == 'tvshow' and item.seasons:
            total_episodes = sum(s.episode_count for s in item.seasons)
            info_text = f"<i>{type_name} • {item.year or 'Year unknown'} • {len(item.seasons)} seasons • {total_episodes} episodes</i>"
        
        info = Paragraph(info_text, self.styles['MediaInfo'])
        elements.append(info)
        
        # Audio and subtitle information
        if item.audio_tracks or item.subtitle_tracks:
            tech_info_parts = []
            
            if item.audio_tracks:
                audio_str = ", ".join(item.audio_tracks)
                tech_info_parts.append(f"<b>Audio:</b> {audio_str}")
            
            if item.subtitle_tracks:
                subtitle_str = ", ".join(item.subtitle_tracks)
                tech_info_parts.append(f"<b>Subtitles:</b> {subtitle_str}")
            
            tech_info_text = " | ".join(tech_info_parts)
            tech_info = Paragraph(tech_info_text, self.styles['MediaInfo'])
            elements.append(tech_info)
        
        # Poster and description side by side
        content_data = []
        
        # Poster (if available)
        if item.poster_path and item.poster_path.exists():
            try:
                img = self._prepare_image(item.poster_path, max_width=self.poster_width_cm*cm)
                content_data.append([img, self._get_description(item.description)])
            except Exception as e:
                print(f"Error loading {item.poster_path}: {e}")
                content_data.append(['', self._get_description(item.description)])
        else:
            # Only description
            desc = self._get_description(item.description)
            elements.append(desc)
        
        # If we have poster + text, create table
        if content_data:
            # Calculate column widths based on poster size
            poster_col_width = (self.poster_width_cm + 0.5) * cm  # Add small margin
            text_col_width = (17 - self.poster_width_cm - 0.5) * cm  # Remaining width
            
            content_table = Table(content_data, colWidths=[poster_col_width, text_col_width])
            content_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(content_table)
        
        # Season overview for TV shows
        if item.media_type == 'tvshow' and item.seasons:
            elements.append(Spacer(1, 0.3*cm))
            self._add_season_overview(elements, item.seasons)
        
        elements.append(Spacer(1, 0.3*cm))
        
        # Separator line
        line_table = Table([['_' * 100]], colWidths=[17*cm])
        line_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.lightgrey),
            ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.3*cm))
        
        # Keep item together
        self.story.append(KeepTogether(elements))
    
    def _add_season_overview(self, elements: list, seasons: list):
        """Adds season overview with images"""
        # Heading
        season_title = Paragraph("<b>Seasons:</b>", self.styles['Normal'])
        elements.append(season_title)
        elements.append(Spacer(1, 0.2*cm))
        
        # Create grid with seasons (3 per row)
        seasons_per_row = 3
        season_rows = []
        current_row = []
        
        for season in seasons:
            # Create season cell
            season_cell = self._create_season_cell(season)
            current_row.append(season_cell)
            
            # New row when 3 seasons reached
            if len(current_row) == seasons_per_row:
                season_rows.append(current_row)
                current_row = []
        
        # Add last incomplete row
        if current_row:
            # Fill with empty cells
            while len(current_row) < seasons_per_row:
                current_row.append('')
            season_rows.append(current_row)
        
        # Create table
        if season_rows:
            # Calculate column width based on season poster size
            col_width = (self.season_width_cm + 2.5) * cm  # Add margin for text
            season_table = Table(season_rows, colWidths=[col_width] * seasons_per_row)
            season_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(season_table)
    
    def _create_season_cell(self, season) -> list:
        """Creates a cell for a season with image and info"""
        cell_elements = []
        
        # Season poster (small)
        if season.poster_path and season.poster_path.exists():
            try:
                img = self._prepare_image(season.poster_path, max_width=self.season_width_cm*cm)
                cell_elements.append(img)
            except Exception as e:
                print(f"Error loading {season.poster_path}: {e}")
        
        # Season info
        season_text = f"<b>Season {season.season_number}</b><br/><i>{season.episode_count} episodes</i>"
        season_para = Paragraph(season_text, self.styles['Normal'])
        cell_elements.append(season_para)
        
        return cell_elements
    
    def _prepare_image(self, image_path: Path, max_width: float = 4*cm) -> Image:
        """Prepares and optimizes image for PDF"""
        from io import BytesIO
        
        # Open with PIL
        pil_img = PILImage.open(image_path)
        
        # Convert to RGB if necessary (removes alpha channel)
        if pil_img.mode in ('RGBA', 'LA', 'P'):
            background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
            if pil_img.mode == 'P':
                pil_img = pil_img.convert('RGBA')
            background.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode in ('RGBA', 'LA') else None)
            pil_img = background
        elif pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
        
        # Calculate target size maintaining aspect ratio
        # max_width is already in reportlab points (1/72 inch)
        aspect = pil_img.height / pil_img.width
        target_width = max_width
        target_height = target_width * aspect
        
        # Maximum height is dynamic: 1.5x the width (typical poster ratio)
        # But no more than 9cm to fit on page
        max_height = min(max_width * 1.5, 9 * cm)
        if target_height > max_height:
            target_height = max_height
            target_width = target_height / aspect
        
        # Convert reportlab points to pixels for resizing
        # We want reasonable resolution: use 150 DPI for good quality
        dpi = 150
        points_per_inch = 72
        
        # Calculate pixel dimensions
        width_inches = target_width / points_per_inch
        height_inches = target_height / points_per_inch
        new_width_px = int(width_inches * dpi)
        new_height_px = int(height_inches * dpi)
        
        # Only resize if image is larger (don't upscale)
        if new_width_px < pil_img.width or new_height_px < pil_img.height:
            pil_img_resized = pil_img.resize(
                (new_width_px, new_height_px), 
                PILImage.Resampling.LANCZOS
            )
        else:
            # Image is already small enough, don't upscale
            pil_img_resized = pil_img
        
        # Save to BytesIO with compression
        img_buffer = BytesIO()
        pil_img_resized.save(
            img_buffer, 
            format='JPEG', 
            quality=self.image_quality,
            optimize=True
        )
        img_buffer.seek(0)
        
        # Create reportlab Image with the correct display size
        img = Image(img_buffer, width=target_width, height=target_height)
        return img
    
    def _get_description(self, description: str) -> Paragraph:
        """Creates description paragraph"""
        if not description:
            desc_text = "<i>No description available</i>"
        else:
            # Limit length and clean text
            desc_text = description[:500]
            if len(description) > 500:
                desc_text += "..."
            # Escape HTML characters
            desc_text = desc_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        return Paragraph(desc_text, self.styles['Description'])
    
    def _get_sort_name(self, sort_method: str) -> str:
        """Returns readable name for sort method"""
        names = {
            'title': 'By title (A-Z)',
            'year': 'By year (newest first)',
            'type': 'By type (Movies/TV Shows)'
        }
        return names.get(sort_method, sort_method)
    
    def _get_current_date(self) -> str:
        """Returns current date"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
