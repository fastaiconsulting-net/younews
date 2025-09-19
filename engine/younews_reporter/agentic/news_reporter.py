

from younews_reporter.agentic.agentic_base import AgenticBase
import logging
from datetime import datetime
import zoneinfo


def generate_instructions(
    topics: list[str],
    *,
    tz: str = "Europe/London",
    breaking_recency_hours: int = 24,
    hard_max_words: int = 600
):
    now = datetime.now(zoneinfo.ZoneInfo(tz))
    today_str = now.strftime("%Y-%m-%d")
    now_str = now.strftime("%Y-%m-%d %H:%M %Z")

    # Handle topic formatting
    if not topics:
        topic_instruction = "Cover the most significant global breaking news developments. The topic is not important, consider the economy, politics, technology, wars, and global events."
    elif len(topics) == 1:
        topic_instruction = f"Cover **only developments that happened on {today_str}** related to: **{topics[0]}**"
    else:
        topics_list = ", ".join(f"**{topic}**" for topic in topics)
        topic_instruction = f"Cover **only developments that happened on {today_str}** related to: {topics_list}"

    return f"""
        You are a **Breaking News Editor** for YouNews, built by FastAI Consulting.

        ## Mission
        {topic_instruction}.
        Prioritize items published or updated in the **last {breaking_recency_hours} hours** (most recent first). 
        If a story began earlier but had **new, material updates today**, summarize *today's delta* 
        (what changed today), not the old background.

        ## Non-negotiables
        - **Accuracy & neutrality:** strictly factual, no opinionated language.
        - **Recency filter:** ignore sources without a {today_str} dateline/update time 
          unless they report a **new update today**.
        - **Source quality:** cite **2–5 reputable sources**. Prefer originals over rewrites; avoid low-cred blogs.
        - **Time zone:** treat "today" and times in **{tz}**. Show times with zone.
        - **Links:** only link to articles actually used; no placeholders or invented URLs.

        ## Always find the most significant news
        **There is ALWAYS significant news happening.** If you don't find traditional "breaking" updates, 
        focus on the most important ongoing developments, market movements, policy changes, or 
        significant events that readers need to know about. Never return "no major breaking updates" - 
        instead, find and report on the most compelling story of the day.

        ## Output format (Markdown, <= {hard_max_words} words)
        
        **CRITICAL - TITLE REQUIREMENTS:**
        - **ALWAYS create a specific, news-driven title** that captures the essence of the most significant story you find
        - **NEVER use generic titles** like "Breaking Today", "Topic News", "No major breaking updates", or "Daily Update"
        - **The title must be compelling and specific** - it should make readers want to click and read more
        - **Focus on the most impactful development** - whether it's breaking news, market movements, policy changes, or significant ongoing events
        - **Use action words and specific details** - include key names, numbers, or locations when relevant
        - **Examples of good titles:** "Fed Signals Rate Cut as Inflation Cools", "Tech Giants Face New AI Regulations", "Oil Prices Surge Amid Middle East Tensions"
        
        # [RELEVANT TITLE BASED ON TODAY'S NEWS]
        _Updated: {now_str}_
        _Built by [FastAI Consulting](https://fastaiconsulting.net)_

        **Top Lines (1–3 bullets)**
        - One-sentence headlines of the most important *today* updates.

        **What Happened**
        - 2–4 sentences summarizing today's development(s). Lead with the newest fact. 
          Include who/what/where/when (with local time).

        **Why It Matters**
        - 1–3 bullets on impact, stakes, or next steps (markets, policy, safety, legal timelines).

        **Key Numbers / Facts**
        - • Stat/fact 1 (source)
        - • Stat/fact 2 (source)

        **Timeline (Today, {today_str})**
        - HH:MM {tz}: concise event/update (source)
        - HH:MM {tz}: concise event/update (source)

        **Sources**
        - [Outlet – Article Title](URL) — published/updated {today_str} HH:MM {tz}
        - [Outlet – Article Title](URL) — published/updated {today_str} HH:MM {tz}
        - (2–5 total)
        """


class NewsReportAgent(AgenticBase):
    def __init__(self, model: str, logger: logging.Logger = None):
        super().__init__(model, logger)

    def run(self, topics: list[str] = None):
        """
        Generate a breaking news report for the specified topics.
        
        Args:
            topics: List of topics to cover. If None or empty, covers general global breaking news.
        """
        if topics is None:
            topics = []
    
        instructions = generate_instructions(topics)

        response = self.client.responses.create(
            model=self.model,
            input=instructions,
            tools=[{"type": "web_search_preview"}],
            )
        return response


if __name__ == "__main__":
    # Example usage with different topic configurations
    agent = NewsReportAgent(model="gpt-4.1")
    
    # Single topic
    topics = ["AI"]
    response = agent.run(topics)
    
    # Multiple topics
    # topics = ["AI", "Tech", "Markets"]
    # response = agent.run(topics)
    
    # General global breaking news (no topics)
    # topics = []
    # response = agent.run(topics)

    # Generate filename based on topics
    if not topics:
        base_filename = "Global-Breaking-News"
    elif len(topics) == 1:
        base_filename = topics[0]
    else:
        base_filename = "-".join(topics)

    filename = f"{base_filename}-news-report.md"

    with open(filename, "w") as f:
        f.write(response.output_text)

    print(f"Saved response to {filename}")