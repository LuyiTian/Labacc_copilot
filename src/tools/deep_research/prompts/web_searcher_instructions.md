Conduct targeted Web Searches to gather the most recent, credible detailed information on "{{research_topic}}" and synthesize it into a verifiable text artifact.

Instructions:
- Query should ensure that the most current information is gathered. The current date is {{current_date}}.
- Conduct multiple, diverse searches to gather comprehensive information.
- Consolidate key findings while meticulously tracking the source(s) for each specific piece of information. When reporting findings, ensure the whole context is clear, not just the conclusion. This means including the background, methodology, and any relevant data that supports the findings.
- Provide a direct and detailed answer without including over-generalised statements, such as saying "something is limited / needs careful work", you need to tell why, where and how. Focus on delivering specific and valuable information only. When you cite conclusions, make sure you introduce the context / settings / examples / experiments / reasons.
- Trust official and reputable sources, such as academic journals, government reports, and established news outlets. Avoid using unverified or low-quality sources.
- The output should be a well-written summary or report based on your search findings. Bring in as much detail as possible from the search results. You can output up to 2000 words if needed.
- Only include the information found in the search results, don't make up any information.
- When you are citing sources, use the format "[display_name](url)" as in Markdown format, where the display name is based on the source domain and identifiable title, for example, if the source is "https://en.wikipedia.org/wiki/Stochastic_gradient_descent", "Wikipedia_stochastic" as the display name is a wonderful choice, making the citation looks like "[Wikipedia_stochastic](https://en.wikipedia.org/wiki/Stochastic_gradient_descent)". This helps in maintaining clarity and consistency in citations. NEVER USE NUMBERS.

Research Topic:
{{research_topic}}

Web Search API Response:
{{search_results}}

Response Language:
{{response_language}}

Just type up your response in a clean, professional markdown format text in Response Language. 