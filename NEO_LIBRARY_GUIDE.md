# NEO LIBRARY GUIDE

This guide explains **Neo Library** in detail.

Neo Library is the **Forge-side** half of Neo Studio Suite. It lives inside **Forge Neo** and focuses on the parts of the workflow that are closest to actual image generation:

- reusable prompt assets
- LoRA / TI organization
- prompt composition
- ControlNet-related asset groupings
- output recovery
- asset metadata
- reusable generation setups

If **Neo Studio** is the drafting and standalone workspace, **Neo Library** is the place where those reusable parts stay close to your real generation workflow inside Forge.

---

## What Neo Library is for

Neo Library exists so your generation workflow does not turn into a folder graveyard.

It gives you a structured place to:

- build prompts with reusable components
- manage LoRAs and TIs with metadata and previews
- store and reuse prompt keywords
- save prompt records and bundles
- recover prompt data from old outputs
- organize mapsets and supporting assets
- keep generation-facing assets available from inside Forge Neo

The main idea is simple:

**if a workflow asset matters, it should be searchable, reusable, inspectable, and easy to insert back into generation.**

---

## Neo Library overview

Neo Library is organized around these main areas:

- **Prompt Composer**
- **Caption Library**
- **Output Inspector**
- **Vault + Maps**
- **Map Generator**

Each one has a different role, but they are designed to work together.

---

# 1. Prompt Composer

**Prompt Composer** is the main generation-facing workspace inside Neo Library.

This is where you assemble, reuse, and inject generation assets into a working prompt flow.

Think of it as the place where saved prompt parts stop being “library records” and become active generation material again.

---

## 1.1 Output

The **Output** section is the core prompt workspace.

This is where you work with your current:

- positive prompt
- negative prompt
- inserted tokens and assets
- reusable text blocks

### Why it exists
The point of Output is to give you a central place to build a prompt from reusable parts instead of manually rebuilding everything every time.

### Typical use cases
- combine a saved character with LoRA tokens
- insert keyword groups into a fresh prompt
- load a saved prompt and refine it
- open a saved bundle into the active workflow
- recover prompt pieces from Output Inspector and continue working from there

### What to expect here
Depending on the exact current build, this section may include:
- positive prompt output area
- negative prompt output area
- prompt insertion buttons
- quick append / replace actions
- status messages for save/load operations

### Best practice
Treat this section as your **active generation workspace**, not your permanent archive.
Use it to build, test, revise, then save the parts worth keeping.

---

## 1.2 LoRA + TI Quick Insert

This section lets you use your saved **LoRA** and **Textual Inversion (TI)** entries quickly inside Prompt Composer.

It is designed to pull from the data managed in **Vault + Maps → LoRA / TI**.

### What it does
- lists saved LoRA / TI entries
- shows prompt token information
- shows preview image when available
- shows example prompt / trigger / keyword info when available
- lets you insert a clean token block into your working prompt

### Why it exists
LoRA collections get messy fast. Quick Insert gives you a way to use them without browsing folders and guessing names.

### Important behavior
The **actual LoRA token** is kept clean and uses the LoRA name instead of the folder path.

Example:

```text
<lora:Thunderians:0.80>
```

not:

```text
<lora:Character - Real/Thunderians:0.80>
```

### Refresh behavior
Quick Insert is designed to refresh after key asset changes so you do not need to restart Forge just to see updates.

It should refresh after actions like:
- folder scan
- LoRA / TI save or edit
- delete
- imported preview apply
- CivitAI import changes

There is also a manual refresh option as backup.

### Recommended workflow
1. scan your LoRA / TI folders in Vault
2. enrich entries with metadata / previews / notes
3. use Quick Insert in Prompt Composer to insert the clean token block
4. save the final setup as a prompt or bundle if it matters

---

## 1.3 Character creation

This section supports creating and reusing **character records**.

A character record is meant to hold the consistent details you want to preserve for a recurring subject or visual identity.

### What it does
- stores character names and details
- lets you keep reusable character descriptions
- supports character-driven prompt reuse
- can be paired with saved prompts, caption components, and bundles

### Why it exists
Character consistency is one of the first things to fall apart in image workflows. This section gives you a stable place to keep that information reusable.

### Good uses
- recurring OC workflows
- actor-like visual continuity
- outfit / vibe / style consistency
- character setup blocks for prompt templates

### Best practice
Keep character records focused on reusable identity information, not one-off scene details.
Use bundles when you want to save a **full setup**, not just the character itself.

---

## 1.4 Prompt Keywords

This section stores reusable keyword groups, fragments, and insertable prompt parts.

### What it does
- organizes prompt phrases into reusable chunks
- supports category-based keyword storage
- lets you quickly insert curated phrases instead of rewriting them

### Why it exists
A lot of prompting is not about writing from zero. It is about reusing pieces that already work:

- style phrases
- camera terms
- mood descriptors
- clothing fragments
- composition fragments
- texture/material fragments

### Good uses
- curated style packs
- reusable quality phrases
- fantasy / sci-fi / realism blocks
- subject-specific descriptor sets

