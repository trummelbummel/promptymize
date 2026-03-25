## Unlock the full potential of AI by learning how to craft powerful prompts that get smarter, more accurate results.

# Prompt Engineering explained — From basic to advanced techniques

## MAKE IT SIMPLE AI SERIES — CRAFTING EFFECTIVE PROMPTS: KEY ELEMENTS AND BEST PRACTICES— PART1

[![RK Iyer](https://miro.medium.com/v2/resize:fill:64:64/1*cGLRW79OKrWZPAxLhATyyA.jpeg)](/?source=post_page---byline--2995198eebb6---------------------------------------)

[RK Iyer](/?source=post_page---byline--2995198eebb6---------------------------------------)

5 min readJun 1, 2025

--

1

Listen

Share

## ❑ Overview

Press enter or click to view image in full size

![]()

Prompt Engineering

Prompt engineering has rapidly emerged as one of the most exciting frontiers in artificial intelligence. At its core, it’s the craft of designing and refining instructions — called prompts — to guide generative AI models like ChatGPT, DALL-E, and others to produce exactly the results you desire. With well-crafted prompts, you can steer AI responses, inject domain knowledge, and even ensure safer, more reliable outputs.

As AI continues to reshape industries, prompt engineering is becoming an essential skill for developers, researchers, and business professionals. In this blog series, I’ll take you on a journey from the basics of prompt design to advanced techniques — empowering you to harness the true potential of generative AI, no matter your starting point.

## ❑ Real World Example

Press enter or click to view image in full size

![]()

Coffee Shop

**But imagine** if the **barista misunderstood** your answers or guessed what you wanted without asking — **maybe handing you an iced caramel macchiato with extra syrup**, even though you **never mentioned caramel or cold drinks**. This would be confusing and not what you wanted.

### Analogy to Prompt Engineering and Hallucination:

If your instructions are vague or the LLM “guesses” details not provided (hallucination), you might get a response that sounds confident but is incorrect or unrelated — just like getting the wrong coffee order. That’s why asking clear, specific questions and verifying the answers is crucial when working with LLMs, to avoid “hallucinated” outputs.

> Prompt engineering with LLMs is like giving clear instructions to the barista so you get the coffee you want.

### ❑ What is a Prompt?

*A prompt is a* ***piece of natural language text*** *— like a question, instruction, or statement — that you give to a* ***large language model (LLM)*** *to* ***guide it in generating a response****.*

For text-to-text language models, a prompt can be a **question**, **a command, or a longer statement that includes context or instructions.**

```
Translate this sentence to French: The weather is nice today.
```

**For** **text-to-image or text-to-audio** models, prompts are typically **descriptions of the desired output. e.g.**

```
Create a landscape image of rolling green hills under a bright blue sky.
```

```
Generate the sound of gentle rain falling on leaves in a quiet forest.
```

Prompts can include **four parts**: the goal, context, expectations, and source, as described in the following image:

### ❑ What is a Prompt Engineering?

[Prompt engineering](https://en.wikipedia.org/wiki/Prompt_engineering) is the **process of structuring** or **crafting an instruction** in order **to produce the best possible output** from a **generative artificial intelligence. Source Wikipedia**.

**According to Google Cloud**, prompt engineering is “The art and science of designing and optimizing prompts to guide AI models, particularly LLMs, towards generating the desired responses”.

### Parts of a Prompt

* **Instruction**: Tells the AI exactly what you want it to do.
* **Context**: Gives extra background or details to help the AI give a better answer.
* **Input Data**: The main question or information you want help with.
* **Output Indicator**: Explains what kind of answer or format you expect from the AI.

These **parts work together** to help you get the best results from your prompts.

### ❑ Prompt Engineering Best Practices

Below are some of the best practices for writing a prompt —

1. **Be Clear and Specific**: Ensure that your prompt clearly states what you want the model to do. Avoid vague or ambiguous language.

### Vague Prompt:

```
Write about technology.
```

***Why it’s unclear:*** It doesn’t specify what **aspect of technology**, **the style**, **length**, or **purpose**.

### Clear and Specific Prompt:

```
Write a 200-word article explaining how artificial intelligence is transforming healthcare, focusing on patient diagnosis improvements.
```

**Why it’s clear:** It specifies the **topic (AI in healthcare)**, the **focus (patient diagnosis)**, and the **length (200 words)**.

2. **Provide Context**: Give the model enough background information to understand the task. This can include relevant details, examples, or constraints.

### Without Context:

```
Summarize this article.
```

***Why it’s lacking****:* The model doesn’t know what the article is about or what kind of summary is needed.

### With Context:

```
Summarize the following article about climate change, focusing on the main causes and effects discussed. The article is intended for high school students.
```

***Why it’s better:*** It gives background (topic: climate change), specifies what to focus on (causes and effects), and mentions the audience (high school students), helping the model generate a more relevant summary.

**3. Use Structured Inputs**: When possible, structure your prompt in a way that makes it easy for the model to follow. This can include using bullet points, numbered lists, or specific formatting.

**4. Iterate and Refine**: Prompt engineering is an iterative process. Experiment with different prompts, analyze the results, and refine your prompts based on the model’s performance.

**5. Test for Bias and Fairness**: Ensure that your prompts do not introduce or reinforce biases. Test your prompts with diverse inputs to check for fairness and inclusivity.

### Prompt Example:

```
Describe a typical software engineer.
```

This prompt **might lead the AI** to **generate stereotypical or biased descriptions (e.g., assuming a certain gender, age, or background).**

**How to Test for Bias and Fairness:**  
Try running the prompt with variations or explicitly ask:

```
Describe a typical software engineer. Make sure your answer is inclusive of all genders, backgrounds, and cultures.
```

**What to Look For:**Check if the AI’s responses avoid stereotypes and represent diversity, ensuring the prompt and output are fair and inclusive.

**6. Use Examples**: Providing examples of the desired output can help guide the model towards producing similar results.

**7. Review and Adjust**: After receiving the model’s response, review it to see if it meets your needs. If not, adjust your prompt and try again.

## ❑ Reference

[Prompt Engineering for AI Guide | Google Cloud](https://cloud.google.com/discover/what-is-prompt-engineering?hl=en#what-is-prompt-engineering)

[Prompt Engineering Guide | Prompt Engineering Guide](https://www.promptingguide.ai/)

## ❑ Conclusion

I hope this blog helped you to go through the basic of Prompt engineering. We will surely explore and continue with advance topics of prompt engineering in upcoming blogs, Till then, Happy Learning!!!

*Please Note — All opinions expressed here are my personal views and not of my employer.*
