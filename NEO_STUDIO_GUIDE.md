# NEO STUDIO GUIDE

This guide explains **Neo Studio** in detail.

Neo Studio is the **standalone local workspace** half of Neo Studio Suite. It is where you do the heavier drafting, captioning, saving, searching, and transfer work outside Forge Neo.

If **Neo Library** is the Forge-side asset and reuse layer, **Neo Studio** is the place where you:

- write and refine prompts
- generate and improve prompt text
- caption images and folders
- extract targeted prompt parts from images
- search across your saved library
- run batch workflows
- save prompts, captions, components, and presets
- manage import/export and backup workflows

Neo Studio is built to reduce workflow chaos before, during, and after generation work.

---

## What Neo Studio is for

Neo Studio exists so the standalone parts of your workflow do not become a mess of:

- temporary prompt drafts
- random caption results
- unsorted reference images
- disconnected presets
- repeated rewrite work
- half-finished batch jobs
- forgotten saved records

It gives you a structured local workspace for turning messy workflow fragments into reusable records.

The core idea is simple:

**if you create useful prompt or caption material, it should be easy to save, search, refine, and reuse.**

---

## Neo Studio overview

Neo Studio is organized around three main areas:

- **Prompt Studio**
- **Caption Studio**
- **Library Settings**

These sections are designed to work together.

---

# 1. Prompt Studio

**Prompt Studio** is the standalone prompt-writing and prompt-management workspace.

This is where you:

- write prompts from scratch
- generate prompt ideas
- improve prompt drafts
- save prompts and presets
- run prompt QA / cleanup
- search and reopen saved prompt material
- reuse character records in a writing workflow

Think of Prompt Studio as your drafting desk, not your final asset archive.

---

## 1.1 Recent Workspace

The **Recent Workspace** section helps you jump back into things you were working with recently.

### What it does
It can surface recently touched items such as:

- prompts
- captions
- characters
- presets
- metadata-driven prompt records
- bundles or linked setup records when relevant to the workflow

### Why it exists
Most people do not work in a perfectly linear way. You try something, switch tasks, come back later, and then forget where the useful version went.

Recent Workspace helps reduce that friction.

### Good uses
- reopen a prompt you were refining earlier
- revisit a caption you want to turn into a prompt
- continue from a recent character-based workflow
- recover your place after testing several variants

### Best practice
Use Recent Workspace for fast re-entry, but still save the things that truly matter into the proper library records.

---

## 1.2 Prompt preset details

This section is for managing **prompt presets** and applying repeatable prompt-generation settings.

### What it does
Depending on your current build and preset structure, this section may include:

- preset save/load
- favorite or grouped presets
- preset notes / intended use
- duplicate preset
- compare preset vs preset
- usage count / last-used info
- preset export for single items

### Why it exists
A lot of prompt work is not just about the prompt text itself. It is also about the **way** you generate, improve, or rewrite the text.

Prompt presets help keep those reusable settings consistent.

### Good uses
- a preset for concise cinematic prompts
- a preset for descriptive prompt generation
- a preset for cleanup / rewrite work
- a preset for variation generation
- a preset for safer, lower-noise outputs

### Best practice
Name presets by workflow purpose, not just mood.
Examples:
- `Descriptive Portrait Prompt`
- `Short Product Prompt`
- `Cleanup / Deduplicate`
- `Attribute-Rich Character Draft`

That makes them much easier to reuse later.

---

## 1.3 Prompt QA / cleanup

This section helps catch messy prompts before you commit them to actual use.

### What it does
Prompt QA / cleanup can analyze prompt text and flag things like:

- repeated tags
- contradictory terms
- filler / low-value phrases
- overloaded style phrases
- overloaded camera terms
- prompt length issues
- weak subject clarity
- weak ordering / structure

### Why it exists
A lot of prompt quality problems are not because the idea is bad. They happen because the text is messy, repetitive, contradictory, or bloated.

This section gives you a quick lint-style pass before the prompt gets used.

### Good uses
- clean up a messy generated draft
- catch contradictions in style-heavy prompts
- reduce redundant phrasing
- tighten prompt ordering before saving

### What to expect
A small QA panel may include:
- warning summary
- prompt stats
- actionable suggestions
- manual cleanup actions

### Best practice
Use QA as a **second pass**, not as a replacement for taste or judgment.
The goal is useful warnings, not blind obedience to every lint rule.

---

