# INSTALLATION

This guide walks through the local setup for **Neo Studio Suite**, including:

- Neo Studio
- Neo Library
- KoboldCpp backend setup
- captioning model setup
- prompt-generation model setup
- path and workflow notes

Neo Studio Suite is designed as a **local-first workflow system**. That means you are expected to run your own backend models and keep your working assets on your machine.

---

## 1. What you need

Before installing Neo Studio Suite, make sure you have:

- a Windows PC or another environment where your local workflow is already running cleanly
- **Forge Neo** installed and working, for **Neo Library**
- Python installed for the standalone **Neo Studio** side
- a local GGUF backend for Neo Studio
- enough RAM / VRAM for the models you want to run
- basic familiarity with where your models and Stable Diffusion assets live

---

## 2. Architecture reminder

Neo Studio Suite is split into two parts:

## Neo Library

This is the Forge-side part of the system.

You place **Neo Library** inside your Forge Neo extensions workflow so it becomes available from inside Forge Neo.

Use Neo Library for:
- Prompt Composer
- Vault + Maps
- LoRA / TI workflows
- Output Inspector
- Caption Library
- Prompt Bundles / Projects
- Map Generator

---

## Neo Studio

This is the standalone local workspace.

Use Neo Studio for:
- Prompt Studio
- Caption Studio
- targeted captioning
- batch captioning
- global search
- prompt QA
- saved prompts and captions
- library import / export

Neo Studio uses a **local LLM backend**.

---

## 3. Recommended backend for Neo Studio

The recommended backend for Neo Studio is **KoboldCpp**.

### KoboldCpp project

Download it from:

`https://github.com/LostRuins/koboldcpp`

### Basic setup idea

1. Download or place KoboldCpp in its own folder.
2. Run the `.exe`.
3. Load a GGUF model.
4. Start the backend.
5. Point Neo Studio to the backend URL in its settings.

If you want to use **image captioning / vision models**, you will also need the correct **mmproj** file for multimodal support when the model requires it.

---

## 4. Folder suggestion

A clean setup might look something like this:

```text
D:\AI\KoboldCpp\
D:\AI\Models\Captioning\
D:\AI\Models\Prompting\
D:\AI\ForgeNeo\
D:\AI\NeoStudio\
```

You do not have to use this exact layout.
The important part is keeping:

- backend files
- model files
- Forge files
- Neo Studio files

organized enough that you can maintain them later.

---

## 5. Model setup basics

Neo Studio Suite can work with different GGUF models depending on what you want to do.

There are two main model roles:

## A. Captioning / vision models
Use these when you want Neo Studio to describe images.

Examples:
- full image captioning
- face-only captioning
- person / character captioning
- outfit / pose / location captioning
- batch captioning

These models usually need:
- a **GGUF model file**
- and, for many multimodal models, a matching **mmproj** file

---

## B. Prompting / text-generation models
Use these when you want Neo Studio to:
- generate prompts
- improve prompts
- continue prompts
- rewrite prompts
- expand prompt ideas

These models usually need:
- a **GGUF model file**
- no image projection file unless they are multimodal

---

## 6. Suggested models

These are **suggestions**, not hard requirements.

Use the models that fit your hardware and your own preferences.

---

## Captioning suggestions

### JoyCaption
Project:

`https://github.com/1038lab/ComfyUI-JoyCaption`

Use this if you want a captioning-focused workflow and you are already familiar with JoyCaption-style outputs.

### ToriiGate
Model page:

`https://huggingface.co/mradermacher/ToriiGate-v0.4-7B-GGUF`

Use this when you want a multimodal GGUF option for image understanding / caption-style workflows.

### Important note
For multimodal captioning models, make sure you download:
- the **GGUF model file**
- and the matching **mmproj** file when the model requires one

---

## Prompting suggestions

### Dolphin
Model page:

`https://huggingface.co/bartowski/cognitivecomputations_Dolphin3.0-R1-Mistral-24B-GGUF`

