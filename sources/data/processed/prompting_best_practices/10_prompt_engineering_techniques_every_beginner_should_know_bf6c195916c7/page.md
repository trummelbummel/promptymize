# 10 Prompt Engineering Techniques Every Beginner Should Know

## Master the art of communicating with AI and unlock its full potential

[![Allan Alfonso](https://miro.medium.com/v2/resize:fill:64:64/1*rAcN0_DMSu5v8PC8XG9NVA.jpeg)](/@allanalfonso?source=post_page---byline--bf6c195916c7---------------------------------------)

[Allan Alfonso](/@allanalfonso?source=post_page---byline--bf6c195916c7---------------------------------------)

4 min readJan 21, 2025

--

Listen

Share

Press enter or click to view image in full size

![]()

Prompts are how we interact with Large Language Models (LLMs).

Kaggle and Google published a great Whitepaper on Prompt Engineering to help people understand the basics of prompting. Bad prompts can lead to ambiguous, inaccurate responses and hinder the model’s ability to provide meaningful output. Becoming a better prompt engineer will help you get the most out of Large Language Models.

Below are 10 Key Takeaways from the whitepaper.

### 1. Zero Shot Prompting

Zero Shot Prompting means you provide no examples in your prompt.

A single sentence chat message is a common zero shot prompt. The LLM has to guess an appropriate response based on limited information. The success of a zero shot prompt will depend on the model’s pre-training and the clarity of the prompt.

A zero shot prompt is the simplest type of prompt.

### 2. Few Shot Prompting

Few Shot Prompting means you provide one or more examples in your prompt.

Examples help the LLM understand what you are asking for and can steer the LLM to a certain output structure or pattern. As a general rule of thumb, provide at least 3–5 relevant examples. The number of examples will vary depending on your task.

Examples should be diverse and well written.

### 3. System Prompting

System Prompting sets the context and purpose for the LLM.

It defines the “big picture” of what the LLM should do and provides task-specific information to guide the LLM. For example, you can use a system prompt to instruct the LLM to generate JSON output. Systems Prompts are also useful for enforcing safety and toxicity because you can add a system prompt such as “You should be respectful in your answer” that instructs the LLM to produce a clean answer.

System Prompting defines the LLM’s fundamental capabilities and overarching purpose.

### 4. Role Prompting

Role Prompting assigns a character or identity for the LLM to adopt.

This helps the LLM generate responses that are consistent with the assigned role. You can assign many different types of roles such as grade school teacher, New York Times Editor, luxury travel guide, etc. Defining a role gives the LLM a blueprint for the tone, style, and expertise you are looking for in your response.

Roles add a layer of specificity and personality.

### 5. Contextual Prompting

Contextual Prompting provides extra details and background information relevant to your task.

By providing contextual prompts, the LLM can generate more accurate and relevant responses. Types of context could include examples, instructions, and background information.

Contextual Prompting is all about giving the LLM the information it needs to its best work.

### 6. Step-Back Prompting

Step-Back Prompting is a two step prompting technique.

First, you prompt the LLM to consider a general question about the task. Second, you feed that response back to the LLM as a separate prompt to get the final response. This technique allows the LLM to activate background knowledge and reasoning processes before attempting to solve the problem.

Step-Back Prompting helps generate a more accurate and insightful response.

### 7. Chain of Thought

Chain of Though (CoT) Prompting improves the reasoning capabilities of LLMs by generating intermediate reasoning steps.

With CoT Prompting, you can see how the LLM thinks. Add “Let’s think step by step” to your prompt and you should see the LLM explaining each step of its thought process instead of just returning an answer. Generally, any task that can be solved by “talking through the problem” is a good candidate for CoT Prompting.

CoT Prompting is also useful for testing different LLMs since responses appear to be more similar when they have to show their reasoning.

### 8. Self Consistency

Self-Consistency Prompting combines sampling and majority voting to generate diverse reasoning paths and selects the most consistent answer.

It’s kinda like the Monte Carlo simulation of prompting. You provide the LLM the same prompt over and over with a high temperature setting to generate different reasoning paths and responses (generate the samples). Then you choose the most common answer out of all the responses (majority voting).

Self-Consistency Prompting can get a more consistent accurate answer from the LLM by selecting the most popular response.

### 9. Tree of Thoughts

Tree of Thoughts (ToT) Prompting allows the LLM to explore multiple reasoning paths.

ToT is a generalization of CoT. Rather than just follow a single linear CoT, ToT follows multiple paths. A tree of thoughts is created and the LLM can explore different paths by traversing different branches of the tree.

ToT is well-suited for complex tasks that require exploration of multiple reasoning paths.

### 10. ReAct

Reason and Act (ReAct) Prompting is a paradigm for enabling LLMs to solve complex tasks using natural language combined with external tools.

ReAct works by first by using the LLM to think about the problem and generate an action plan. Then the LLM executes the action plan and observes the results. The LLM continues the process of generating an action plan and observing the results until it find a solution to the problem.

ReAct tries to mimic how humans operate where we think, take action, observe the results, and repeat until we are satisfied with the result.

## Resources

* <https://www.kaggle.com/whitepaper-prompt-engineering>