## 1.4 Save Prompt

This section handles saving prompt records that are worth keeping.

### What it does
- stores prompt text as reusable records
- keeps prompt data searchable later
- supports integration with search, recents, and library workflows

### Why it exists
If a prompt worked once, or even if it is a strong draft worth returning to, it should be easy to save without leaving the workspace.

### Good uses
- save a working positive/negative pair
- store a reusable style prompt
- preserve a client/project-specific prompt draft
- save a refined version after QA cleanup

### Best practice
Do not save every throwaway experiment.
Save the prompts that are reusable, instructive, or worth comparing later.

---

## 1.5 Saved Prompts

This section lets you browse and reopen prompt records from the standalone side.

### What it does
- lists saved prompt records
- lets you reopen them into Prompt Studio
- supports editing / reuse / re-save workflows
- connects with search and recent items

### Why it exists
A saved prompt should be easy to reuse without leaving the tool or digging through raw files.

### Difference from Prompt Bundles / Projects
Saved Prompts are mainly prompt records.

Full **Prompt Bundles / Projects** are managed in **Neo Library**, because they represent a broader generation setup that belongs closer to the Forge-side workflow.

If you need the whole generation setup, use Bundles in Neo Library.
If you need strong text records, use Saved Prompts here.

---

## 1.6 Character Library

This section gives Prompt Studio access to saved character records.

### What it does
- lets you browse saved characters
- pull character information into active prompt drafting
- reuse consistent visual identity details

### Why it exists
Character reuse should not require copying text between random notes.
This section keeps character-driven prompt writing practical.

### Good uses
- recurring characters
- visual identity consistency
- style-locked character prompts
- combining characters with targeted caption components later

### Best practice
Use Character Library for identity continuity.
Use Prompt Studio to adapt that identity into scene-specific prompts.

---

## 1.7 Search integration inside Prompt Studio

Prompt Studio benefits heavily from the global search workflows available across Neo Studio.

### What it does
You can search across things like:
- prompts
- captions
- characters
- presets
- LoRA records
- metadata records
- bundles when relevant to the overall system

### Why it exists
A strong search layer prevents the tool from becoming a fancy storage closet you never open again.

### Best practice
Search first before rewriting something from scratch. Many workflows become faster once you start reusing what you already saved.

---

# 2. Caption Studio

**Caption Studio** is the captioning, prompt-component, and image-description side of Neo Studio.

It is one of the strongest parts of the suite because it is not limited to simple full-image captions. It supports targeted workflows designed to help with actual prompt building.

---

## 2.1 Caption preset details

This section stores reusable **caption presets**.

### What it does
Depending on your build, caption presets may include settings for:

- caption mode
- component type
- detail level
- category or intended use
- notes / purpose
- reuse in both single and batch workflows

### Why it exists
Not every captioning job is the same.
Sometimes you want:
- a short full-image description
- a detailed face breakdown
- an outfit-only extraction
- an attribute-rich person description

Presets let you switch between these workflows without resetting everything manually.

### Best practice
Save presets by use case.
Examples:
- `Face Only / Attribute-Rich`
- `Outfit Only / Detailed`
- `Location Only / Basic`
- `Batch Caption / General`

---

## 2.2 Targeted caption modes

This is one of the standout features in Caption Studio.

Instead of captioning only the whole image, you can target the part you actually want for prompt building.

### Available modes
- **Full image**
- **Face only**
- **Person / character**
- **Outfit only**
- **Pose only**
- **Location only**
- **Custom crop**

### Why this exists
When building prompts, you often do not want the model to describe everything.
You may only want:
- the face
- the clothing
- the pose
- the environment
- the full visible person as a character reference

Targeted caption modes make that workflow practical.

### Best use cases by mode
#### Full image
Use when you want a general caption of the whole image.

#### Face only
Use when you want visible facial details such as:
- face shape
- eyebrow shape
- eye shape or color when visible
- lips
- nose
- hair details
- expression

#### Person / character
Use when you want a fuller visible breakdown of the subject, such as:
- body build
- posture
- outfit
- accessories
- hairstyle
- visible face details
- overall character vibe

#### Outfit only
Use when you want clothing details and want the rest of the image deprioritized.

#### Pose only
Use when pose or body positioning matters more than clothes or background.

#### Location only
Use when you want the environment or scene rather than the subject.

#### Custom crop
Use when none of the preset target regions are enough and you want manual control.

