# 1. The problem

## 1

  I'm trying to create a design and I need examples and inspiration to inform my decision.

## 2

  This is an issue for many developers who need a quick UI, and for marketers who are exploring branding options. It can help design teaching materials, advertisements, brochures and of course, websites.

# 2. The solution

## 1.

  The goal of this solution is to query a variety of expert-created website designs, analyze them and categorize them according to design elements, and then use this library to serve users designs based on their description. The chat model can then discuss with the user whether the design matches their goals, and suggest resources and revisions to help them continue.

## 2. Tools

  a. LLM - There are a few models used, relying on gpt-4o for the design analysis and the chat, and gpt-4o-mini for the knowledge graph due to speed and cost issues. gpt-4o was important for the initial web design analysis because the input data used both visual graphics and text descriptions.

  b. Embedding model - We're using OpenAI's default embedding model

  c. Orchestration - The initial goal was to use a LangGraph agent with a tool node, however there were issues with getting the agent to call the custom designed tool. graph.ipynb shows the initial agent design, which could be re-applied later with more debugging.

  d. Vector database - We're using FAISS to store the design elements and the user's description.

  e. Monitoring - LangSmith

  f. Evaluation - LangSmith, used with evaluation.ipynb

  g. UI - Chainlit
  
 ## 3. Agents

  An important agent for this project was the initial design analysis of the scraped designs. Since the rest of the application follow on that, the analysis provided by that agent is important and could use its own testing, evaluation and improvement.

  Ideally the application should be able to discuss the user's goals and description before fetching a result, but this was not implemented due to time constraints and the difficulty of getting an agent to call a custom tool.

# 3. Data Production

## 1. I created my own design analysis data by setting up a headless browser to take screenshots and css files, then pipe to an agent to provide a condensed json file with the key design elements and categories. While the agent is able to reference public websites during its discussion, the designs it returns are limited to this dataset.

It's possible to modify this process to scrape a selection of sites, providing a more robust dataset. A more advanced version could utilize a search api to find ideal sites, call the scraper and analyzer, and then serve results dynamically. However, doing so much processing on the fly would take a long time between user messages, so it's better to have a set of sites ahead of time.

## 2.

  Because the documents are all designed by my own application, they are already ideally separated to provide one document per result. As such, there is no need to use a splitter.

# 4. RAG prototype

## 1. [https://huggingface.co/spaces/Technologic101/imagineui](https://huggingface.co/spaces/Technologic101/imagineui) It Works!

# 5. Evaluation

## 1. RAGAS

  There's a demonstration of creating a RAGAS test set, but it has a key flaw. RAGAS synthetic data is designed for question and answer responses, generally having a specific answer. Our users are not sending questions, but a description of what they want.

  Looking over the generated ragas queries, they don't represent our users.

  Instead, use LangSmith's evaluation tools to create a custom evaluator, taking in a set of manually created prompts and returning a score for their relevance to the initial query. Using this score, we can evaluate the performance of the application in a variety of use cases.

## 2. Evaluation lessons

  The initial design analysis and json output varied widely in quality and changed substantially with different prompt usage. Some are excellent and provide the application with relevant information, while others have misleading keywords. "minimalism" in particular is often misapplied.

  Also, with only 141 examples, there are not as many options as we might like, but given the constraints the matches are reasonably good. Returning the reasoning with the model's results gives insights into why the designs were selected, we could inform refinement of the initial scraping and analysis.

# 6. Fine-tuning open-source embeddings

  1. I fine-tuned an embedding model that traded performance for semantic similarity, but found a surprising result. One of the test results was so poor it scored a zero, and manual inspection confirmed that the fine-tuned model had picked a considerably worse choice than the original. I uploaded the moddel to Hugging Face, but did not use it.

# 7. Assessment

  ## 1. Performance

  Performance comparison is found in fine_tune_embeddings.ipynb.

  Throughout the course of development, it is clear that there are many opportunities to improve the application, particularly when it comes to improved prompt engineering and potentially tighter control over which LLM models are used at different stages. It's likely that fine-tuning didn't substantially improve performance because the dataset is fairly small, and fine-tuning is intended for larger sets.

  ## 2. Roadmap

  There are many opportunities to improve and expand this application.

  The code base has artifacts of CSS production, as the initial goal was to write functional CSS based on the returned designed. This application still serves as a potential foundation for that, but the challenges of producing working CSS are significant, even more so testing and evaluating the results.

  So ideally, this application would continue to refine its goal of scraping, analyzing, and serving web designs, and could be packages as an exportable node to be used in other applications.

  potential improvements:

  a. Improved design analysis
  b. Scrape designs from more sites
  c. Working graph with separate agent functions

#. 8 - Demo Time!

[Loom Video]([https://huggingface.co/Technologic101/css_zen_design_embeddings](https://www.loom.com/share/174e34a28a4a4913a930f2c9dabb6bee))
  
