# Neo_Studio_Suite
A local prompt, caption, metadata, and asset workflow system for Stable Diffusion creators.

Neo Studio Suite is built to make prompting less chaotic and more reusable. It brings together **prompt writing**, **captioning**, **LoRA / TI organization**, **character creation**, **output recovery**, **ControlNet asset handling**, and **reusable generation setups** across two connected environments:

- **Neo Library** — the Forge-side asset, prompt, and generation workflow layer
- **Neo Studio** — the standalone local workspace for writing, captioning, saving, searching, and organizing

Instead of scattering ideas across text files, screenshots, folders, and half-forgotten prompts, Neo Studio Suite gives you a structured system for building, storing, recovering, and reusing the parts of your workflow that actually matter.

---

## Why this project exists

Most SD workflows break down in the same places:

- prompts get lost
- LoRA and TI collections become hard to manage
- captions are generated once and never reused properly
- output metadata is trapped inside images
- character ideas are difficult to keep consistent
- ControlNet assets end up scattered across folders
- useful generation settings are rarely saved as complete reusable setups

Neo Studio Suite was made to solve that.

The goal is not just to generate text. The goal is to create a **repeatable local workflow system** for image generation work:

- write better prompts
- organize reusable assets
- recover useful data from old outputs
- caption images in targeted ways
- store prompts, captions, characters, presets, and bundles properly
- move faster without restarting your whole process every time

---

## Who this is for

Neo Studio Suite is built for people who work seriously with local image-generation workflows, especially:

- Stable Diffusion / Forge users
- LoRA-heavy workflows
- character and style builders
- prompt engineers
- dataset and captioning workflows
- creators who want local-first tools instead of cloud-first dependency chains
- anyone tired of digging through folders called `final_final_v2_real_last` 😭

---

## Architecture

# Why the prompt suite bridge is Split into Two Parts

**Prompt Suite Bridge** is intentionally split into **Neo Library** and **Neo Studio**.

## The Main Reason: Hardware Reality

A lot of local users are working on **low to medium VRAM systems**. Running too many heavy workflows inside Forge at the same time can quickly become slow and inefficient.

Loading extra model workflows directly inside Forge Neo is often **not** the best option for these users.

That is why the suite is designed this way:

- **Neo Library** stays inside **Forge Neo** for generation-facing asset reuse
- **Neo Studio** uses a **separate local backend** for prompting and captioning workflows

## Benefits of This Split

This design keeps the workflow practical and performant:

- Forge Neo can stay focused on **generation-side** work
- Neo Studio can use its own optimized backend for **prompting and captioning**
- Reusable assets can still move freely between both parts
- No need to force everything into one overloaded environment

## Important Usage Advice

⚠️ **It is not recommended** to run:

- Forge / Forge Neo  
- **and** the Neo Studio backend  

**at the same time** on lower or mid-range hardware — unless you already know your system can handle it comfortably.

For many users, opening both at once will heavily slow things down and make the experience worse instead of better.

## Recommended Approach

**Use one heavy environment at a time** whenever possible:

### Phase 1: Preparation
Use **Neo Studio + backend** for:
- Prompting
- Captioning
- Saving
- Searching
- Prep work

### Phase 2: Generation
Use **Forge Neo + Neo Library** for:
- Generation-facing workflows
- Asset reuse

If your machine is strong enough, you can run both with some overlap.  
But for the **intended workflow** — especially on low or medium VRAM systems — treating them as **separate working phases** is the smarter and smoother path.

---

## Neo Library

**Neo Library** lives inside Forge Neo and focuses on the parts of the workflow that need to stay close to actual generation.

It is where you:

- manage reusable prompt assets
- work with LoRA / TI metadata and previews
- build prompts inside Prompt Composer
- manage keywords and map assets
- inspect output metadata
- save and reopen full prompt bundles / projects
- reuse saved prompts, characters, and mapsets directly in the Forge-side workflow

Think of Neo Library as the **generation-facing asset and reuse layer**.

---

## Neo Studio

**Neo Studio** is the standalone local workspace.

It is where you:

- write and refine prompts
- run prompt generation workflows
- caption images and folders
- save prompts and captions into the library
- perform targeted captioning by mode
- search across prompts, captions, characters, presets, LoRAs, and metadata records
- run batch captioning workflows
- manage backup/import/export workflows

Think of Neo Studio as the **workspace, organization, and drafting layer**.

---

## Core feature overview

## Neo Library

### Prompt Composer
The main prompt-building area inside Forge Neo.

