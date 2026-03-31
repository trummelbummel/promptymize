# Best Prompt Techniques for Best LLM Responses

[![Jules S. Damji](https://miro.medium.com/v2/resize:fill:64:64/0*hIS9LgEB75e1xfzz.jpeg)](/@2twitme?source=post_page---byline--24d2ff4f6bca---------------------------------------)

[Jules S. Damji](/@2twitme?source=post_page---byline--24d2ff4f6bca---------------------------------------)

7 min readFeb 12, 2024

--

9

Listen

Share

> *Better prompts is all you need for better responses*

Press enter or click to view image in full size

![]()

## Introduction

The notion of a prompt is not new. This idea of offering a prompt permeates many disciplines: arts (to spur a writer or to speak spontaneously); science (to commence an experiment); criminal investigation (to offer or follow initial clues); computer programming (to take an initial step, given a specific context). All these are deliberative prompts as requests to elicit a desired respective response.

Interacting with [large language models](https://en.wikipedia.org/wiki/Large_language_model) (LLMs) is no different. You engineer the best prompt to generate the best response. To get an LLM to generate a desired response has borne a novel discipline: [prompt engineering](https://en.wikipedia.org/wiki/Prompt_engineering)–as “the process [and practice] of structuring text that can be interpreted and understood by a [generative AI](https://en.wikipedia.org/wiki/Generative_AI) model.” [1]

In this article, we explore what is prompt engineering, what constitutes best techniques to engineer a well-structured prompt, and what prompt types steer an LLM to generate the desired response; contrastingly, what prompt types deter an LLM to generate a desired response.

## What’s Prompt Engineering?

Prompt engineering is not strictly an engineering discipline or precise science, supported by mathematical and scientific foundations; rather it’s a practice with a set of guidelines to craft precise, concise, creative wording of text to instruct an LLM to carry out a task. Another way to put it is that “prompt engineering is the art of communicating with a generative large language model.” [2]

To communicate with LLM with precise and task-specific instructions prompts, Bsharat et.al [3] present a comprehensive principled instructions and guidelines to improve the quality of prompts for LLMs. The study suggests that because LLMs exhibit an impressive ability and quality in understanding natural language and in carrying out tasks in various domains such as answering questions, mathematical reasoning, code generation, translation and summarization of tasks, etc., a principled approach to curate various prompt types and techniques immensely improves a generated response.

Take this simple example of a prompt before and after applying one of the principles of conciseness and precision in the prompt. The difference in the response suggests both readability and simplicity–and the desired target audience for the response.

Press enter or click to view image in full size

![]()

**Figure 1:** An Illustration showing a general prompt on the left and a precise and specific prompte on the right.[4]

As you might infer from the above example that the more concise and precise your prompt, the better LLM comprehends the task at hand, and, hence, the better response it formulates.

Let’s examine some of the principles, techniques and types of prompt that offer better insight in how to carry out a task in various domains of natural language processing.

## Prompt Principles and Guides

[Bsharat et.al](https://arxiv.org/pdf/2312.16171.pdf) tabulate 26 ordered prompt principles, which can further be categorized into five distinct categories, as shown in Figure 2:

1. **Prompt Structure and Clarity:** Integrate the intended audience in the prompt.
2. **Specificity and Information**: Implement example-driven prompting (Use few-shot prompting)
3. **User Interaction and Engagement**: Allow the model to ask precise details and requirements until it has enough information to provide the needed response
4. **Content and Language Style**: Instruct the tone and style of response
5. **Complex Tasks and Coding Prompts:** Break down complex tasks into a sequence of simpler steps as prompts.

Press enter or click to view image in full size

![]()

**Figure 2.** : Prompt principle categories.

Equally, Elvis Saravia’s [prompt engineering guide](https://www.promptingguide.ai/introduction/elements) states that a prompt can contain many elements:

**Instruction**: describe a specific task you want a model to perform

**Context**: additional information or context that can guide’s a model’s response

**Input Data**: expressed as input or question for a model to respond to

**Output and Style Format**: the type or format of the output, for example, JSON, how many lines or paragraphs. Prompts are associated with roles, and roles inform an LLM who is interacting with it and what the interactive behavior ought to be. For example, a *system* prompt instructs an LLM to assume a role of an Assistant or Teacher.

A user takes a role of providing any of the above prompt elements in the prompt for the LLM to use to respond. Saravia, like the [Bsharat et.al](https://arxiv.org/pdf/2312.16171.pdf)’s study, echoes that prompt engineering is an art of precise communication. That is, to obtain the best response, your prompt must be designed and crafted to be [precise, simple, and specific](https://www.promptingguide.ai/introduction/tips). The more succinct and precise the better the response.

Also, [OpenAI’s guide on prompt engineering](https://platform.openai.com/docs/guides/prompt-engineering) imparts similar authoritative advice, with similar takeaways and demonstrable examples:

* Write clear instructions
* Provide reference text
* Split complex tasks into simpler subtasks
* Give the model time to “think”

Finally, Sahoo, Singh and Saha, et.al [5] offer a systematic survey of prompt engineering techniques, and offer a concise “overview of the evolution of prompting techniques, spanning from zero-shot prompting to the latest advancements.” They breakdown into distinct categories as shows in the figure below.

Press enter or click to view image in full size

![]()

Figure 3. Taxonomy of prompt engineering techniques

## CO-STAR Prompt Framework

But the CO-STAR prompt framework [6] goes a step further. It simplifies and crystalizes all these aforementioned guidelines and principles as a practical approach.

In her prompt [engineering blog](https://towardsdatascience.com/how-i-won-singapores-gpt-4-prompt-engineering-competition-34c195a93d41) that won Singapore’s GPT-4 prompt engineering competition, Sheila Teo offers a practical strategy and worthy insights into how to obtain the best results from LLM by using the CO-STAR framework.

In short, Ms. Teo condenses and crystallizes [Bsharat et.al](https://arxiv.org/pdf/2312.16171.pdf) (see Figure. 2) principles, along with other above principles, into six simple and digestible terms, as CO-STAR (Figure 4):

**C: Context:** Provide background and information on the task

**O: Objective**: Define the task that you want the LLM to perform

**S: Style:** Specify the writing style you want the LLM to use

**T: Tone:** Set the attitude and tone of the response

**A: Audience:** Identify who the response is for

**R: Response:** Provide the response format and style

Press enter or click to view image in full size

![]()

**Figure 4**: The CO-STAR’s distinct and succinct five principles of a prompt guide

Here is a simple example of a CO-STAR prompt in a demonstrative notebook:

Press enter or click to view image in full size

![]()

**Figure 4 (a):** An example prompt with CO-STAR framework

With this CO-STAR prompt, we get the following concise response from our LLM.

Press enter or click to view image in full size

![]()

**Figure 4(b):** An example response with CO-STAR framework

You can view extensive examples in these two Colab notebooks:

1. [Basic Tasks](https://colab.research.google.com/github/dmatrix/genai-cookbook/blob/main/llm-prompts/1_how_to_use_basic_prompt.ipynb)
2. [NLP Tasks](https://colab.research.google.com/github/dmatrix/genai-cookbook/blob/main/llm-prompts/2_how_to_conduct_common_nlp_llm_tasks.ipynb)

Besides CO-STAR, other frameworks specific to ChatGPT have emerged, yet the core of crafting effective prompts remains remains the same: clarity, specificity, context, objective, task, action etc. [7]

## Prompt Types and Tasks

So far we have explored best practices, guiding principles, and techniques, from an array of sources, on how to craft a concise prompt to interact with an LLM — all to generate the desired and accurate response. Prompts are linked to type of tasks, meaning the kind of task you wish the LLM perform equates to a type of prompt–and how you will craft it.

Saravia [8] analyzes various task-related prompts and advises on crafting effective prompts to accomplish these tasks. Generally, these tasks include:

* Text summarization
* Zero and few shot learning
* Information extractions
* Question answering
* Text and image classification
* Conversation
* Reasoning
* Code generation

I won’t elaborate on the explanation for brevity. But do explore prompt types through illustrative examples in the Colab notebooks below for insights on crafting effective prompts and obtaining accurate responses.

Press enter or click to view image in full size

![]()

**Figure 5.** [Example notebooks](https://github.com/dmatrix/genai-cookbook/blob/main/llm-prompts/README.md) that explore type of prompts associated with type of tasks.

**Note:** All notebook examples have been tested using [OpenAI APIs](https://openai.com/blog/openai-api) on GPT-4-turbo, Llama 2 series models, Mixtral series, Code Llama 70B (running on [Anyscale Endpoints](https://www.anyscale.com/endpoints)). To execute these examples, you must have accounts on [OpenAI](https://openai.com/) and [Ansyscale Endpoints](https://www.anyscale.com/endpoints). These examples are derived from a subset of [GenAI Cookbook GitHub Repository.](https://github.com/dmatrix/genai-cookbook/blob/main/README.md)

## Summary

In this article, we covered what is prompt engineering, provided an array of authoritative guiding principles and techniques to curate and craft effective prompts to obtain the best response from LLMs. At the same time, the OpenAI guide also advised what prompts not to use.

Incorporating above principles, we discussed the CO-STAR prompt framework and provided a couple of examples on how to use this prompting framework.

Finally, we linked prompt types to common tasks for LLMs and offered a set of illustrative notebook examples for each type of task.

All the above serve a helpful first step into your journey into crafting and curating effective prompts for LLMs and obtaining the best response.

## What’s Next?

Read the next sequence of blogs on GenAI Cookbook series on LLMs:

* [LLM Beyond its Core Capabilities as AI Assistants or Agents](/@2twitme/llm-beyond-its-core-capabilities-as-ai-assistants-or-agents-704ffb972934)
* [Crafting Intelligent User Experiences: A Deep Dive into OpenAI Assistants API](/@2twitme/crafting-intelligent-user-experiences-a-deep-dive-into-openai-assistants-api-00439ace108a)

## Resources & References

[1] <https://en.wikipedia.org/wiki/Prompt_engineering>

[2] [ChatGPT, 2023](https://chat.openai.com/)

[3] <https://arxiv.org/pdf/2312.16171.pdf>

[4] <https://arxiv.org/pdf/2312.16171.pdf>

[5] <https://arxiv.org/pdf/2402.07927.pdf>

[6] <https://towardsdatascience.com/how-i-won-singapores-gpt-4-prompt-engineering-competition-34c195a93d41>

[7] <https://www.linkedin.com/pulse/9-frameworks-master-chatgpt-prompt-engineering-edi-hezri-hairi/>

[8] <https://www.promptingguide.ai/introduction/examples>

[9] <https://platform.openai.com/docs/guides/prompt-engineering>

[10] <https://platform.openai.com/examples>

[11] [https://github.com/dmatrix/genai-cookbook/blob/main/README.m](https://github.com/dmatrix/genai-cookbook/blob/main/README.md)
