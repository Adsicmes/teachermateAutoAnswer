from mitmproxy import http
import re
import json

papers = {}


def request(flow: http.HTTPFlow) -> None:
    pass


# https://v18.teachermate.cn/wechat-api/v3/students/papers/656308/questions?page=0
def response(flow: http.HTTPFlow) -> None:
    pattern = r"https://v18\.teachermate\.cn/wechat-api/v3/students/papers/(\d+)/questions\?page=(\d+)"
    match = re.match(pattern, flow.request.url)

    if not match:
        return

    paper_id = match.group(1)
    page_num = match.group(2)
    print("Paper ID:", paper_id)
    print("Page Number:", page_num)

    global papers
    if not papers.get(paper_id):
        papers[paper_id] = {}
    papers[paper_id][page_num] = flow.response.json()

    with open(f"paper-{paper_id}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(papers[paper_id], indent=4, ensure_ascii=False))

    print(flow.response.text)
