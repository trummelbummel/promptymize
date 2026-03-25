# Top 5 Prompt Engineering Techniques for LLMs in 2025

[![Neha Ummareddy](https://miro.medium.com/v2/resize:fill:64:64/1*GbyqMbILHHkKofGabAtVnA.jpeg)](/@nehaummareddy?source=post_page---byline--f114d4958b4d---------------------------------------)

[Neha Ummareddy](/@nehaummareddy?source=post_page---byline--f114d4958b4d---------------------------------------)

5 min readOct 15, 2025

--

Listen

Share

As LLMs continue to get better, the debate — Is prompt engineering dead or becoming even more important is totally on. With today’s models, the extent to which prompting is needed is drastically reducing, but no matter how smart LLMs become, they still need directions on various ‘whats’, ‘hows’, 'whys’, and 'whens.' The guidelines become important to get the outputs you are looking for. We all have experiences with LLMs where the results are outright unacceptable. **Here are 5 prompt engineering techniques that have always worked and are very much relevant with the newest models, be it GPT, Gemini or Claude —**

### 1. Few Shots

Few-shot is a prompting technique where you include examples as part of your prompt. This provides LLM guidelines on how to approach a task and the format in which we expect the output. Few-shot prompting is 80% more efficient than zero-shot prompts (without any examples).

***Sample Template***

*<Task> Use examples below as ref :  
<Example1>  
<Example2>*

Press enter or click to view image in full size

![]()

How many examples are the right number of examples? — The goal with few-shot prompts is to cover enough so that LLM can respond to a similar new task. Trying out and experimenting is the best approach here. Starting with 2 or 3 examples is a good idea, and depending on the complexity and different use cases that have to be covered, more can be included. More complex tasks, which need to cover a lot of cases, can use techniques like dynamic few-shot. For dynamic few-shot inclusion, refer to —

[## Dynamic few-shot prompting | Technology Radar | Thoughtworks United States

### Dynamic few-shot prompting builds upon few-shot prompting by dynamically including specific examples in the prompt to…

www.thoughtworks.com](https://www.thoughtworks.com/en-us/radar/techniques/dynamic-few-shot-prompting?source=post_page-----f114d4958b4d---------------------------------------)

With dynamic few-shots, we provide LLM just the relevant examples instead of overloading it with a lot of examples and leaving LLM to figure out which one to use as a reference. Dynamic few-shot approach is great of complex tasks, resulting in better outputs at the same time, reducing cost and latency.

### 2. Persona / Role-Based Prompting

In Persona or Role-based prompting, you direct the LLM to act as an expert or assume the role of a domain expert, for example, a potential client or an employer and then respond to the task. This allows LLMs to wear a specific hat and focus on the task.

***Sample Template*** *You are an expert in <>. <Task>*

Press enter or click to view image in full size

![]()

Without the persona, based LLMs are free to attempt the task from multiple directions, of which not all might be relevant to you. Defining the persona pushes the LLM to attempt the task with a more focused and relevant lens and, hence, gets better outputs.

### 3. Chain of Thought

With Chain of Thought (COT) prompting, you prompt LLMs to do step-by-step thinking while generating the output of a task. This technique is very efficient for logic-based tasks, which is usually a weak area for LLMs. COT allows LLMs to break down a problem into smaller problems before solving them. Explicitly prompting LLMs to think through each step allows LLMs to engage in logical thinking at each step, making the final output literally “Add up”. COT is great for tasks which need reasoning and logic, like SQL generation or maths problems or tasks which might need multiple steps to arrive at the correct output. The most common way of making your prompt COT-driven is by prompting the LLM to explain each step or walk through each step.

***Sample Template***  *1. <Task prompt >. Explain your answer step by step.  
2. <Task prompt >. Think through the output step by step.*

Press enter or click to view image in full size

![]()

While COT is great for complex/reasoning tasks, including COT can also give a deeper insight into LLM's thought process while arriving at the output. Experiment with mathematical problems to see how LLMs tend to give wrong answers without COT.   
COT can be used with Few-Shot prompting — Few-Shot COT. Few-shot COTs are usually more consistent with outputs.

### 4. ReAct — Reasoning and Acting

ReAct prompting combines reasoning and action. ReAct allows LLMs to reason and then take an action based on the reasoning. ReAct prompting technique becomes extremely important when a task needs a series of tools or functions to be invoked. While LLMs have natively become enabled with tool/function calling, making ReAct part of your prompt has many advantages. The reasoning and actions are explicit with ReAct. Making these steps explicit can make debugging easier. ReAct with COT is a powerful combination that allows reasoning at each sub-problem level.

***Sample Template***

*Task   
Follow this exact loop:  
Thought: <brief reasoning about next step>  
Action: <ToolName>[Arguments]  
Observation: <result returned by the operator>*

*Tools available   
<tools>*

Multiple iterations of thought-action-observation can be enforced till a task is completed. I have not included an example screenshot, as the comparison here needs to trigger the LLM function calling. I will be attaching a sample code link here soon.

### 5. Tree of Thoughts (TOT)

Tree of Thoughts, or TOT, is a supercharged COT. While COT follows a single chain of reasoning, TOT branches out and weighs multiple possible options before arriving at the output. TOT is extremely useful for tasks which need to consider multiple variations.

***Sample Template*** *<Task>  
Consider multiple options to approach the task  
Option 1: <Option>  
Option 2: <Option>  
Evaluate the options and decide on the best one.  
<Result>*

Press enter or click to view image in full size

![]()

TOT is ideal for examining multiple scenarios, weighing pros and cons and picking output which is apt for the given task. TOT combined with Persona/Role-based prompting can also be used to approach a task from multiple personas to get a holistic picture before arriving at the output.

### Summary Snapshot

Below is the snapshot of the 5 prompting techniques, along with when to use them and which techniques together yield even better results. Always keep the prompt clear and concise. Provide enough context in the prompt for LLMs to respond better. And always **Verify— Fix — Repeat.**

Press enter or click to view image in full size

![]()

* Gemini has been used for all generations
* Generated output has been truncated because of its length. You can try out the prompt.
