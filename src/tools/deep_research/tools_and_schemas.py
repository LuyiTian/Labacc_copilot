import hashlib
import os
import pickle
from functools import wraps

from pydantic import BaseModel, Field
from tavily import TavilyClient

from src.config.keys import API_KEYS

client = TavilyClient(API_KEYS["tavily"]["api_key"])


class SearchQueryList(BaseModel):
    rationale: str = Field(
        description="A brief explanation of why these queries are relevant to the research topic."
    )
    query: list[str] = Field(
        description="A list of search queries to be used for web research."
    )
    response_language: str = Field(
        description="The language in which the response should be generated, typically the same as the user's input question's language."
    )


class Reflection(BaseModel):
    knowledge_gap: str = Field(
        description="A description of what information is missing or needs clarification."
    )
    is_sufficient: bool = Field(
        description="Whether the provided summaries are sufficient to answer the user's question."
    )
    useful_expansion: str = Field(
        description="A description of what information would be useful to expand the understanding of the topic."
    )
    follow_up_queries: list[str] = Field(
        description="A list of follow-up search queries to address the knowledge gap and useful expansion."
    )


class SearchCache:
    def __init__(self, cache_dir: str = "search_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def __call__(self, func):
        @wraps(func)
        def wrapper(query: str, count: int = 10):
            # Create hex hash of query and count
            query_hash = hashlib.md5(f"{query}_{count}".encode()).hexdigest()
            cache_file = os.path.join(self.cache_dir, f"{query_hash}.pkl")

            # Try to load from cache
            if os.path.exists(cache_file):
                with open(cache_file, "rb") as f:
                    return pickle.load(f)

            # If not cached, call the function and cache result
            result = func(query, count)
            with open(cache_file, "wb") as f:
                pickle.dump(result, f)

            return result

        return wrapper


@SearchCache()
def search_with_tavily(query: str, count: int = 10) -> list[str]:
    """
    Perform a web search using the Tavily API and return a list of URLs.

    Args:
        query (str): The search query to use.
        count (int): The number of search results to return.

    Returns:
        List[str]: A list of URLs from the search results.
    """
    # Truncate query to 400 characters if too long
    if len(query) > 400:
        query = query[:397] + "..."

    response = client.search(
        query=query,
        max_results=count,
        search_depth="advanced",
        chunks_per_source=5
        # include_raw_content="text"
    )
    # {
    #   "query": "Who is hired with the most recent Meta super star AI team?",
    #   "follow_up_questions": null,
    #   "answer": null,
    #   "images": [],
    #   "results": [
    #     {
    #       "title": "Meet the people Zuck hired for his AI superintelligence team",
    #       "url": "https://www.businessinsider.com/meet-the-people-zuck-hired-for-his-ai-superintelligence-team-2025-7?op=1",
    #       "content": "Meta CEO Mark Zuckerberg just hired his dream team of AI avengers, raising the stakes in the all-out battle between Big Tech companies for talent.",
    #       "score": 0.7451949,
    #       "raw_content": "# Meet Zuckerberg's brand-new AI dream team\n\n![Mark Zuckerberg](https://i.insider.com/681cc2f3a466d2b74ab56231?width=700)\n\nMeta CEO Mark Zuckerberg just hired his dream team of AI avengers, raising the stakes in the all-out battle between Big Tech companies for talent.\n\nOn Monday, Zuckerberg [announced](https://www.businessinsider.com/meta-ceo-mark-zuckerberg-announces-superintelligence-ai-division-internal-memo-2025-6) the launch of Meta Superintelligence Labs, a group of star researchers that Meta poached from its AI competitors and has tasked with building a \"personal superintelligence for everyone.\"\n\nInterest in the new unit surged after OpenAI CEO [Sam Altman claimed](https://www.businessinsider.com/sam-altman-meta-tried-poaching-openai-staff-ai-talent-war-2025-6) that Meta is offering recruits $100 million signing bonuses. But the team also offers a glimpse into what Meta is up to on AI, which it has mostly kept under wraps so far.\n\nMeta is clearly interested in using multimodal AI, which means using AI to generate images, video, and speech. It has hired multiple people with expertise in this domain.\n\nThe new hires also show Meta is keeping very close tabs on OpenAI, since most of them worked on training OpenAI's latest models. (Meta wouldn't be the only Big Tech firm [obsessed with beating ChatGPT](https://www.businessinsider.com/google-used-chatgpt-to-improve-bard-scale-ai-documents-2025-6).)\n\nMeta has said it will disclose other hires later, so it's still early. Regardless, the hiring blitz has commanded Silicon Valley's attention. Whatever form it takes, Meta's new team stands to shape whoever controls the future of AI.\n\nMeta didn't comment for this article.\n\n## Related stories\n\n![](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/logos/placeholder.png)\n\n### Business Insider tells the innovative stories you want to know\n\n![](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/logos/placeholder.png)\n\n### Business Insider tells the innovative stories you want to know\n\n## Leaders\n\n**Alexandr Wang** will lead the team as its Chief AI Officer, according to Zuckerberg's [memo](https://www.businessinsider.com/meta-ceo-mark-zuckerberg-announces-superintelligence-ai-division-internal-memo-2025-6). At only 28, Wang has already cofounded and led Scale AI, a startup that helps Big Tech train their latest AI models. Meta [recently invested](https://www.businessinsider.com/meta-scale-ai-15-billion-alexandr-wang-acquihire-ai-2025-6) $14 billion into Scale as part of a deal to hire Wang. Wang has a strong interest in AI progress: while he was at Scale, for example, the startup [helped create](https://scale.com/research/humanitys-last-exam) an especially difficult test for AI systems called Humanity's Last Exam.\n\n**Nat Friedman** will co-lead Meta's lab with Wang, Zuck's memo says. Friedman is best-known as the former CEO of Github and as an AI investor who has [backed](https://nfdg.com/) startups like Stripe and Perplexity. Friedman has also served on Meta's AI advisory [group](https://investor.atmeta.com/Advisors/default.aspx) since May 2024. He's dabbled in other projects, too, like funding a program to [decode an ancient Roman scroll](https://www.businessinsider.com/ai-decipher-ancient-philosophers-work-buried-mount-vesuvius-2024-2) charred by the Pompeii eruption.\n\n## Researchers and others\n\n**Trapid Bansal** is a former research scientist at OpenAI, where he co-created the company's leading o-series of AI models, Meta's announcement says. OpenAI's o3 model is [touted](https://platform.openai.com/docs/models) by OpenAI as its most powerful \"reasoning\" model. Reasoning is [a trend](https://www.businessinsider.com/openai-meta-agi-ai-models-reasoning-race-2024-4) that's taken over AI this past year, and involves AI chatbots fleshing out their 'thoughts' before answering a question.\n\n**Jiahui Yu** used to lead OpenAI's perception team, which works on multimodal AI, and co-led Gemini's multimodal efforts when he worked at Google, according to his [personal website](https://jiahuiyu.com/). He's also helped build some of OpenAI's latest models, Meta says.\n\n**Shuchao Bi** also worked on multimodal AI at OpenAI, co-creating GPT-4o's voice mode. He also co-created YouTube shorts when he worked at Google, according to a Columbia University [profile page](https://ai.columbia.edu/events/distinguished-lecture-shuchao-bi-openai).\n\n**Huiwen Chang** is an expert in multimodal AI who helped launch image generation for OpenAI's GPT-4o model, Meta says. Prior to that, she used to work for Google and Adobe, according to her LinkedIn [profile](https://www.linkedin.com/in/huiwen-chang-999962156/).\n\n**Ji Lin** is a former OpenAI research scientist who specializes in multimodal and reasoning models, his personal [website](https://www.linji.me/) says. He's also a co-creator of several of OpenAI's latest AI models, Meta says.\n\n**Hongyu Ren** also worked at OpenAI, where he led a team focused on post-training AI models. \"Post-training\" means improving an AI model's performance after the model itself has already been created.\n\n**Shengjia Zhao** is a co-creator of ChatGPT and previously led synthetic data at OpenAI, Meta says. Synthetic data means using AI-generated data to make AI models smarter — [another big AI trend](https://www.businessinsider.com/ai-synthetic-data-industry-debate-over-fake-2024-8) as AI labs run out of materials to train on.\n\n**Johan Schalkwyk** worked as a machine learning lead at Sesame, a startup [building](https://www.sesame.com/team) software and hardware that can chat naturally with people. Schalkwyk previously worked at Google on speech-related technologies, including leading a 'moonshot' effort to expand Google's support to 1,000 languages, according to his LinkedIn page.\n\n**Pei Sun** worked for Google creating the most recent generations of AI models for Google's self-driving car subsidiary Waymo. Sun also worked on post-training and reasoning efforts for Gemini, Google's ChatGPT competitor, according to Meta's announcement.\n\n**Joel Pobar** worked on building inference systems for OpenAI rival Anthropic. That means making sure massively popular AI systems have enough data centers and other tools to run smoothly. Prior to joining Anthropic, Pobar worked at Meta (then Facebook) for about a decade, leading engineering teams, his LinkedIn page shows.\n\n## Read next\n\n![](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/logos/placeholder.png)\n\n### Business Insider tells the innovative stories you want to know\n\n![](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/logos/placeholder.png)\n\n### Business Insider tells the innovative stories you want to know\n\n![](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/logos/placeholder.png)\n\n### Business Insider tells the innovative stories you want to know\n\n![](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/logos/placeholder.png)\n\n### Business Insider tells the innovative stories you want to know\n\n![Business Insider](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/logos/stacked-black.svg)\n![Download on the App Store](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/badges/app-store-badge.svg)\n![Get it on Google Play](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/badges/google-play-badge.svg)\n![Insider.com TM Logo](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/INSIDER/US/logos/insider-com-trademark-opt.svg)\n![Insider](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/INSIDER/US/logos/Insider-logo-dark-opt.svg)\n![Insider-Inc Logo](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/INSIDER/US/logos/insider-inc.svg)\n![Tech Insider Logo](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/BI/US/logos/Tech-Insider-opt.svg)\n![Business Insider DE Logo](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/BI/DE/logos/BI-DE-Black-on-Light-final-footer-logo-opt.svg)\n![Insider Media Logo](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/MI/logos/markets-insider-stacked.svg)\n![Insider Media Logo](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/INSIDER/US/logos/insider-media.svg)\n![News Insider Logo](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/INSIDER/US/logos/news-insider.svg)\n![Silicon Alley Logo](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E)\n![](/public/assets/INSIDER/US/logos/silicon-alley-insider.svg)\n![](https://sb.scorecardresearch.com/p?c1=2&c2=9900186&cv=3.6.0&;cj=1&comscorekw=tech)\n\nJump to"
    #     }
    #   ],
    #   "response_time": 2.65
    # }
    return response["results"]
