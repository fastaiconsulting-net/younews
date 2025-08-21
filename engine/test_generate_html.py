
from younews_reporter.convert_to_html import convert_md_to_html


if __name__ == "__main__":
    TODAY = "2025:08:21-14:08:30"
    markdown_file = f"/Users/zachwolpe/Documents/build/younews/Engine/reports/{TODAY}/news-report.md"
    title_file = f"/Users/zachwolpe/Documents/build/younews/Engine/reports/{TODAY}/main_title.txt"
    audio_file = f"/Users/zachwolpe/Documents/build/younews/Engine/reports/{TODAY}/audio.wav"
    image_path = f"/Users/zachwolpe/Documents/build/younews/Engine/reports/{TODAY}/news-image.png"
    save_html_file = f"/Users/zachwolpe/Documents/build/younews/Engine/reports/{TODAY}/news-report-v2.html"

    with open(markdown_file, "r") as f:
        report_txt = f.read()

    print('............. Convert Markdown to HTML .............')
    styled_html = convert_md_to_html(
        markdown_content=report_txt,
        secondary_title=">Younews Daily Report",
        image_path_to_embed=image_path,
        embed_audio_file=audio_file,
        )
    with open(save_html_file, "w") as f:
        f.write(styled_html)
    print('saved to :', save_html_file)
    input('Press Enter to continue...')
    import subprocess
    output = "reports/2025:08:21-14:08:30/news-report-v2.html"
    subprocess.run(["open", output])
    