### Best practice
Do not dump every random phrase here.
Use this section for **repeatable high-value building blocks**.

---

## 1.5 Saved Prompts

This section gives you access to prompt records you decided were worth storing.

### What it does
- stores prompt records
- makes them reusable from inside Forge-side workflows
- lets you reopen prompt content into Prompt Composer

### Why it exists
A prompt that worked once should not have to live inside a screenshot, text file, or memory.

### Difference between Saved Prompts and Bundles
**Saved Prompts** are mainly prompt records.
They are lighter.

**Prompt Bundles / Projects** are full reusable setups with more attached data.

Use:
- **Saved Prompts** for strong text records
- **Bundles** for full generation setups

---

## 1.6 Prompt Bundles / Projects

This section stores a **full reusable creative setup**, not just a text prompt.

This is one of the most important sections in Neo Library because it ties together multiple parts of the system.

### What a bundle can include
- positive prompt
- negative prompt
- attached character
- attached LoRAs / TI entries
- model / checkpoint defaults
- CFG / steps / sampler defaults
- style notes
- reference image
- metadata snapshot

### Why it lives in Neo Library
Bundles are closest to actual generation reuse, which is why they belong here instead of Neo Studio.
They are not just for writing prompts — they are for reopening a whole usable setup inside Forge-side work.

### What you can do
- create a bundle from current state
- update a bundle
- load a bundle
- duplicate a bundle
- delete a bundle
- reopen a bundle into Prompt Composer

### Good uses
- recurring character setups
- project-specific generation presets
- style package reuse
- client-specific visual systems
- “this exact setup worked, save it forever” moments

### Best practice
Use a bundle when the **combination** is what matters.
If only the text prompt matters, save a prompt.
If the whole setup matters, save a bundle.

---

## 1.7 CN MapSets + saved assets

This section is for reusable ControlNet-related or map-based workflow assets.

### What it does
- stores reusable mapsets
- lets you organize saved helper assets
- helps connect map-driven workflows back into actual prompting and generation reuse

### Why it exists
Map-based workflows become messy fast when they are left as random files in random places.
This section gives them a reusable home.

### Good uses
- ControlNet support assets
- grouped maps for recurring workflows
- pose/canny/depth/other map collections
- scene-specific reusable support assets

### Best practice
Think of MapSets as reusable helper packages, not just loose files.

---

# 2. Caption Library

**Caption Library** stores reusable caption records and caption-derived material.

This is where caption outputs stop being temporary and become useful library data.

### What it does
- stores saved caption records
- keeps caption-driven prompt parts reusable
- supports reuse of caption-derived content in later workflows

### Why it exists
Captions are often useful far beyond the first time they are generated.
A good caption can become:
- a prompt seed
- a descriptive component
- a character block
- a style reference
- a saved dataset note

### Good uses
- reusing image descriptions later
- keeping descriptive records tied to saved images
- building prompt fragments from prior caption work
- making caption outputs searchable and worth keeping

### Best practice
Use Caption Library for reusable caption results that matter in generation-facing workflows.
If the caption is disposable, do not treat it like a library asset.

---

# 3. Output Inspector

**Output Inspector** is the output-recovery and metadata-analysis area.

It exists to make old generated images useful again.

### What it does
- inspect output metadata from generated images
- recover prompt-related information
- compare outputs
- rebuild prompt text from recovered data
- save recovered information back into the workflow

### Why it exists
Useful generation data often gets trapped inside images.
Output Inspector gives you a way to pull that information back into a reusable state.

### Main workflows
- upload or inspect an output image
- extract metadata
- review positive / negative prompt info when available
- compare two outputs
- rebuild a cleaner prompt
- send recovered data back into Prompt Composer
- save metadata-linked information into your broader workflow

### Good uses
- recover from old generations
- compare similar outputs
- understand what settings were used
- rebuild a working setup from an output image
- attach recovered data to a bundle or prompt workflow

### Best practice
Use Output Inspector when an image already contains useful generation history.
Do not manually rewrite what the metadata can recover for you.

---

# 4. Vault + Maps

**Vault + Maps** is the structured asset-management side of Neo Library.

If Prompt Composer is the place where assets get used, Vault + Maps is the place where many of them are organized and enriched first.

It includes:
- Keywords
- LoRA / TI
- MapSets

---

## 4.1 Keywords

This section stores reusable keyword assets in a structured way.

### What it does
- saves curated keyword entries
- organizes them into usable categories
- supports reuse in Prompt Composer

### Why it exists
Raw prompting gets better when your best descriptor fragments are organized instead of scattered.

### Good uses
- style collections
- mood collections
- clothing keyword packs
- composition packs
- quality or material blocks

### Best practice
Curate this section. Do not treat it as a dumping ground.
Keywords are more useful when categories and entries are intentional.

---

## 4.2 LoRA / TI

This is one of the most important areas in Neo Library.

It manages local LoRA and TI entries as real reusable assets instead of just files sitting in folders.