A good option for prompt-generation style work if your system can handle the size.

### Qwen3-VL
Model page:

`https://huggingface.co/Qwen/Qwen3-VL-32B-Instruct-GGUF/tree/main`

This can also be used when you want a stronger multimodal-capable model.

### Note
Some captioning-capable models can also be used for prompt generation.
So depending on your setup, you may choose:
- one model for both jobs
- or separate models for captioning and prompting

---

## 7. Choosing the right model size

Do **not** download random quants blindly.

Pick a model size that matches your:
- VRAM
- RAM
- speed tolerance
- quality needs

### General advice
- lower quants are lighter and faster, but can lose quality
- mid quants are often the best balance
- larger quants need more VRAM/RAM and are slower, but may give better results

If your machine struggles:
- go smaller first
- confirm the workflow works
- then scale up later

The model suggestions in this project are based on practical usage, not strict requirements.
You are free to use other compatible models.

---

## 8. Neo Library installation

Neo Library is meant to live inside your Forge Neo environment.

### General install idea

1. Locate your Forge Neo `extensions` folder.
2. Place the `neo_library_v1` folder there.
3. Restart Forge Neo.
4. Open Forge Neo and confirm the Neo Library tab appears.

### Example layout

```text
F:\LLM\sd-webui-forge-neo\extensions\neo_library_v1\
```

If you already use Forge extensions, install it the same way you install your other local extensions.

---

## 9. Neo Studio installation

Neo Studio is the standalone local side.

### General install idea

1. Place the `neo_studio_v1` folder wherever you keep your local tools.
2. Install any required Python dependencies for the project.
3. Run Neo Studio using the provided launcher or your preferred Python command.
4. Open Neo Studio in your browser.
5. Point it to the local backend.
6. Set the library paths in **Library Settings**.

### Suggested layout

```text
D:\AI\NeoStudio\neo_studio_v1\
```

---

## 10. Connecting Neo Studio to KoboldCpp

Once KoboldCpp is running:

1. copy the backend URL / host / port you are using
2. open Neo Studio
3. go to the settings area if needed
4. enter the backend URL
5. test the connection

If prompt generation works but captioning does not, check whether:
- you loaded a multimodal model
- you loaded the correct **mmproj** file
- the backend is actually running with image support

---

## 11. First recommended setup steps

After installation, the best order is:

1. confirm Forge Neo loads **Neo Library**
2. confirm Neo Studio can open and connect to the backend
3. scan your LoRA / TI folders in **Vault + Maps**
4. check that LoRA / TI Quick Insert updates correctly
5. save one test prompt
6. caption one test image
7. test one targeted caption mode
8. test one batch caption run on a small folder
9. export a small library backup

That gives you a full workflow sanity check before you start loading hundreds of assets.

---

## 12. Common setup tips

### Use separate folders for model roles
If possible, keep:
- captioning models
- prompting models
- multimodal extras like `mmproj`

in clean folders so you do not lose track of which files belong together.

### Keep your library paths stable
Avoid constantly moving your prompt/caption/library folders around after setup.
It is possible to recover, but stable paths make life easier.

### Start small
Before doing batch jobs or large imports:
- test one image
- test one prompt save
- test one LoRA scan
- test one export

This prevents much larger cleanup pain later.

---

## 13. What to read next

After installation, continue with:

- `MODEL_GUIDE.md`
- `NEO_LIBRARY_GUIDE.md`
- `NEO_STUDIO_GUIDE.md`
- `FAQ_TROUBLESHOOTING.md`

---

## 14. Final note

Neo Studio Suite works best when treated as a **structured local workflow**, not just a random collection of tabs.

Take a little time to:
- organize models
- organize LoRAs / TIs
- confirm your backend
- test your save/load flow
- keep backups

That makes the rest of the system much smoother.

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

Some features are still evolving, and the project is being shaped around real local workflows rather than a fake polished demo.

---

## License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this project, including in commercial work, as long as the original copyright and license notice are included.

See the `LICENSE` file for full details.

---

