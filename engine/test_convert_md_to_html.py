from younews_reporter.convert_to_html import convert_md_to_html


if __name__ == "__main__":
    TODAY = "2025:08:21-13:43:13"
    md_file_path = f"reports/{TODAY}/news-report.md"
    html_file_path = f"reports/{TODAY}/news-report-v2.html"
    img_path = f"https://younews-reports.s3.eu-west-2.amazonaws.com/{TODAY}/news-image.png"


    print('> Converting md to html...')
    styled_html = convert_md_to_html(
        md_file_path=md_file_path,
        image_path_to_embed=img_path,
        )
    
    with open(html_file_path, 'w') as f:
        f.write(styled_html)
    
    # (md_file_path, html_file_path, img_path)
    print(f"> Converted {md_file_path} to {html_file_path}")