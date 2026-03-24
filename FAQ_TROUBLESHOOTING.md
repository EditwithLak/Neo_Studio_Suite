# FAQ / TROUBLESHOOTING

This guide covers common setup problems, workflow issues, and confusing behavior you may run into while using **Neo Studio Suite**.

It focuses on the issues most likely to waste your time if they are not explained clearly.

---

# 1. General troubleshooting mindset

Before assuming something is deeply broken, check the basics first:

- is the backend actually running?
- are you using the right model for the task?
- if the model is multimodal, did you load the matching `mmproj` when needed?
- are your library paths correct?
- did the save actually complete?
- did the UI need a refresh after an update?
- are you testing on one small input before a giant batch job?

A lot of “the tool is broken” moments are really:
- wrong backend state
- wrong model type
- stale UI data
- missing files
- invalid paths
- old cached assumptions

---

# 2. Neo Studio issues

## 2.1 Neo Studio opens, but the backend does not respond

### Symptoms
- prompt generation does nothing
- captioning does nothing
- status looks disconnected
- test requests fail

### Check these first
- make sure your local backend is actually running
- confirm the host / port / URL are correct
- confirm the model loaded successfully
- confirm the backend is not frozen on model load

### Common causes
- wrong backend URL
- backend was closed
- model failed to load
- port mismatch
- trying to caption with a non-vision model

### What to do
1. restart the backend
2. confirm the model is loaded
3. confirm the URL in Neo Studio
4. test one simple prompt request first
5. then test one image caption

---

## 2.2 Prompt generation works, but captioning does not

### Symptoms
- text generation works
- image captioning fails or ignores images
- caption output is empty or useless

### Common causes
- you loaded a text-only model
- the multimodal model needs `mmproj` and it was not loaded
- the wrong `mmproj` was used
- the backend is not actually running in a multimodal-capable state

### What to do
- make sure you are using a vision-capable model
- load the matching `mmproj` when required
- test on one simple image first
- confirm full-image captioning works before trying targeted modes

---

## 2.3 Caption Studio tab does not open or behaves strangely

### Symptoms
- clicking the tab does nothing
- the tab looks dead
- page controls stop responding

### Likely cause
A frontend JavaScript error can break tab behavior.

### What to do
- refresh the browser page fully
- check whether a recent code edit introduced a JS syntax issue
- test whether other tabs also behave oddly
- open browser dev tools if you are comfortable checking console errors

### Prevention
After code changes, run a syntax check on updated JS files before shipping them.

---

## 2.4 Saved prompt or caption changes do not appear immediately

### Symptoms
- you saved something, but it still looks old
- the browser panel does not seem updated yet

### Common causes
- stale UI state
- filter/search hiding the updated record
- update saved, but the current view needs refresh

### What to do
- refresh the relevant browser panel or search view
- clear filters temporarily
- reopen the saved record
- confirm the save message was successful

---

## 2.5 Search does not show the item I expected

### Symptoms
- you know the item exists, but search misses it
- only partial results show up

### Common causes
- wrong search terms
- active filters excluding the item
- item saved in a different type/category than expected
- newly saved data not yet reloaded into the current view

### What to do
- search with simpler terms first
- clear active filters
- try category or type filters explicitly
- verify the record was actually saved where you think it was

---

# 3. Caption Studio issues

## 3.1 Targeted captioning describes too much of the image

### Symptoms
- face mode still talks about clothes or background
- outfit mode includes pose or location details
- location mode keeps talking about the person

### Why this happens
Targeted captioning in V1 relies mainly on:
- crop focus
- mode-specific prompt instructions

If the selected area is too broad or visually busy, the model may still include extra details.

### What to do
- use a tighter crop
- use **Custom crop** if the preset area is not focused enough
- try **Detailed** or **Attribute-rich** only when the visible target is clear
- simplify the test image first

### Best practice
For busy images, manual crop beats vague hope every time.

---

## 3.2 Face-only captions miss details I expected

### Symptoms
- eye color not mentioned
- hair detail feels weak
- lip / brow / jawline detail is vague

### Common causes
- face area is too small in the image
- low image quality
- crop is too loose
- model is weak at fine facial detail
- detail level is too low

