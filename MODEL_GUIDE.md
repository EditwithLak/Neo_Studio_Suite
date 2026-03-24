# MODEL GUIDE

This guide explains how to choose models for **Neo Studio Suite**, especially for **Neo Studio** where local GGUF backends are used for prompt generation and image captioning.

It is written to help you avoid the two classic mistakes:

- downloading the biggest model you can find and wondering why your PC is suffering
- downloading the wrong model type and wondering why captioning or prompting feels cursed

---

## 1. What Neo Studio Suite needs from models

Neo Studio Suite can use different local models depending on the job.

There are three practical model roles to understand:

## A. Prompting / text-generation models
These are used for:
- prompt generation
- prompt improvement
- prompt continuation
- rewriting
- cleanup
- creative expansion

These models are mostly text-first.

---

## B. Captioning / vision models
These are used for:
- full image captioning
- targeted captioning
- face-only captioning
- person / character captioning
- outfit / pose / location captioning
- batch captioning

These need to understand images, not just text.

---

## C. Multimodal all-rounders
These models can often handle both:
- text prompting
- image understanding

They are flexible, but not always the absolute best at both jobs compared with a more specialized split setup.

---

## 2. One-model workflow vs two-model workflow

There are two clean ways to use Neo Studio.

## Option 1 — One model for both jobs
Use one multimodal model for:
- captioning
- prompt generation

### Pros
- simpler setup
- fewer files to manage
- easier switching

### Cons
- may be slower
- may not be the strongest specialist for either task

---

## Option 2 — Separate models for each job
Use:
- one captioning/vision model
- one prompting/text model

### Pros
- better specialization
- more control over quality vs speed
- easier to optimize each workflow

### Cons
- more files
- more switching
- more setup management

---

## Recommendation

If you are just starting, use the workflow that is easiest for your hardware.

If your system is strong enough and you care about quality, a **split setup** is usually the cleaner long-term option:

- captioning model for Caption Studio
- prompting model for Prompt Studio

---

## 3. What is `mmproj` and when do you need it?

Some multimodal GGUF models need an additional file called **`mmproj`**.

That file is used for image understanding / projection support.

### You usually need `mmproj` when:
- the model is a vision-capable GGUF
- you want image captioning or image understanding
- the model page provides a separate `mmproj` file

### You usually do not need `mmproj` when:
- you are using a pure text GGUF model
- the model is only being used for prompt generation and text tasks

### Important rule
If your model is meant to read images and the repo includes a separate `mmproj`, treat that as part of the model package.
Do not load only the main GGUF and then wonder why image captioning is dead on arrival.

---

## 4. How to choose a model for captioning

A captioning model for Neo Studio should be able to do one or more of these well:

- describe images clearly
- follow instruction-style caption prompts
- handle targeted captioning
- remain grounded to visible details
- run at a usable speed on your machine

### Good qualities for captioning models
- reliable visual understanding
- decent instruction following
- not too vague
- not too hallucination-prone
- stable enough for batch work

### When caption quality feels weak
Common reasons:
- wrong model type
- missing `mmproj`
- quant is too aggressive
- prompt template is too weak
- backend is running but not actually in multimodal mode

---

## 5. How to choose a model for prompting

A prompting model for Neo Studio should be able to:

- write clearly
- follow formatting instructions
- produce prompt-ready text
- expand and refine prompts without drifting too far
- behave consistently during cleanup and rewrite tasks

### Good qualities for prompting models
- strong instruction following
- stable style control
- low repetition
- good medium-length output
- not overly verbose unless asked

### When prompting quality feels weak
Common reasons:
- model is too small
- quant is too low
- temperature/settings are bad
- the model is more chatty than structured
- the backend settings are fighting the model

---

## 6. Suggested model options

These are **practical suggestions**, not hard requirements.

Use what works for your hardware and workflow.

---

## Captioning / multimodal suggestions

### JoyCaption
Project:

`https://github.com/1038lab/ComfyUI-JoyCaption`

Why it is relevant:
- focused on caption generation
- supports GGUF workflows
- supports batch processing
- offers different caption styles and length controls

Best use in Neo Studio:
- caption generation
- targeted captioning
- batch captioning
- descriptive prompt-part extraction

Good fit if you want:
- stronger caption-oriented behavior
- a workflow already centered around image description

---

### ToriiGate v0.4 7B GGUF
Model page:

`https://huggingface.co/mradermacher/ToriiGate-v0.4-7B-GGUF`

Why it is relevant:
- multimodal GGUF option
- includes a separate `mmproj-fp16`
- offers multiple quant levels

Best use in Neo Studio:
- captioning
- image understanding
- one-model-for-both-jobs setups

Good fit if you want:
- a lighter multimodal model than the huge vision stacks
- a single model that can do both image and text tasks reasonably well

---

## Prompting / text suggestions

### Dolphin 3.0 R1 Mistral 24B GGUF
Model page:

`https://huggingface.co/bartowski/cognitivecomputations_Dolphin3.0-R1-Mistral-24B-GGUF`

