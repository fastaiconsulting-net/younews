    
import markdown
import os

from younews_reporter.utils import extract_main_title


def apply_younews_styling(html_content, title="YouNews Report", image_path=None):
    """
    Apply YouNews styling to HTML content generated from markdown.
    
    Args:
        html_content (str): The HTML content to style
        title (str): The title for the page
        image_path (str, optional): Path to an image to embed in the document
    
    Returns:
        str: Complete HTML document with YouNews styling applied
    """
    # Read the CSS file
    css_path = os.path.join(os.path.dirname(__file__), 'styles.css')
    try:
        with open(css_path, 'r') as css_file:
            css_content = css_file.read()
    except FileNotFoundError:
        # Fallback CSS if file not found
        css_content = """
        body { 
            background-color: #0D0D0D; 
            color: #FFFFFF; 
            font-family: 'Courier New', monospace; 
            padding: 2rem; 
        }
        h1, h2 { color: #8B5CF6; }
        .main-title { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .secondary-title { font-size: 1.5rem; margin-bottom: 1rem; color: #A78BFA; }
        .fastai-link { font-size: 1.2rem; margin: 1rem 0; }
        """
    
    # Create the complete HTML document
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="main-title">> YOUNEWS DAILY REPORT</h1>
        <p class="fastai-link" style="text-align: center; margin: 1rem 0; color: var(--text-secondary);">
            <a href="https://fastaiconsulting.net" target="_blank" 
               style="color: var(--accent-purple); text-decoration: none; font-size: 1.2rem;">
                ⚡️ a FastAIConsulting project ⚡️
            </a>
        </p>
        <h2 class="secondary-title" style="text-align: center; margin-bottom: 2rem;">{title}</h2>
        {f'''<div style="text-align: center; margin: 2rem 0; 
                    display: flex; justify-content: center; align-items: center;">
            <img src="{image_path}" alt="Report Image" 
                 style="max-width: 100%; height: auto; border-radius: 12px; 
                        border: 2px solid var(--border-color); 
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        display: block; margin: 0 auto;">
        </div>''' if image_path else ''}
        {html_content}
    </div>
</body>
</html>"""
    
    return html_template


def convert_md_to_html(
    md_file_path: str = None,
    markdown_content: str = None,
    secondary_title: str = "> YOUNEWS DAILY REPORT",
    image_path_to_embed: str = None,
):
    
    assert md_file_path is not None or markdown_content is not None, "Either md_file_path or markdown_content must be provided"

    if md_file_path is not None:
        # From a file
        with open(md_file_path, "r") as md_file:
            markdown_content = md_file.read()

    # Extract the main title from the markdown content
    main_title = extract_main_title(markdown_content)
    
    # Remove the main title from the markdown content to avoid duplication
    lines = markdown_content.strip().split('\n')
    filtered_lines = []
    title_removed = False
    
    for line in lines:
        line_stripped = line.strip()
        # Check for markdown heading (# Title) or bold markdown (**Title**)
        if not title_removed and (
            line_stripped.startswith('# ') or 
            (line_stripped.startswith('**') and line_stripped.endswith('**'))
        ):
            title_removed = True
            continue
        filtered_lines.append(line)
    
    # Reconstruct markdown content without the main title
    filtered_markdown = '\n'.join(filtered_lines).strip()

    # Convert markdown to HTML with proper list handling
    html_content = markdown.markdown(
        filtered_markdown,
        extensions=['markdown.extensions.nl2br', 'markdown.extensions.sane_lists']
    )

    # Apply YouNews styling with the extracted main title
    styled_html = apply_younews_styling(html_content, main_title, image_path_to_embed)

    return styled_html


if __name__ == "__main__":
    secondary_title = "> YOUNEWS DAILY REPORT"
    md_file_path = "reports/news-report.md"
    html_file_path = "reports/news-report.html"
    image_path = "news-report.png"
    
    # Optional: Add an image to the report
    # image_path = "reports/news-image.png"  # Uncomment and set path to include an image
    
    convert_md_to_html(md_file_path, html_file_path, secondary_title, image_path)
    # convert_md_to_html(md_file_path, html_file_path, secondary_title, image_path)  # With image