### What to do
- crop closer to the face
- use **Attribute-rich** detail level
- test with a higher-quality image
- compare results with a stronger captioning model if available

### Important note
The model can only describe what is actually visible well enough to detect.
Do not expect magic forensic detail from a blurry low-res crop.

---

## 3.3 Person / character captions feel too shallow

### Symptoms
- build, outfit, and vibe are vague
- the output sounds generic

### Common causes
- detail level too low
- crop too broad or too small
- model too weak for richer image understanding
- image itself does not show enough visual information clearly

### What to do
- use **Detailed** or **Attribute-rich**
- crop the subject more cleanly
- test another model if the current one is weak at visual detail
- save only the strong results, not every weak caption

---

## 3.4 Custom crop does not give better results

### Common causes
- crop box still includes too much noise
- the target feature is too small
- the model is weak for the task

### What to do
- crop tighter
- test on a clearer image
- use the crop to isolate the important region, not just “smaller version of the same chaos”

---

## 3.5 Batch captioning stops or feels unreliable

### Symptoms
- batch stops partway through
- some items fail
- output feels incomplete

### Common causes
- unstable backend
- very large job without testing first
- model/backend ran out of patience/resources
- bad source images in the folder

### What to do
- test a small batch first
- resume the batch if supported
- retry failed items only
- export the batch log and inspect the failures
- check image file integrity

### Best practice
Do not throw 1000 images at a workflow you have not tested on 5 images first.

---

## 3.6 Post-task shutdown / sleep is risky

### Yes, it can be.

If you use post-task actions like:
- sleep
- hibernate
- shut down

make sure:
- the batch finished cleanly
- the summary/log was saved
- you do not have unrelated unsaved work open

Always use these options intentionally, especially for overnight jobs.

---

# 4. Neo Library issues

## 4.1 Neo Library tab does not appear in Forge Neo

### Check these first
- confirm the extension folder is in the correct Forge `extensions` location
- restart Forge Neo fully
- check whether the extension threw an error during startup

### Common causes
- wrong folder placement
- missing files
- Python/module error during extension load
- syntax/import issue after a code change

### What to do
- confirm the path
- restart Forge
- read the Forge console traceback if one appears

---

## 4.2 LoRA / TI Quick Insert does not show new entries until restart

### Why this used to happen
The UI can hold stale choices if the quick-insert list was only built once at startup.

### Expected behavior now
After actions like:
- folder scan
- save/edit
- delete
- import preview apply

Quick Insert should refresh.

### What to do if it still looks stale
- use the manual **Refresh LoRA/TI** button
- confirm the asset actually saved correctly
- confirm the entry is not filtered out or missing required fields

---

## 4.3 LoRA / TI details panel shows errors or no details

### Symptoms
- red error pills
- preview or metadata does not load
- quick insert details stay blank

### Common causes
- bad callback path after code change
- missing helper function import
- corrupted or incomplete metadata path
- stale UI state after an update

### What to do
- check the Forge console traceback
- confirm the current extension files are synced
- refresh the tab or restart Forge if the code was just replaced
- verify the selected entry actually exists in the store

---

## 4.4 LoRA token includes folder path instead of only the LoRA name

### Wrong example
```text
<lora:Character - Real/Thunderians:0.80>
```

### Correct example
```text
<lora:Thunderians:0.80>
```

### Why this matters
Prompt tokens should use the actual LoRA name, not the folder path.
Folder/category info is useful for browsing, but not for the generated token text.

### If this shows up again
Check the token builder logic, not just the display label.

---

## 4.5 LoRA or TI scan works, but metadata feels incomplete

### Why this happens
Not every local file contains rich metadata.
Some assets include useful embedded information. Others barely include anything helpful.

### What to do
- enrich the entry manually
- add notes, preview, example prompt, and categories yourself
- use remote enrichment like CivitAI import where helpful

### Best practice
Treat local metadata reading as a starting point, not guaranteed perfection.

---

## 4.6 CivitAI fetch downloads previews, but details are weak or partial

### Why this happens
Remote sources are not always equally rich for every model/version.
Some entries provide better prompts, notes, or trained words than others.

### What to do
- use fetched previews even if the text fields are weak
- import only missing fields if that is safer
- manually review before overwriting good local metadata