### Best practice
Choose the mode based on what you actually want to save or reuse later. This keeps your components cleaner and more useful.

---

## 2.3 Detail levels

Targeted captioning also supports **detail levels**.

### Available levels
- **Basic**
- **Detailed**
- **Attribute-rich**

### Why this exists
Not every caption needs to be a full attribute breakdown.
Sometimes you want a quick usable description.
Sometimes you want a deeper visible-detail extraction.

### Practical guidance
#### Basic
Use for quick notes or lightweight caption workflows.

#### Detailed
Use when you want a fuller description without going too forensic.

#### Attribute-rich
Use when you want visible attribute breakdowns for things like:
- faces
- people / characters
- clothing
- scene parts

This is especially useful for prompt building where you want richer descriptive control.

### Important note
The goal is to describe **visible details**, not invent hidden ones.
Attribute-rich mode should stay grounded to what can actually be seen.

---

## 2.4 Crop workflow

Caption Studio supports crop-aware targeted captioning.

### What it does
- shows a crop preview
- supports manual crop box selection
- supports crop-aware captioning
- can use mode-aware crop guidance for targeted workflows

### Why it exists
Just telling a captioning model to “describe only the face” is weaker than also helping it focus on the right region.
Crop support makes targeted captioning more reliable.

### Typical workflow
1. choose caption mode
2. choose detail level
3. set or adjust crop if needed
4. run caption on the selected target
5. save the result as a reusable component

### Best practice
If the image is visually busy, use crop support instead of relying only on instructions.
That usually gives cleaner results.

---

## 2.5 Save Captioned Image

This section handles saving caption records that are worth keeping.

### What it does
It can save:
- the caption text
- the image reference
- notes
- caption mode
- detail level
- component type
- crop metadata when relevant

### Why it exists
Good caption outputs should be reusable, not disposable.
This section turns a one-off caption into a record you can search and use later.

### Good uses
- save a strong face description
- keep a clothing component for later prompt reuse
- store a location caption tied to its image
- preserve a character-style image description

### Best practice
Save captions when they provide reusable descriptive value. If they are weak or redundant, regenerate or skip them.

---

## 2.6 Saved Captions Browser

This section lets you browse saved caption records in a more useful way than raw file browsing.

### What it does
Depending on your build, it may support:
- search
- filtering by category, model, style, date, type, or mode
- thumbnail grid
- full image preview
- caption editing
- delete
- duplicate as prompt
- send caption into Prompt Studio

### Why it exists
Saved captions become much more useful when you can actually browse, filter, inspect, and repurpose them.

### Good uses
- find all face descriptions in a category
- reopen a caption tied to a specific image
- turn a caption into a prompt draft
- review and edit saved notes later

### Best practice
Use the browser as a reusable caption library, not just storage.
If a caption is saved, it should be discoverable and useful.

---

## 2.7 Prompt Components

This section turns saved caption outputs into reusable **prompt parts**.

### What it does
It can work with saved component types such as:
- face
- person / character
- outfit
- pose
- location
- custom

You can:
- browse saved components
- select multiple components
- combine them into a new draft
- send that draft into Prompt Studio

### Why it exists
A lot of prompt building is modular.
You may want:
- the face from one image
- the outfit from another
- the location from another
- the pose from another

Prompt Components makes that possible without rewriting everything by hand.

### Best practice
Save components with clear categories and meaningful detail levels so they stay useful when you come back later.

---

## 2.8 Batch Captioning

This section is for folder-based caption workflows and larger caption jobs.

### What it does
Depending on your current build, Batch Captioning can support things like:
- folder scan
- batch runs
- cancel current batch safely
- resume incomplete batch
- retry failed items only
- ETA display
- duplicate summary
- export batch log
- post-task action options after completion

### Why it exists
Large caption workflows are painful when they are fragile.
Batch Captioning is there to make them more reliable and more practical for real use.

### Good uses
- caption a reference-image folder
- build caption libraries from image sets
- run overnight jobs
- process prompt-component source folders in batches

### Best practice
Start with a small test batch before you throw 1000 images at it.
That saves a lot of cleanup pain.

### Safe cancel behavior
A well-behaved batch cancel should stop **after the current item finishes**, not hard-kill the process mid-write.
That keeps the batch state cleaner.

### Post-task actions
When available, these can help for overnight runs, such as:
- do nothing
- sleep
- hibernate
- shut down

Always make sure other unsaved work is not open before using those options.

