# Practical Prompt Engineering Techniques for LLMs

[![Dr Abdullah Azhar](https://miro.medium.com/v2/resize:fill:64:64/1*FBW2vt5zNWERzNat2vwwPA.jpeg)](/@abdullahazhar1071?source=post_page---byline--881c912eda16---------------------------------------)

[Dr Abdullah Azhar](/@abdullahazhar1071?source=post_page---byline--881c912eda16---------------------------------------)

6 min readAug 28, 2025

--

Listen

Share

Press enter or click to view image in full size

![]()

AI generated image by SORA

Large Language Models (LLMs) have moved from research labs into the daily workflows of developers, analysts, and even non-technical teams. Whether it’s **writing SQL queries, summarizing documents, generating code, or brainstorming product ideas**, the effectiveness of an LLM largely depends on the *quality of your prompts*.

And here’s the truth: **prompting is not magic, it’s engineering.**

In this article, we’ll explore practical prompt engineering techniques for LLMs. I’ll share frameworks, tested strategies, and examples you can apply immediately to improve results. By the end, you’ll not only understand *why prompts work the way they do* but also *how to systematically design them for reliability, precision, and scalability*.

This is a long read (~3000 words) because we’ll go deep. Grab a coffee, open a Jupyter notebook (you’ll want to try things), and let’s start.

## Why Prompt Engineering Matters

If you’ve ever asked an LLM to *“write a SQL query for monthly sales by region”* and got back something half-baked or incorrect, you already know why prompts matter.

Unlike deterministic programs, LLMs are **probabilistic generators**. They’re predicting the next most likely token based on your input. That means your prompt is not just an instruction — it’s part of the input distribution shaping the output.

Think of it like this:

* A *vague prompt* is like asking a stranger for directions in a foreign city. You’ll get a confused answer, maybe even the wrong street.
* A *clear, structured prompt* is like handing them a GPS map. You drastically improve the odds of getting where you want.

Good prompts = **less guesswork, more consistency, less post-editing**.

## The Building Blocks of a Good Prompt

Before diving into advanced techniques, let’s establish the foundations:

1. **Role definition** → Who is the LLM supposed to be?  
    Example: *“You are a data scientist specializing in time-series forecasting.”*
2. **Task clarity** → What exactly should it do?  
    Example: *“Generate a Python function that uses Prophet to forecast weekly sales.”*
3. **Constraints** → What rules should it follow?  
    Example: *“Limit the forecast to 12 weeks, and return only the Python code.”*
4. **Context** → What background does it need?  
    Example: *“Here is the CSV header: [‘date’, ‘sales’, ‘region’]. Use ‘date’ as the time column.”*
5. **Output format** → How should the answer be structured?  
    Example: *“Return the output as a Markdown code block with no explanation text.”*

These five ingredients are the DNA of effective prompting.

## Practical Prompt Engineering Techniques

Let’s move from theory into practice. Here are techniques that work consistently across OpenAI, Anthropic, and open-source LLMs.

## 1. Role Prompting

Humans respond differently depending on their role. LLMs are no different. By assigning a role, you prime the model into a certain *style, tone, and knowledge base*.

**Example:**

```
You are a senior data scientist mentoring a junior analyst.    
Explain how gradient boosting works, using analogies from sports.    
Keep the explanation under 200 words.
```

Result? The LLM adopts an *instructor persona* rather than dumping textbook jargon.

## 2. Few-Shot Prompting

Instead of telling, *“Do X”*, show the LLM how X looks.

**Example:** Classify sentiment.

```
Q: "The model performs exceptionally well."    
A: Positive    
  
Q: "The experiment was a complete disaster."    
A: Negative    
  
Q: "The dataset has some inconsistencies but can be cleaned."    
A: Neutral
```

This works because LLMs are *pattern learners*. Few examples anchor the response style.

**Pro tip:** Use **diverse but representative examples**. Too many can cause “overfitting” to your examples, while too few may fail to set the pattern.

## 3. Chain-of-Thought (CoT) Prompting

For reasoning tasks, explicitly tell the LLM to **think step by step**.

**Example:**

```
You are solving a math problem.    
Explain your reasoning step by step before giving the final answer.    
  
Problem: A train travels 60 km/h for 2 hours, then 90 km/h for 1 hour.    
What is the average speed?
```

This increases accuracy because the model breaks the problem into smaller reasoning chunks.

**Fact:** Google researchers showed that CoT improves performance in multi-step reasoning tasks by up to **40%**.

## 4. ReAct Prompting (Reason + Act)

Sometimes you want the LLM to reason **and** act. This hybrid approach lets the model *explain what it’s thinking, then execute an action*.

**Example (pseudo-agent):**

```
Question: "What’s the weather in London today?"    
  
Reasoning: I need to call a weather API with today’s date and location.    
Action: fetch_weather("London", "2025-08-26")
```

This is the foundation of LLM-based agents (like LangChain tools). Even if you’re not building agents, structuring prompts this way makes outputs predictable.

## 5. Self-Consistency

LLMs sometimes hallucinate. A trick to reduce this: ask the same question multiple times with slight variations, then **aggregate results**.

**Example:**

Instead of:

*“Summarize this research paper.”*

Try:

*“Generate 3 different summaries of this paper. Then synthesize them into one final summary.”*

Surprisingly, this reduces factual errors because the model “cross-checks” itself.

## 6. Instruction Hierarchies

Stack instructions in **layers of importance**. Models tend to obey top-level instructions first.

**Example:**

```
Main Task: Summarize this financial report.    
  
Constraints:    
1. Limit summary to 200 words.    
2. Use bullet points.    
3. Highlight risks and opportunities separately.    
  
Context: [Insert report text]
```

Think of it as a **prompt architecture**. This structure minimizes the risk of the model ignoring constraints.

## 7. Delimiters & Explicit Formatting

Ambiguity kills prompts. Use clear delimiters like triple quotes, XML tags, or JSON.

**Example:**

```
Summarize the following text between triple backticks in 3 bullet points.
```

For structured outputs:

```
Return the answer in JSON with the following keys:    
{ "summary": string, "keywords": list, "tone": string }
```

This makes post-processing automated and reliable.

## 8. Prompt Chaining

Break complex tasks into smaller steps and chain prompts.

**Example:** Research summarization

1. Prompt 1 → Extract key findings.
2. Prompt 2 → Summarize methods.
3. Prompt 3 → Generate final executive summary.

This modular approach is easier to debug and more scalable.

## 9. Negative Prompting

Tell the model what *not* to do.

**Example:**

```
Explain random forests in simple terms.    
Do not use mathematical formulas.    
Do not exceed 3 paragraphs.
```

This reduces irrelevant tangents.

## 10. Prompt Optimization with Automation

Manual prompting is fine for one-off queries. But for workflows, you need automation.

* Use **Python scripts** to generate variations of prompts.
* Use **logging** to track model responses.
* Run **A/B tests** on prompts to measure which yields higher accuracy.

**Example (Python snippet):**

```
prompts = [  
    "Summarize this text in 3 bullets:",  
    "Provide a concise summary in 3 key points:",  
    "Give me 3 takeaways from this document:"  
]  
  
for p in prompts:  
    response = llm_api(prompt=p + text)  
    log(p, response)
```

This way, you engineer prompts like you’d tune hyperparameters.

## Common Mistakes in Prompt Engineering

Let’s also cover what **not** to do:

1. **Overloading prompts** → If you ask for 10 things in one go, the model will likely miss half.
2. **Underspecification** → “Summarize this” without length, style, or focus = vague output.
3. **Ignoring iteration** → The first prompt is rarely the best. Iterate like you would with code.
4. **Trusting outputs blindly** → Always verify factual correctness, especially in critical domains.

## Practical Applications for Data Science Workflows

Since this is **DATA SCIENCE COLLECTIVE**, let’s anchor techniques to real use cases:

* **SQL generation:** Few-shot prompting with table schema examples.
* **Data cleaning:** Role prompting as a “data wrangler” with step-by-step reasoning.
* **EDA (Exploratory Data Analysis):** Chain-of-thought to generate hypotheses, then automate visualization code.
* **Documentation:** Delimited prompts to auto-generate function docstrings.
* **Report writing:** Prompt chaining for structured executive summaries.

These aren’t futuristic use cases — they’re daily productivity boosts.

## The Future of Prompt Engineering

Will prompt engineering become obsolete as models improve?

Not exactly. Think of it like **UI design for AI**. Models will get smarter, but humans will always need to:

* Define **intent** clearly.
* Translate messy goals into **structured inputs**.
* Optimize for **efficiency, consistency, and automation**.

What may change is tooling: IDEs with built-in prompt testing, monitoring dashboards, and shared prompt libraries. But the core skill — communicating effectively with LLMs — will remain.

## :::To Sum Up:::

Prompt engineering is part art, part science.

The *art* is in framing problems clearly, creatively, and empathetically.  
 The *science* is in structuring, testing, and optimizing prompts like any other system.

To recap, here are the most practical techniques:

* Role prompting
* Few-shot learning
* Chain-of-thought
* ReAct reasoning
* Self-consistency
* Instruction hierarchies
* Delimiters & formatting
* Prompt chaining
* Negative prompting
* Automated optimization

Mastering these will make you not just a better prompt writer, but a more effective data scientist, developer, or AI practitioner.

So the next time you open your LLM interface, remember: it’s not about *talking to a chatbot*. It’s about **engineering a conversation**.

And if you treat it like engineering, you’ll get results that feel like magic.
