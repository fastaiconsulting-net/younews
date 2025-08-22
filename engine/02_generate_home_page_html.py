# def generate_urls

# write config file for frontend
# today = "2025:08:19-14:32:12/"
# with open(f"../Frontent/reports_config.yaml", "w") as f:
#     f.write(f"today: {today}")
#     f.write(f"markdown_news_report_path: {markdown_news_report_path}")


# list all files in s3 bucket
import boto3
from datetime import datetime
import requests
from pprint import pprint


from generate_html.utils import generate_index_html, extract_date, extract_report_name, extract_html_doc, extract_urls


def build_html_doc(
    s3_client,
    s3_bucket_name: str = "younews-reports",
    base_html_doc_path='./generate_html/base_index.html',
    save_path='../index.html'
):

    response = s3_client.list_objects_v2(Bucket=s3_bucket_name)
    dates, files = extract_urls(response)

    docs_for_frontend = []
    ordered_date_keys = sorted(files.keys(), reverse=True)
    for i, date in enumerate(ordered_date_keys):
        _files = files[date]
        report_name = extract_report_name(_files, date)
        html_doc = extract_html_doc(_files)
        if not html_doc:
            continue
        docs_for_frontend.append((date, str(report_name), html_doc))

    generate_index_html(
        docs_for_frontend,
        base_html_doc_path=base_html_doc_path,
        save_path=save_path)


if __name__ == "__main__":
    s3 = boto3.client('s3')
    build_html_doc(s3)