---

# 3. Library Settings

**Library Settings** is the management and transfer side of Neo Studio.

It handles the practical system-level parts of keeping your saved data organized and portable.

---

## 3.1 Paths and storage behavior

This section controls or reflects where Neo Studio stores and reads key library data.

### Why it matters
If your paths are chaotic, your workflow becomes chaotic too.
Stable storage paths make everything else easier.

### Best practice
Set your library paths early and avoid moving them constantly unless you are intentionally migrating or reorganizing.

---

## 3.2 Categories

Library Settings may include category-related handling for organizing prompts, captions, or other saved records.

### Why it exists
Categories are the difference between “saved somewhere” and “findable later.”

### Best practice
Use categories intentionally. Avoid meaningless category sprawl.

---

## 3.3 Full library import / export

This section is one of the most practical long-term features in Neo Studio.

### What it does
It supports backup and migration workflows such as:
- export prompts
- export captions
- export characters
- export presets
- export selected categories
- export metadata records
- export prompt bundles when relevant to shared storage
- export a full library snapshot

It also supports importing with conflict behavior such as:
- merge
- overwrite
- skip duplicates

### Why it exists
If you are building a serious workflow system, backup and migration should not feel like a side quest.

### Good uses
- move your library to a new install
- create a backup before large changes
- share a curated library pack with yourself across systems
- recover after reinstall or migration work

### Best practice
Export before major changes, not after things already went wrong.

---

## 3.4 Transfer and backup philosophy

Library Settings is where Neo Studio becomes more than a workspace.
It becomes a tool that respects the fact that your saved data actually matters.

### Why this matters
A workflow system is only truly useful if you can:
- keep your data safe
- move it cleanly
- recover from mistakes
- understand what was imported or overwritten

That is why import/export belongs here.

---

# How Neo Studio sections connect to each other

Neo Studio works best when the sections support one another.

### Example workflow 1 — prompt drafting
1. write or generate a prompt in **Prompt Studio**
2. run **Prompt QA / cleanup**
3. save the final version in **Save Prompt**
4. reopen it later through **Saved Prompts** or search

### Example workflow 2 — targeted caption to prompt
1. caption an image in **Caption Studio** using a targeted mode
2. save the result as a typed component
3. combine components in **Prompt Components**
4. send the merged draft into **Prompt Studio**
5. refine and save the final prompt

### Example workflow 3 — batch reference processing
1. configure **Batch Captioning**
2. run a small test batch
3. resume or retry failed items if needed
4. browse results in **Saved Captions Browser**
5. reuse the best outputs as prompt components

### Example workflow 4 — backup and migration
1. save your prompt, caption, and character records normally
2. go to **Library Settings**
3. export selected records or a full snapshot
4. restore later with merge / overwrite / skip options

---

# Recommended first steps in Neo Studio

If you are new to Neo Studio, the cleanest path is:

1. confirm the backend connection works
2. generate or edit one test prompt in Prompt Studio
3. run Prompt QA once
4. save one prompt record
5. caption one image in Caption Studio
6. test one targeted mode such as Face only or Person / character
7. save one captioned image
8. try one small batch caption run
9. export a small library backup

That gives you a full basic workflow test without diving into everything at once.

---

# Best practices for Neo Studio

## Save what is reusable
Not every draft needs to become permanent, but good drafts should not vanish into the void.

## Use targeted captioning intentionally
Pick the mode that matches what you actually want to reuse.
That keeps your components stronger.

## Let search do its job
Before creating something from scratch again, search for it.
You may already have the useful version saved.

## Use presets by purpose
Name prompt and caption presets based on what they do, not whatever mood you were in that day.

## Back up before large changes
If you are reorganizing categories, importing big sets, or moving installs, export first.

---

# What Neo Studio is not trying to be

Neo Studio is not trying to replace Forge.
It is not trying to be a cloud prompt generator.
It is not a model host.
It is not a training system.

It is a **standalone local workflow workspace** built to make drafting, captioning, searching, and saving less chaotic.

---

# Continue reading

After this guide, continue with:

- `NEO_LIBRARY_GUIDE.md`
- `INSTALLATION.md`
- `MODEL_GUIDE.md`
- `FAQ_TROUBLESHOOTING.md`

If Neo Library is where your reusable generation assets stay close to Forge, Neo Studio is where you build, refine, caption, search, and transfer the pieces that make those assets worth keeping.