### Best practice
Remote import should enhance your entry, not blindly replace your better local/manual data.

---

## 4.7 Output Inspector works, but recovered prompt is messy

### Why this happens
Recovered metadata is often useful, but not always clean.
It may include:
- bloated phrasing
- mixed formatting styles
- extra metadata noise
- awkward ordering

### What to do
- use the clean rebuild option if available
- send the recovered prompt into Prompt Studio or Prompt Composer
- run Prompt QA / cleanup on it
- save only the cleaned version that is worth reusing

---

# 5. Import / export issues

## 5.1 Import did not behave the way I expected

### First question to ask
Which import mode did you use?

- **Merge**
- **Overwrite**
- **Skip duplicates**

These do different things.

### Quick meaning
- **Merge**: keep existing items and add new ones, renaming incoming conflicts if needed
- **Overwrite**: replace matching items
- **Skip duplicates**: leave matching items alone and import only non-duplicates

### Best practice
If you are unsure, export a backup first and use **Merge** on a test import.

---

## 5.2 Imported library looks incomplete

### Common causes
- exported pack did not include that section
- category filter limited the export
- assets were not packaged the way you expected
- you imported into a different path/library root than expected

### What to do
- check export settings from the original pack
- verify selected categories
- verify the pack actually contains the expected folders/files
- confirm the active library path in the new install

---

## 5.3 I am scared of losing my saved data

### Good. You should be a little scared.
That fear keeps backups alive.

### Best practice
Before:
- large imports
- category cleanup
- path changes
- reinstall/migration
- code experiments

always export a backup first.

---

# 6. Model and backend confusion

## 6.1 Do I need one model or two?

### Short practical answer
- one multimodal model = simpler setup
- separate captioning + prompting models = cleaner specialization

If your machine can handle it, a split setup is often better long term.

---

## 6.2 How do I know if my model needs `mmproj`?

### Rule of thumb
If it is a multimodal / vision-capable GGUF and the model page includes a separate `mmproj`, assume you need it for image tasks.

If you skip it, image understanding may fail or behave badly.

---

## 6.3 The model is loaded, but everything is too slow

### Common causes
- model too large
- quant too heavy
- hardware mismatch
- trying to use one giant model for everything

### What to do
- move to a lighter quant
- try a split model setup
- test smaller jobs first
- use a model that fits your actual machine, not your aspirational machine

---

# 7. Workflow confusion

## 7.1 When should I save a Prompt vs a Bundle?

### Save a Prompt when
- the text itself is what matters
- you want a reusable prompt record
- the setup is lightweight

### Save a Bundle when
- the full generation setup matters
- you want to keep prompt + LoRAs + defaults + notes + reference together

### Where Bundles live
Bundles belong in **Neo Library**, because they are generation-facing reusable setups.

---

## 7.2 When should I save a caption as a component?

Save it as a component when the caption is useful as a modular prompt part, such as:
- face
- person / character
- outfit
- pose
- location

If it is just a weak general caption you will never reuse, do not force it into the system.

---

## 7.3 Why not save everything?

Because a library full of junk becomes hard to trust.
Save the things that are:
- reusable
- instructive
- high-quality
- worth finding later

---

# 8. If something still feels broken

If the issue still does not make sense, check in this order:

1. backend state
2. model type
3. `mmproj` requirement
4. paths and saved-data location
5. recent code changes
6. UI refresh / restart needs
7. console traceback or error logs

If there is a traceback, keep it.
That is usually more useful than “it broke somehow.”

---

# 9. Final advice

Neo Studio Suite works best when you treat it like a structured workflow, not a magic box.

When something goes wrong, usually one of these is true:
- the backend is wrong
- the model is wrong
- the paths are wrong
- the UI is stale
- the workflow was pushed too hard before testing small

Start small, test cleanly, save backups, and read the actual error messages.
They are annoying, but they are usually telling you where the problem lives.

---

# Continue reading

After this file, also check:

- `INSTALLATION.md`
- `MODEL_GUIDE.md`
- `NEO_LIBRARY_GUIDE.md`
- `NEO_STUDIO_GUIDE.md`
- `CHANGELOG.md`
- `ROADMAP.md`

