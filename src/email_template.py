from datetime import datetime

def create_youtube_style_html_body(videos):
    """
    Generates a responsive HTML email body with a rich YouTube-style design.
    Enhanced with gradients, shadows, and premium visual elements.
    Optimized for iPhone/Gmail rendering.
    """
    
    # CSS styles defined inline for email compatibility
    # Palette: White (#FFFFFF), Red (#FF0000), Black (#0F0F0F), Gray (#606060)
    
    # Base styles
    style_body = "font-family: 'Roboto', 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px; color: #0f0f0f;"
    style_container = "max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05);"
    
    # Header
    style_header = "padding: 16px 24px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; justify-content: space-between; background-color: #ffffff;"
    style_logo_text = "font-family: 'Roboto', sans-serif; font-size: 22px; font-weight: 700; letter-spacing: -0.5px; color: #0f0f0f;"
    style_date_badge = "background-color: #f2f2f2; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; color: #606060;"
    
    style_content_wrapper = "padding: 24px;"
    
    # Card
    style_card = "margin-bottom: 40px; border-bottom: 1px solid #f0f0f0; padding-bottom: 32px;"
    
    # Thumbnail
    style_thumbnail_container = "position: relative; width: 100%; border-radius: 12px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
    style_thumbnail_img = "width: 100%; display: block; aspect-ratio: 16/9; object-fit: cover;"
    style_duration_badge = "position: absolute; bottom: 8px; right: 8px; background-color: rgba(0, 0, 0, 0.8); color: #ffffff; padding: 3px 6px; border-radius: 4px; font-size: 12px; font-weight: 500; letter-spacing: 0.5px;"
    
    # Video Info
    style_video_info = "padding: 0 4px;"
    style_video_title = "font-size: 18px; font-weight: 600; line-height: 1.4; color: #0f0f0f; margin-bottom: 12px; text-decoration: none; display: block;"
    
    style_meta_text = "font-size: 12px; color: #606060; margin-bottom: 16px;"
    
    # Summary Box
    style_summary_box = "background-color: #f2f2f2; padding: 16px; border-radius: 12px; margin-bottom: 16px; position: relative;"
    style_summary_header = "display: flex; align-items: center; margin-bottom: 8px; font-size: 12px; font-weight: 700; color: #0f0f0f;"
    style_ai_icon = "margin-right: 6px; font-size: 14px;"
    style_summary_text = "font-size: 14px; line-height: 1.6; color: #0f0f0f;"
    
    # Action Button
    style_action_button = "display: inline-block; background-color: #f2f2f2; color: #0f0f0f; padding: 10px 20px; border-radius: 20px; text-decoration: none; font-size: 14px; font-weight: 500;"
    
    style_footer = "text-align: center; padding: 32px; background-color: #f9f9f9; color: #909090; font-size: 12px;"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="x-apple-disable-message-reformatting">
        <title>YouTube Summary</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            
            /* Reset */
            body, p, h1, h2, h3 {{ margin: 0; padding: 0; }}
            img {{ max-width: 100%; height: auto; }}
            
            /* Mobile Responsive Styles */
            @media only screen and (max-width: 600px) {{
                body {{ padding: 0 !important; }}
                .container {{ 
                    border-radius: 0 !important; 
                    box-shadow: none !important;
                }}
                .header {{ 
                    padding: 12px 16px !important; 
                }}
                .logo-text {{ 
                    font-size: 18px !important; 
                }}
                .date-badge {{ 
                    font-size: 11px !important; 
                    padding: 4px 8px !important; 
                }}
                .content-wrapper {{ 
                    padding: 16px !important; 
                }}
                .card {{ 
                    margin-bottom: 24px !important; 
                    padding-bottom: 24px !important; 
                }}
                .video-title {{ 
                    font-size: 16px !important; 
                }}
                .meta-text {{ 
                    font-size: 11px !important; 
                }}
                .summary-box {{ 
                    padding: 12px !important; 
                }}
                .summary-text {{ 
                    font-size: 13px !important; 
                }}
                .action-button {{ 
                    font-size: 13px !important; 
                    padding: 8px 16px !important; 
                }}
            }}
        </style>
    </head>
    <body style="{style_body}">
        <div class="container" style="{style_container}">
            <!-- Header -->
            <div class="header" style="{style_header}">
                <span class="logo-text" style="{style_logo_text}">YouTube Summary</span>
                <div class="date-badge" style="{style_date_badge}">{datetime.now().strftime('%b %d')}</div>
            </div>

            <div class="content-wrapper" style="{style_content_wrapper}">
    """
    
    for idx, video in enumerate(videos, 1):
        # Format date
        try:
            published_at = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')).strftime('%Y.%m.%d')
        except:
            published_at = video['published_at']
        
        # Format view count
        view_count = video['view_count']
        if view_count >= 1000000:
            view_str = f"{view_count/1000000:.1f}M views"
        elif view_count >= 1000:
            view_str = f"{view_count/1000:.1f}K views"
        else:
            view_str = f"{view_count} views"
        
        # Last card should not have bottom border/margin
        current_style_card = style_card
        if idx == len(videos):
            current_style_card = "margin-bottom: 0; border-bottom: none; padding-bottom: 0;"
        
        html += f"""
                <!-- Video Card {idx} -->
                <div class="card" style="{current_style_card}">
                    <div class="thumbnail-container" style="{style_thumbnail_container}">
                        <a href="{video['url']}" style="display: block;">
                            <img src="{video['thumbnail']}" alt="{video['title']}" class="thumbnail-img" style="{style_thumbnail_img}">
                            <div class="duration-badge" style="{style_duration_badge}">{video['duration']}</div>
                        </a>
                    </div>
                    
                    <div class="video-info" style="{style_video_info}">
                        <a href="{video['url']}" class="video-title" style="{style_video_title}">{video['title']}</a>
                        
                        <div class="meta-text" style="{style_meta_text}">
                            {video['channel_title']} • {view_str} • {published_at}
                        </div>

                        <div class="summary-box" style="{style_summary_box}">
                            <div class="summary-header" style="{style_summary_header}">
                                <span class="ai-icon" style="{style_ai_icon}">✨</span> AI Summary
                            </div>
                            <div class="summary-text" style="{style_summary_text}">
                                {video['summary'].replace(chr(10), '<br>')}
                            </div>
                        </div>

                        <a href="{video['url']}" class="action-button" style="{style_action_button}">Watch on YouTube</a>
                    </div>
                </div>
        """
    
    html += f"""
            </div>
            <!-- Footer -->
            <div class="footer" style="{style_footer}">
                &copy; {datetime.now().year} YouTube Summary Agent
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
