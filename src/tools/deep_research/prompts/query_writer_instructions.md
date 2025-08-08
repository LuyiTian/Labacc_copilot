Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Each query should focus on one specific aspect of the original question. Sometimes you may have to break down the original query into a linearized step-by-step process, then you should write out the first step as the query, you will have the opportunity to read the search result and further expand the queries.
- Keep queries concise and under 300 characters each.
- Don't produce more than required queries total.
- Queries should be diverse, if the topic is broad, generate more than 1 query.
- Don't generate multiple similar queries, 1 is enough.
- Query should ensure that the most current information is gathered.
- When the user is asking for literature review, you should not directly search for "literature review", instead, you should generate queries that will help you learn about the topic and write the review.
- You will write the rationale and the queries in ENGLISH ONLY, even if the user's topic is in another language. Then you will set the response_language to the user's language for the final answer.

Format: 
- Format your response as a JSON object with ALL two of these exact keys:
   - "rationale": Brief explanation of why these queries are relevant
   - "query": A list of search queries

Examples:

Example 1:
User's Topic: What revenue grew more last year apple stock or the number of people buying an iphone
```json
{
    "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth by fiscal year", "Apple stock price growth fiscal year 2024"],
    "response_language": "English"
}
```

Example 2:
User's Topic: 虚拟博物馆的社交设计研究
```json
{
    "rationale": "To comprehensively research virtual museum social design, we need both Chinese and English sources. Chinese queries will capture local research and implementations, while English queries will access international academic literature and best practices.",
    "query": ["virtual museum social design research review", "digital museum user interaction experience design", "Current trends in virtual museum social design"],
    "response_language": "Chinese"
}
```

User's Topic: {{research_topic}}
Current Date: {{current_date}}
Number Queries: {{number_queries}}