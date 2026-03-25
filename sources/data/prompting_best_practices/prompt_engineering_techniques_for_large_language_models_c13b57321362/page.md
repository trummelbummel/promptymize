# Prompt Engineering Techniques for Large Language Models

[![Pan Xinghan](https://miro.medium.com/v2/da:true/resize:fill:64:64/0*BaoqPRJef2BdT4Ka)](/@sampan090611?source=post_page---byline--c13b57321362---------------------------------------)

[Pan Xinghan](/@sampan090611?source=post_page---byline--c13b57321362---------------------------------------)

5 min readJan 15, 2025

--

Listen

Share

The development and application of Large Language Models (LLMs) such as OpenAI’s GPT-3.5 and GPT-4 have redefined the boundaries of natural language understanding and generation. Central to maximizing the utility of these models is **prompt engineering**, the process of crafting inputs to optimize the model’s output for a given task. This article delves into the nuances of prompt engineering, exploring techniques and strategies supported by benchmarking results from models like GPT-3.5-Turbo and GPT-4–1106 across tasks. Moreover, we include detailed guidance on how to apply each strategy effectively.

## Understanding the Need for Prompt Engineering

LLMs are trained on extensive datasets to generate responses based on textual inputs. However, their performance can vary significantly depending on how queries are framed. Prompt engineering bridges the gap between the model’s capabilities and the user’s expectations by:

* Enhancing the accuracy and relevance of responses.
* Reducing ambiguity in task instructions.
* Improving performance across diverse domains and benchmarks.

While baseline performance showcases the raw capability of models, thoughtfully designed prompts can unlock higher potential.

## Key Prompt Engineering Techniques and How to Use Them

### 1. Chain-of-Thought (CoT) Prompting

CoT prompting guides the model to break down tasks step-by-step. By encouraging reasoning through intermediate steps, CoT enhances performance in tasks requiring logical deduction or calculations. For example, in the **gsm8k benchmark** (math problem-solving), GPT-3.5-Turbo achieved a baseline accuracy of 47.15%, while CoT improved performance to 40.33% and even higher for GPT-4–1106.

How to Use CoT Prompting:

**Zero-Shot CoT:** Include instructions like “Think step-by-step” in your prompt without providing specific examples. This approach encourages the model to reason through tasks autonomously. For example:

* **Prompt:** “Solve the following problem step by step: If a train travels 60 miles in 1 hour, how long will it take to travel 180 miles?”

**Few-Shot CoT:** Provide a few examples of step-by-step reasoning before asking the model to solve the target problem. For instance:

* **Prompt:** “Example 1: To find the area of a rectangle, multiply length by width. Example 2: If an object travels 50 km in 2 hours, its speed is distance divided by time. Now, solve: What is the speed of a car that travels 100 km in 4 hours?”

### 2. Expert Prompting

Expert prompting leverages domain-specific knowledge. By crafting inputs that mimic subject-matter expertise, models deliver more nuanced and accurate outputs. On tasks such as **bigbench\_object\_tracking**, GPT-3.5-Turbo showed substantial gains with expert prompting, achieving 56.53% compared to 39.2% baseline accuracy.

How to Use Expert Prompting:

Use precise, technical vocabulary relevant to the task. For instance:

* **Prompt:** “In the context of quantum mechanics, explain the concept of wave-particle duality and its implications for the double-slit experiment.”

Frame queries in a structured format, such as:

* “Step 1: Define the problem. Step 2: Provide examples. Step 3: Discuss implications.”
* Ensure clarity and specificity to reduce ambiguity. Example:
* **Prompt:** “Provide a summary of the factors affecting climate change, focusing on greenhouse gas emissions and deforestation.”

### 3. Emotion-Based Prompting

Emotion-based prompting incorporates human-like emotional understanding into tasks. For instance, in sentiment analysis and conversational AI, adding emotional cues can enhance context-sensitive responses. In the **csqa benchmark**, the emotion-prompted approach for GPT-4–1106 scored 90.83%, outperforming both baseline and CoT methods.

How to Use Emotion-Based Prompting:

Include emotional context in the prompt. For example:

* **Prompt:** “Respond empathetically: A customer is frustrated because their order was delayed.”

Emphasize tone and sentiment in task instructions:

* **Prompt:** “Write a cheerful email to a customer informing them about a new product launch.”

Use cues to guide conversational tone:

* **Prompt:** “Act as a supportive friend and provide advice to someone feeling overwhelmed at work.”

### 4. Least-to-Most Prompting

This strategy incrementally increases task complexity, starting with simpler subtasks and gradually progressing. For example, in tasks like **last-letter-concat**, the least-to-most prompting approach helped GPT-3.5-Turbo achieve 79.8%, demonstrating how breaking down a task improves overall accuracy.

How to Use Least-to-Most Prompting:

Start with a simple version of the task and progressively add complexity. For example:

* **Prompt:** “Step 1: Identify the first letter of each word in the phrase ‘Artificial Intelligence’. Step 2: Concatenate these letters to form ‘AI’. Step 3: Apply the same process to ‘Machine Learning’.”

Structure prompts to build foundational knowledge before introducing advanced elements:

* **Prompt:** “Explain the concept of supply and demand. Then, analyze its application in the stock market.”

## Integrating Benchmark Results

Benchmarking data highlights the strengths and weaknesses of different prompting strategies. The table below summarizes the performance of GPT-3.5-Turbo and GPT-4–1106 across key benchmarks:

Press enter or click to view image in full size

![]()

benchmark

### Interpreting the Table

* **Baseline Performance:** Indicates the model’s ability to perform tasks without any specific prompting strategy.
* **Chain-of-Thought (CoT):** Illustrates the impact of breaking tasks into steps.
* **Zero-Shot CoT:** Highlights the model’s ability to reason without examples.
* **Expert Prompting:** Reflects the improvements using domain-specific inputs.
* **Emotion Prompt:** Evaluates the model’s performance in sentiment-driven tasks.
* **Least-to-Most Prompting:** Demonstrates performance gains through incremental complexity.

This benchmarking underscores the importance of selecting appropriate strategies based on the nature of the task to achieve optimal outcomes.

## Practical Applications of Prompt Engineering

### Academic Research

In fields like mathematics, history, and linguistics, prompt engineering allows researchers to extract precise insights and simulate hypothetical analyses. By employing CoT or expert prompting, models can handle complex problem-solving tasks with improved accuracy.

### Business Solutions

Companies leverage LLMs for tasks like:

* Automating customer service (emotion-based prompts).
* Generating detailed technical reports (expert prompting).
* Forecasting trends through data synthesis (least-to-most prompting).

### Creative Industries

For content creators, prompt engineering enhances the creative process by generating:

* Storylines and dialogue using emotional cues.
* Tailored marketing strategies with targeted language.

## Conclusion

Prompt engineering is a transformative tool for unlocking the full potential of LLMs like GPT-3.5 and GPT-4. By employing strategies such as CoT prompting, expert prompting, and emotion-based approaches, users can achieve remarkable improvements in model performance across diverse benchmarks. This article has highlighted not only the techniques but also practical ways to implement them effectively. However, as the field evolves, it remains crucial to balance performance with ethical considerations and computational efficiency. With continuous advancements, prompt engineering will continue to drive innovations in AI applications, shaping the future of human-computer interaction.

To dive deeper into the principles and practical examples of prompt engineering, consider visiting the following resources:

* [Prompting Guide](https://www.promptingguide.ai/zh)
* [OpenAI’s Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