Includes:
- positive / negative prompt output workflow
- LoRA + TI Quick Insert
- character creation and reuse
- prompt keyword insertion
- saved prompts access
- prompt bundles / projects
- CN MapSets + saved assets

### Caption Library
A reusable library for saved caption records and caption-driven prompt parts.

### Output Inspector
Recover useful generation data from output images.

Includes:
- output metadata inspection
- prompt recovery
- output comparison
- save recovered data back into your workflow

### Vault + Maps
The structured asset management area.

Includes:
- keywords
- LoRA / TI metadata management
- mapsets
- preview handling
- local metadata scanning
- optional remote preview / metadata import workflows

### Map Generator
Create or manage map-style generation helper assets and connect them back into prompt and ControlNet workflows.

---

## Neo Studio

### Prompt Studio
The standalone prompt-writing and prompt-management workspace.

Includes:
- recent workspace
- prompt preset details
- prompt QA / cleanup
- save prompt
- saved prompts
- character library
- search integration

### Caption Studio
The image captioning and prompt-component workspace.

Includes:
- caption preset details
- targeted caption modes
- save captioned image
- saved captions browser
- prompt components
- batch captioning

### Library Settings
The path, category, import/export, and backup management area.

---

## Standout workflows

### 1. Prompt building
Use Prompt Composer or Prompt Studio to write, refine, save, and reuse prompts instead of rebuilding them from scratch every time.

### 2. LoRA / TI management
Scan local LoRAs and TIs, read metadata, add previews, store notes, and reuse them quickly during prompting.

### 3. Targeted captioning
Caption only what you need:
- full image
- face only
- person / character
- outfit only
- pose only
- location only
- custom crop

Then save those parts and combine them into new prompts later.

### 4. Output recovery
Take an existing generated image, inspect the metadata, recover useful prompt information, compare outputs, and push that information back into your workflow.

### 5. Prompt bundles / projects
Save a complete reusable setup instead of only a text prompt.

A bundle can include:
- positive prompt
- negative prompt
- character
- LoRAs / TIs
- model defaults
- sampler / steps / CFG defaults
- style notes
- reference image
- metadata snapshot

### 6. Batch captioning
Run folder-based captioning workflows, monitor progress, resume incomplete runs, retry failed items, export logs, and use post-task actions for long overnight jobs.

---

## What this tool is **not**

Neo Studio Suite is not trying to be:

- a cloud SaaS prompt app
- a one-click magic prompt generator
- a replacement for Forge itself
- a training framework
- a model host

It is a **local workflow layer** built to support the way real SD users actually work.

---

## Quick start

1. Install and configure the required local backend for Neo Studio.
2. Install Neo Library into your Forge Neo setup.
3. Open Neo Library inside Forge Neo.
4. Open Neo Studio as your standalone local workspace.
5. Set your library paths and backend connection.
6. Start by scanning your local LoRA / TI folders and saving your first prompt or caption record.

For full setup instructions, see:

- `INSTALLATION.md`
- `MODEL_GUIDE.md`
- `NEO_LIBRARY_GUIDE.md`
- `NEO_STUDIO_GUIDE.md`

---

## Documentation map

### Core docs
- `INSTALLATION.md`
- `MODEL_GUIDE.md`

### Feature guides
- `NEO_LIBRARY_GUIDE.md`
- `NEO_STUDIO_GUIDE.md`

### Support docs
- `FAQ_TROUBLESHOOTING.md`
- `CHANGELOG.md`
- `ROADMAP.md`

---

## Current status

Neo Studio Suite is an actively developed local workflow project.

Current highlights include:
- split Neo Library / Neo Studio architecture
- saved captions browser
- output metadata actions
- global search
- LoRA metadata and preview workflows
- prompt QA / linting
- prompt bundles / projects
- full library import / export
- targeted caption modes with detail levels

Some features are still evolving, and the project is designed to grow around actual real-world local workflows rather than a fake polished demo.

---

## Project philosophy

This tool was built around a simple idea:

**good local workflows should be reusable, inspectable, searchable, and worth keeping.**

If a prompt worked, you should be able to save it.
If a caption was useful, you should be able to reuse it.
If a LoRA matters, it should have metadata, previews, and notes.
If an output image contains useful generation history, that data should not stay trapped forever.
If a whole setup works, it should be savable as a bundle — not rebuilt from memory next week.

That is the point of Neo Studio Suite.

---

## Final note

Neo Studio Suite was built to reduce workflow chaos and turn scattered generation habits into an actual reusable system.

If you work locally, save a lot of generation data, experiment with LoRAs, caption heavily, and want your workflow to stop living in random folders and temporary memory, this tool was made for you.
