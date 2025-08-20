from datetime import datetime
import requests


def generate_index_html(
        docs_for_frontend: list,
        base_html_doc_path: str = "./generate_html/base_index.html",
        save_path: str = '../index.html'):
    # Read the template index.html
    with open(base_html_doc_path, "r") as f:
        html_content = f.read()

    if not docs_for_frontend:
        return

    # Get the most recent article (first item)
    most_recent_date, most_recent_title, most_recent_link = docs_for_frontend[0]
    # Format the date for display
    formatted_date = most_recent_date.strftime("%B %d, %Y")
    # Update the Today's Featured Story section
    html_content = html_content.replace(
        '<p class="todays-news-subtitle">August 15, 2025</p>',
        f'<p class="todays-news-subtitle">{formatted_date}</p>'
    )
    html_content = html_content.replace(
        'src="https://younews-reports.s3.eu-west-2.amazonaws.com/2025%3A08%3A15-15%3A16%3A49/news-report.html"',
        f'src="{most_recent_link}"'
    )

    # Generate HTML for all articles
    articles_html = ""
    for date, title, link in docs_for_frontend:
        formatted_date = date.strftime("%B %d, %Y")
        article_html = f"""
                <a href="{link}" class="article-card">
                    <div class="article-date">{formatted_date}</div>
                    <div class="article-title">{title}</div>
                </a>
        """
        articles_html += article_html

    # Replace the articles section
    start_marker = '<div class="articles-grid">'
    end_marker = '</div>\n        </section>'
    # end_marker = '</div>\n            </div>\n        </section>'
    start_idx = html_content.find(start_marker) + len(start_marker)
    end_idx = html_content.find(end_marker, start_idx)

    if start_idx >= len(start_marker) and end_idx > start_idx:
        new_content = html_content[:start_idx] + articles_html + html_content[end_idx:]
    else:
        print("Warning: Could not find articles section markers")
        new_content = html_content

    # Write the modified content back to index.html
    with open(save_path, "w") as f:
        f.write(new_content)


def extract_date(key):
    date = key.split('/')[0]
    try:
        date = datetime.strptime(date, '%Y:%m:%d-%H:%M:%S')
        return date
    except Exception:
        return None


def _update_files(files, date, value):
    if date in files.keys():
        files[date].append(value)
    else:
        files[date] = [value]
    return files


def generate_urls(file: str):
    return f"https://younews-reports.s3.eu-west-2.amazonaws.com/{file}"


def extract_urls(response):
    dates = []
    files = {}
    for r in response['Contents']:
        date = extract_date(r['Key'])
        if date:
            dates.append(date)
            url = generate_urls(r['Key'])
            files = _update_files(files, date, url)
    return dates, files


def extract_report_name(files: list, date: str):
    for file in files:
        if "main_title.txt" in file:
            url = file
            response = requests.get(url)
            title = response.text.strip()
            return title
    return f"> younews daily report [{date}]"


def extract_html_doc(files: list):
    for file in files:
        if "news-report.html" in file:
            return file
    return None