Why it is relevant:
- strong text-generation candidate for prompt work
- multiple quant options
- a good middle ground for people who want better text quality and can handle the size

Best use in Neo Studio:
- prompt generation
- rewrite / improve workflows
- structured prompt drafting
- cleanup / continuation

Good fit if you want:
- a dedicated prompting model
- better text quality than smaller lightweight options

---

### Qwen3-VL 32B Instruct GGUF
Model page:

`https://huggingface.co/Qwen/Qwen3-VL-32B-Instruct-GGUF/tree/main`

Why it is relevant:
- multimodal-capable
- includes separate `mmproj` files
- can be used for both image and text tasks if your system can support it

Best use in Neo Studio:
- multimodal captioning
- prompt generation
- one-model high-capability setups

Good fit if you want:
- a stronger multimodal all-rounder
- one backend model doing more of the heavy lifting

---

## 7. Quantization basics without the nonsense

You do not need to memorize every quant format on earth.
You just need the practical version.

### In general
- **smaller quants** = lighter, faster, lower memory, more quality loss
- **middle quants** = best everyday balance
- **larger quants / F16** = heavier, slower, best quality, more demanding

### Practical rule of thumb
If you are unsure:
- start around the middle
- confirm the workflow works
- then move up or down based on speed and quality

---

## 8. Suggested starting strategy by hardware comfort

These are not strict hardware guarantees. They are **sanity suggestions**.

## Low comfort / limited VRAM
Use:
- smaller captioning model or lower quant
- smaller prompting model or lower quant
- simpler workflows first

Prioritize:
- stability
- getting the tool working
- smaller batch jobs

---

## Mid-range comfort
Use:
- medium quant captioning model
- medium quant prompting model
- or one mid-range multimodal model for both

This is often the best starting point for real use.

---

## High comfort / stronger machine
Use:
- stronger multimodal model for captioning
- stronger dedicated text model for prompting
- or a large all-rounder if that fits your preferences

Prioritize:
- quality
- detail retention
- larger prompt and caption tasks

---

## 9. Recommended setup patterns

## Pattern A — Simple caption-first setup
Use one multimodal model for everything.

Good for:
- fast setup
- fewer moving parts
- testing the whole system first

---

## Pattern B — Balanced split setup
Use:
- JoyCaption or ToriiGate for captioning
- Dolphin for prompting

Good for:
- users who want better prompt quality without overcomplicating things

---

## Pattern C — Strong multimodal setup
Use a larger multimodal model like Qwen3-VL if your machine can support it.

Good for:
- users who want one model handling both image and text work
- users who care more about capability than lightweight simplicity

---

## 10. Which tasks care most about model choice?

### Very model-sensitive
- face-only detailed captioning
- person / character attribute-rich captioning
- output metadata recovery cleanup
- prompt rewriting / cleanup
- high-quality prompt generation

### Less sensitive
- simple tags
- straightforward short prompt expansion
- basic save/search workflows

If the output quality matters a lot, model choice matters a lot.

---

## 11. Common failure patterns

## A. Captioning model loads, but images are ignored
Usually means:
- wrong model
- missing `mmproj`
- wrong multimodal setup in backend

## B. Captions are too vague
Usually means:
- model is weak for image understanding
- quant is too small
- prompt template is too soft

## C. Prompt model is too chatty
Usually means:
- model is not ideal for structured prompting
- settings need tightening
- you may want a more instruction-focused prompt model

## D. Everything is too slow
Usually means:
- model too large
- quant too heavy
- hardware mismatch
- trying to run one huge model for every task when a split setup would be better

---

## 12. Practical recommendations for Neo Studio users

### If your priority is captioning
Start with a caption-friendly multimodal model first.
Make sure multimodal support is actually working before you judge the workflow.

### If your priority is prompting
Start with a good text model first.
You can always add a vision model later.

### If your priority is convenience
Use one multimodal model first, then split later if needed.

### If your priority is quality
Use separate models for captioning and prompting.
That is usually the cleaner long-term route.

---

## 13. Model selection checklist

Before settling on a model, ask:

- Can it do the job I actually need?
- Does it need `mmproj`?
- Can my machine run it without suffering?
- Is the speed usable for my workflow?
- Does the output quality justify the size?
- Would a split setup be smarter?

If the answer to the third question is “barely,” that model is probably not the one to start with 😅

---

## 14. Suggested first test routine

When trying a new model, test these in order:

1. generate one short prompt
2. improve one existing prompt
3. caption one full image
4. caption one face crop
5. caption one person / character image
6. try one batch folder with 3 to 5 images

This gives you a practical feel for:
- quality
- speed
- whether the model is actually worth keeping

---

## 15. Final advice

Do not chase model hype first.
Chase the model that makes your workflow smoother.

A model that is:
- stable
- fast enough
- good enough
- and easy to maintain

is often a better daily driver than a monster model that makes every task feel like a boss fight.

Pick the model setup that lets you actually use Neo Studio Suite consistently.
That matters more than winning a benchmark argument on the internet.

