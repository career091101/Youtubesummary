from datetime import datetime

def create_youtube_style_html_body(videos):
    """
    Generates a responsive HTML email body with a rich YouTube-style design.
    Enhanced with gradients, shadows, and premium visual elements.
    Optimized for iPhone/Gmail rendering.
    """
    
    # CSS styles defined inline for email compatibility
    # Palette: White (#FFFFFF), Red (#FF0000), Black (#0F0F0F), Gray (#606060)
    
    # Base styles (Desktop defaults, overridden by media queries in <head>)
    style_body = "font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; color: #333333; background-color: #f4f4f4; margin: 0; padding: 20px;"
    style_container = "max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05);"
    
    # Header
    style_header = "background: #ffffff; padding: 20px 24px; border-bottom: 1px solid #eeeeee; display: flex; align-items: center;"
    style_logo_text = "font-size: 20px; font-weight: 700; color: #0F0F0F; display: flex; align-items: center; letter-spacing: -0.5px;"
    style_logo_icon = "color: #FF0000; margin-right: 8px; font-size: 24px;"
    
    style_content_wrapper = "padding: 24px;"
    style_intro = "margin-bottom: 24px; color: #555555; font-size: 15px; text-align: center;"
    
    # Card
    style_card = "margin-bottom: 32px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); border: 1px solid #f0f0f0;"
    
    # Thumbnail
    style_thumbnail_wrapper = "position: relative; width: 100%; overflow: hidden; padding-top: 56.25%;" # 16:9 Aspect Ratio
    style_thumbnail = "position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; display: block;"
    
    style_card_content = "padding: 20px;"
    style_video_title = "margin: 0 0 12px 0; font-size: 18px; font-weight: 700; line-height: 1.4; color: #0F0F0F;"
    style_link = "text-decoration: none; color: #0F0F0F;"
    
    style_meta = "font-size: 12px; color: #666666; margin-bottom: 16px; display: flex; flex-wrap: wrap; gap: 12px; align-items: center;"
    style_meta_item = "display: flex; align-items: center; gap: 4px;"
    
    style_summary_box = "background-color: #f8f9fa; padding: 16px; border-radius: 8px; font-size: 14px; color: #444444; line-height: 1.7; border-left: 3px solid #FF0000;"
    
    style_footer = "text-align: center; font-size: 12px; color: #999999; padding: 24px; background-color: #f4f4f4;"
    
    style_divider = "height: 1px; background-color: #eeeeee; margin: 24px 0;"

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
            
            /* Mobile Responsive Styles */
            @media only screen and (max-width: 600px) {{
                .body-wrapper {{ padding: 0 !important; background-color: #ffffff !important; }}
                .container {{ width: 100% !important; max-width: 100% !important; border-radius: 0 !important; box-shadow: none !important; }}
                .content-wrapper {{ padding: 16px !important; }}
                .card {{ margin-bottom: 24px !important; border: none !important; box-shadow: none !important; border-bottom: 1px solid #eeeeee !important; border-radius: 0 !important; }}
                .video-title {{ font-size: 16px !important; }}
                .summary-box {{ padding: 12px !important; }}
            }}
        </style>
    </head>
    <body class="body-wrapper" style="{style_body}">
        <div class="container" style="{style_container}">
            <!-- Header -->
            <div style="{style_header}">
                <div style="{style_logo_text}">
                    <span style="{style_logo_icon}">▶</span> YouTube Summary
                </div>
            </div>

            <div class="content-wrapper" style="{style_content_wrapper}">
                <!-- Intro -->
                <p style="{style_intro}">
                    Daily AI Updates • <strong>{datetime.now().strftime('%b %d, %Y')}</strong>
                </p>
                
                <div style="{style_divider}"></div>
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
            view_str = f"{view_count/1000000:.1f}M"
        elif view_count >= 1000:
            view_str = f"{view_count/1000:.1f}K"
        else:
            view_str = str(view_count)
        
        html += f"""
                <!-- Video Card {idx} -->
                <div class="card" style="{style_card}">
                    <div style="{style_thumbnail_wrapper}">
                        <a href="{video['url']}" style="text-decoration: none; display: block;">
                            <img src="{video['thumbnail']}" alt="{video['title']}" style="{style_thumbnail}">
                        </a>
                    </div>
                    <div style="{style_card_content}">
                        <h3 class="video-title" style="{style_video_title}">
                            <a href="{video['url']}" style="{style_link}">{video['title']}</a>
                        </h3>
                        
                        <div style="{style_meta}">
                            <span style="{style_meta_item}">📺 {video['channel_title']}</span>
                            <span style="{style_meta_item}">👁️ {view_str}</span>
                            <span style="{style_meta_item}">⏱️ {video['duration']}</span>
                            <span style="{style_meta_item}">📅 {published_at}</span>
                        </div>
                        
                        <div class="summary-box" style="{style_summary_box}">
                            <div style="font-weight: 700; color: #FF0000; font-size: 12px; margin-bottom: 8px; letter-spacing: 0.5px;">AI SUMMARY</div>
                            <div style="color: #444444;">
                                {video['summary'].replace(chr(10), '<br>')}
                            </div>
                        </div>
                    </div>
                </div>
        """
    
    html += f"""
            </div>
            <!-- Footer -->
            <div style="{style_footer}">
                <p>&copy; {datetime.now().year} YouTube Summary Agent</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