### What it does
- scans local LoRA / TI folders
- reads metadata from local files when available
- stores notes and usage fields
- stores preview images
- supports example prompts and trigger words
- supports recommended strength ranges
- supports category and base-model organization
- supports warnings and filtering
- supports remote preview/metadata import from CivitAI

### Why it exists
LoRA and TI collections get out of control quickly.
This section turns them into manageable, reusable records.

### Metadata workflow
LoRA / TI data should be treated with a sensible priority:

1. local file metadata
2. manual user edits
3. remote import enrichment

That way remote imports do not casually overwrite the useful truth already present in the local file or your manual edits.

### Fields you may manage here
Depending on the current entry and workflow, this section may include:
- display name
- trigger words
- keywords
- notes
- preview image
- example prompt
- default strength
- recommended min/max strength
- base model compatibility
- style/use category
- caution notes
- source info

### CivitAI import
This section can fetch remote previews and useful metadata from CivitAI.

Use it to:
- import preview images
- fill missing fields
- optionally overwrite selected fields only

This should be treated as an enhancement path, not a replacement for local metadata scanning.

### Warnings and filters
LoRA / TI management may include things like:
- missing-file warning
- duplicate trigger warning
- category filtering
- base-model filtering
- style/category filtering

### Best practice
Do not rely only on folder names.
Use the metadata fields, preview images, and notes so future-you actually knows what a LoRA is for.

---

## 4.3 MapSets

This section stores reusable grouped map assets.

### What it does
- organizes map-based support assets
- keeps them grouped for recurring workflows
- makes them easier to reuse from Prompt Composer or related generation paths

### Why it exists
Map workflows are rarely just one file.
They often involve a reusable group of files or a known combination that supports a particular result.

### Good uses
- pose-related support groups
- ControlNet helper packs
- reusable scene-control assets
- consistent workflow bundles for map usage

### Best practice
Store MapSets with names and categories that explain the use case, not just the technical map type.

---

# 5. Map Generator

**Map Generator** supports workflows related to generating or preparing map-like helper assets.

### What it does
- helps produce or prepare helper map outputs
- supports workflows that feed into ControlNet or related asset reuse
- connects map generation back into saved assets and MapSets

### Why it exists
Map workflows are too important to leave completely disconnected from the rest of the system.
This section helps bridge generation support assets back into Neo Library.

### Good uses
- preparing generation helper maps
- organizing support assets for future reuse
- building reusable control inputs instead of remaking them every time

### Best practice
Treat generated maps as workflow assets when they are reusable, not just throwaway byproducts.

---

# How Neo Library sections connect to each other

Neo Library works best when the sections are used together.

### Example workflow 1 — LoRA-first prompting
1. scan and enrich LoRAs in **Vault + Maps → LoRA / TI**
2. use **LoRA + TI Quick Insert** in Prompt Composer
3. refine prompt in Output
4. save as Saved Prompt or Bundle

### Example workflow 2 — recover from an old output
1. inspect image in **Output Inspector**
2. rebuild prompt or recover useful information
3. send it into Prompt Composer
4. save the result as a prompt or bundle

### Example workflow 3 — keyword-driven building
1. curate reusable phrase sets in **Vault + Maps → Keywords**
2. insert them in Prompt Composer
3. combine with character and LoRA entries
4. save final reusable setup

### Example workflow 4 — reusable generation setup
1. build a working setup in Prompt Composer
2. attach character, LoRAs, defaults, notes, and reference
3. save it as **Prompt Bundle / Project**
4. reopen it later directly in Neo Library when needed

---

# Recommended first steps in Neo Library

If you are new to Neo Library, the best order is:

1. confirm the tab loads inside Forge Neo
2. scan your LoRA / TI folders in Vault
3. enrich a few entries with metadata and previews
4. test LoRA + TI Quick Insert in Prompt Composer
5. save one prompt
6. inspect one old output in Output Inspector
7. create one bundle/project from a real working setup
8. test map-related storage only after the basic prompt workflow is working

That gives you a clean path into the system without trying to do everything at once.

---

# Best practices for Neo Library

## Keep metadata useful
Do not leave important entries blank if you already know what they do.
Future-you will not magically remember.

## Save the things that actually matter
Not every prompt or map needs to become a permanent record.
Save the ones that are worth reusing.

## Separate prompt records from full setups
Use **Saved Prompts** for prompt text.
Use **Bundles** for full generation setups.

## Treat previews as working aids
LoRA previews are not just cosmetic. They help identify the right asset faster.

## Use Output Inspector when you already have a useful image
Do not waste time reverse-engineering something the metadata already knows.

---

# What Neo Library is not trying to be

Neo Library is not meant to replace Forge itself.
It is not a model host.
It is not a training pipeline.
It is not a cloud asset manager.

It is a **local Forge-side workflow and asset system** built to make generation reuse cleaner and less chaotic.

---

# Continue reading

After this guide, continue with:

- `NEO_STUDIO_GUIDE.md`
- `FAQ_TROUBLESHOOTING.md`
- `MODEL_GUIDE.md`
- `INSTALLATION.md`

If Neo Library is where your assets live close to generation, Neo Studio is where you do the heavier standalone drafting, captioning, searching, and transfer work.

