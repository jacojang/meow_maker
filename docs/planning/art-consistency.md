---
status: review
updated: 2026-10-02
---

# Art consistency (cat identity, framing, pipeline)

Request: Type: modify. Name: art consistency. User report: "the images are not consistent at all; how can we fix it?"
Design: [`../design/art-consistency.md`](../design/art-consistency.md). Asset rules: [`feature-backlog.md`](feature-backlog.md#asset-generation-policy-applies-to-every-slices-design-doc).
Nothing in this plan runs `tools/asset-gen`. Every batch needs the user's go-ahead with the prompt shown first (AGENTS.md).

## Goal

The player should see one recognizable cat across the portrait panel, every
activity scene and the opening. Today the cat changes face, markings, eye
color and even drawing style from image to image. Fix that without wasting
generation budget, and make the result checkable so it does not drift again.

## Scope

**In**

- Zero-cost code fixes for portrait size, foot line, age scale and grounding.
- A locked anchor (identity + style) and a written style/scene spec.
- Pilot-gated regeneration of the 12 portraits, then the 30 scene frames.
- A reusable measurement and contact-sheet script, and a provenance record.

**Out**

- Editing or deleting shipped asset files during planning. Regeneration replaces files only in the coding stage.
- New game mechanics. New assets from other slices (bedridden/delinquent portraits, job scene, festival art) follow this slice's template and are listed in Open questions only.
- Seasonal backgrounds beyond a low-priority option (they are already structurally consistent).

## Verified facts

Checked on the files and code, not taken from the critic's report.

| Claim | Result |
|---|---|
| 12 portraits differ in look | True by eye. The kitten-healthy-normal portrait is painterly with brown eyes; kitten-healthy-chubby has yellow-green eyes; the rest are flat cel with yellow eyes. Sick variants have rougher, greyer fur and different face masks. Spot count and position vary (adult-healthy-chubby has almost no spots; adult-healthy-normal has a long black saddle). |
| Portrait bbox height 0.76 to 0.98 | True. Measured with Pillow (alpha > 20, 640x640): range 0.76 (kitten-sick-chubby) to 0.98 (young-healthy-chubby). Adult-healthy-normal 0.94, kitten-healthy-normal 0.91. |
| Foot line varies | True. Bottom edge of the cat sits at y = 555 to 628 across the 12 files. |
| Why it shows in game | `GameScene.js` places the image with origin bottom-center on the panel floor (`PORTRAIT_GROUND_MARGIN` 6, `PORTRAIT_SCALE` 0.4), i.e. it aligns the file edge, not the paws. So the paws float up to about 13% of the image height (555 vs 640) depending on the file, and the cat jumps when its state changes. Horizontal centering is also by file, not by cat (bbox centers range about 299 to 364 px). I could not take an in-game screenshot, so the visual effect is inferred from the code and numbers. |
| Age scale not visible | True. The kitten (0.91) and adult (0.94) heights are almost equal. The stage thresholds are in `web/src/utils/portrait.js` (kitten age <= 4, young <= 8, adult after). |
| Scene cats differ from Mimi and from portraits | True by eye. Play and train frames show big heart-shaped spots; educate shows a mostly black face with a white muzzle; groom shows a black saddle; outing shows a smaller cat with a harness. Within one activity the spots move (play-d has almost none). |
| Scene framing and background differ | True by eye. Play and outing are full-figure; groom and rest are close-ups; the human's face size varies about 3x. Background tone is grey-beige, peach, pink-beige or yellow cream depending on the activity. |
| Human is mostly stable | True. Striped tee, navy trousers, long brown hair across the 30 frames. Hair is slightly lighter in `opening-background.jpg` than in `mom_of_cats_01.png`. |
| Seasons: same composition, different color treatment | True. Four 800x533 files with identical composition. Spring is washed pink, autumn heavy orange, winter nearly grey, summer crisp. |
| Model description mismatch across docs | Partly. `tools/asset-gen/README.md` and `generate_image.py` agree: default `gpt-image-1-mini`, quality `low`. `calendar-and-motion-overhaul.md` describes an earlier default (`gpt-image-2.5-flare`) and one `gpt-image-1` override. That is history, not a conflict, but nothing records which model and refs made each shipped file. |
| asset-gen has no consistency device | True. Flags are prompt, repeatable `--ref`, size, background, model, quality. No style template, no check, no record. |

Anchor candidates (opened, compared and measured):
- `docs/design/character_and_background_samples/cat_mimi_01.png`: six-view sheet, 896x1195. Clear markings: black cap over head and ears with a white blaze, large black side patches, black tail, white chest, legs and paws. Realistic proportions and thin lines, not the game's cel style. Each view is small inside the sheet (front view about 150x390 px, side views about 400x250 px). Eye color is not clearly yellow; it reads olive-grey.
- The cat in `web/public/assets/opening-background.jpg` (1536x1024 JPEG): same markings, in the flat cel style the game uses. Cropped by me to check: the cat is about 465x370 px (the critic guessed the 300s; it is larger, but still low resolution, and JPEG-compressed). Eyes are closed, the pose is a side-facing sit with the head raised, and the human's fingers touch the cheek at the crop's right edge. Not a usable game pose.
- `mom_of_cats_01.png`: standing front view of the human on grey. Usable as the human ref.
- Neither cat anchor is in a pose the game needs (sitting, front to three-quarter, eyes open). Giving a realistic-style sheet and a cel-style crop together can make the model blend the two. That may explain the painterly `cat-kitten-healthy-normal`; I could not prove it, it is a hypothesis.

## Decisions on the critic's report

| # | Point | Decision | Reason |
|---|---|---|---|
| 1 | Portraits differ in markings, eyes, style | adopt | Verified by eye. It breaks the "my cat grows up" feeling. |
| 2 | Portrait size and foot line vary; ages not scaled | adopt | Measured. Fixable in code with zero calls. |
| 3 | Scene cats differ from Mimi and portraits | adopt | Verified by eye. Needs regeneration or separation. |
| 4 | Scene framing, human size, background differ | adopt | Verified. Needs one scene spec, applied at regeneration. |
| 5 | Human mostly stable | adopt | No action on the human. Only pin a human ref for regenerated scenes. |
| 6 | Seasons: tint from one original | adapt | Composition is already consistent. Tinting cannot make blossoms or snow, so tint-from-one is rejected. Keep the files. A grounding shadow in code is added (free). Optional low-priority regeneration. |
| 7 | Opening as anchor basis | adopt | It is the in-game style with the right markings. Use it together with the sheet. |
| 8 | Pipeline lacks anchor, spec, checks | adopt | Confirmed. Add template, provenance, script. |
| root | Cheap model causes drift | adapt | Plausible, unproven. The pilot decides on measured results rather than assuming. |
| root | Chaining and no anchor | adopt | Matches the calendar-and-motion record. |
| A | Anchor sheet + full regeneration | adapt | Adopt, but pilot-gated and split into portraits then scenes. Not one big batch. |
| B | Separate cat from scenes | adapt | Portraits are already a separate sprite. For scenes it is not cheaper (30 human-only scenes plus 12 to 15 cat poses). Contact poses (grooming, lap, leash) overlap badly. Test it on non-contact activities only, if the pilot suggests it. |
| C | Code post-processing | adopt | First step. Done at runtime from measured metrics, so shipped files are not edited. |
| B/C | 12 portraits to 1 to 3 anchors by stretch and tint | reject | Chubby and sick are different drawings (expression, fur, posture). Stretch and tint will look wrong. Pilot may try stretch for chubby as a cost lever only. |

### Round 3 (critic review of this plan)

Agreed by both sides, no change: option B out of the default, the AC order (AC-1 with no calls, then the pilot, portraits, scenes),
no silent pricier-model fallback, seasons keep their files with only a shadow added (the first-round "tint from one original" is withdrawn).
The one-hop frame ref is accepted on conditions (see AC-4).

| # | Point | Decision | Reason |
|---|---|---|---|
| core | Dual anchors of different styles, neither a game pose | adopt | Verified above. Make one formal anchor first (AC-2a). |
| 1 | AC-2a: one proper anchor, approved by the user, then the only cat ref | adopt | Removes the style-mixing risk from every later call. Eye color is fixed here. |
| 2 | Lock one pose for all 12 portraits | adopt | Only expression and body type change. Pose shows tail and body patch. |
| 3 | Pre-register pilot pass numbers | adopt | Written below before any run, to stop after-the-fact rationalizing. |
| 4 | Pilot scenes: static, dynamic and contact; failure plan | adopt | Educate is the easiest case, so it alone proves little. |
| 5 | 5 frames per call as a pilot option | adopt | Could cut 30 calls to 6 to 12. Resolution and cell alignment risks are tested. |
| 6a | Approximate identity metrics | adapt | Advisory only, calibrated in the pilot, never the sole gate. |
| 6b | Embedding similarity | adapt | Not used (user decision). |
| 6c | Reviewer pass on the contact sheet, recorded in provenance | adopt | Independent look. Verdict stored. |
| 6d | Metrics JSON staleness test | adopt | Content hash, not mtime. Fails loudly. |
| 6e | AC-1 browser check, 12 states x 4 seasons | adopt | In the AC-1 acceptance. |
| 7 | Stage heights are provisional | adopt | Old-file values. Final after AC-3. Identity ranks above size. |
| 8 | Master storage and halo test | adopt | Masters are committed (user, Round 6). Halo test is an AC-3 acceptance. |
| 9 | Include bedridden and delinquent portraits in AC-3 | adopt | Later generation would drift again. Confirmed by the user. |
| misc | Chubby wording | adopt | Same target height, uniform scale only, never a stretch. |
| misc | Groom and rest crop | adopt | Own allowed crop. Groom joins the pilot. |
| misc | `gpt-image-1` medium control | adapt | Not done (user decision). |
| misc | Call cap and money cap | adopt | Both are requested from the user. |

## Options compared

| | A: anchor + regenerate | B: separate cat sprites in scenes | C: code post-process |
|---|---|---|---|
| Fixes portraits identity | yes | already separate | no |
| Fixes portrait size and floor | partly | n/a | yes |
| Fixes scene cat identity | yes, if refs hold | yes (one cat source) | no |
| Keeps interaction (petting, brushing, leash) | yes | weak | n/a |
| Asset-gen calls | 51 base, about 75 to 100 with retries (incl. pilot) | 30 human scenes + 12 to 15 sprites, not cheaper | 0 |
| Risk | markings drift at mini model | cut-out look; lost charm | none for identity |

Call counts are my estimates. Per-call price at `medium` on `gpt-image-1-mini` is not known to me; the user sets the budget (Open questions).

## Mechanics (slices, in order)

**AC-1 Measure and align (code only, 0 calls)**
- A Pillow script measures every portrait (alpha bbox, foot line, center) and writes a metrics JSON that also stores each file's content hash. It is the first piece of the reusable check tool.
- Client: a Phaser-free helper in `web/src/utils/`, Vitest-tested, places each cat by its paws and bbox center with a target height per age stage. A Vitest test fails if any listed file's hash differs from the metrics (no silent fall back to the old placement for a stale entry). Runtime falls back to today's placement only for textures that are not listed (for example optional portraits not yet made).
- Stage heights relative to adult: kitten 0.55, young 0.75, adult 1.0. These are provisional values based on the old files. Final values are set after AC-3.
- Chubby uses the same target height as the other body type. Scale is uniform. The code never stretches a sprite in one direction.
- A soft ground-shadow ellipse under the cat.
- Acceptance: build and Vitest pass, and a browser pass over all 12 portrait states in all 4 seasons shows no jump, no floating, no clipping. Does not touch asset files.

**AC-2a Formal anchor (about 3 to 6 calls; the prompt is shown before running and the user picks the take)**
- Failure rule: at most 6 calls. If no take is acceptable by then, stop and ask the user (change the prompt or refs, raise quality, or hold). No automatic extra retries and no silent model change.
- One cat, game cel style, eyes open, seated three-quarter view (body turned about 30 to 45 degrees so the side patch and the tail show, head toward the viewer, both front paws visible), transparent background, size 1024. Inputs: the sheet for markings and the opening crop for style.
- Quality: `high` for this one image only (user decision), because everything later depends on it.
- The user picks the take. Eye color is fixed here. From then on the only cat ref for any generation is this anchor. The sheet and the opening crop are no longer refs.
- The 1024 master is kept (see Master storage).

**AC-2 Pilot (about 12 to 16 calls; each batch's prompt is shown before running)**
Setup: `gpt-image-1-mini`, `--quality medium`, refs = the anchor (and the human ref for scenes), never an earlier output.

Pass criteria, registered before any run:

| # | Test | Pass |
|---|---|---|
| P1 | adult-healthy-normal, 3 tries | at least 2 of 3 pass the full portrait checklist |
| P2 | kitten-healthy-normal and young-sick-chubby, up to 3 tries each | each gets at least 1 pass; the 3 passing portraits on one contact sheet are judged "the same cat" by the user and by the reviewer agent |
| P3 | transparency | corners are fully transparent in at least 90% of tries, and the halo test passes on the 4 season backgrounds plus a magenta one |
| P4 | scenes, frame A only: educate (static), play (dynamic), groom (contact), up to 3 tries each | at least 2 of the 3 activities get a pass on the scene checklist (cat identity, human outfit, framing, background) |
| Go | overall | P1 to P3 pass and P4 passes |

Also in the pilot (selection, not pass/fail):
- Sheet method: generate a 3x2 grid of 512 px cells (one call at 1536x1024 yields the 5 frames of an activity plus a spare cell), then crop. Test on play, 1 to 2 calls. Checks: cell alignment, cat identity across cells, and the upscale from 512 to 640. If it works it cuts the 30 scene calls to about 6 to 12 plus retries.
- One `low` versus `medium` comparison on adult-healthy-normal.

Call cap: the pilot cap is 16 calls. The worst case adds up to about 20 (P1 3, P2 up to 6, P4 up to 9, sheet method 1 to 2, `low` comparison 1). The run stops at the cap and asks the user whether to continue, in the same way as for a failure.

If the pilot fails:
- Portraits: report the numbers and ask the user how to proceed (prompt or ref changes, a different model for that class, or hold). No silent fallback.
- Scenes: all stay on option A (option B is off by user decision). Report and ask, including whether to try a different model for the failing class.

**AC-3 Portraits (12 base, about 18 base with the 6 extras; roughly 27 to 36 with retries)**
- All 12 generated from the anchor. Same seated pose in all, with healthy, sick and chubby changing only expression, ears, fur roughness and body width.
- In the same batch: 3 bedridden and 3 delinquent portraits from the S3 asset list (user decision), so they match the rest.
- Transparent PNG; the 1024 master is kept, the shipped file is 640x640.
- Acceptance: checklist, script, halo test on 4 season backgrounds and magenta, reviewer pass on the contact sheet recorded in provenance, then metrics regenerated (the hash test goes green) and stage heights finalized.
- Tolerances: identity ranks above size. The code normalizes height and foot line, so generation-stage bbox tolerance is loose.

**AC-4 Scenes (30 frames)**
- Option A, per frame: frame A from the anchor plus the human ref. Frames B to E use the anchor and the approved frame A together, only after frame A is accepted by eye, and never a B to C chain. (One-hop exception, conditional.)
- If the sheet method passed the pilot: 1 to 2 calls per activity, about 6 to 12 calls plus retries (about 9 to 18). Otherwise 30 base, about 45 to 60 with retries.
- Option B is off. Every activity, contact or not, is generated with option A.

**AC-5 Seasons**: not done (user decision). The season files stay; AC-1 adds the code shadow only.

Order rationale: portraits are on screen every turn, scenes only during resolution; so AC-1, AC-2a, AC-2, AC-3, then AC-4.

**Call estimates (mine, no price known)**

| Step | Calls |
|---|---|
| AC-1 | 0 |
| AC-2a | 3 to 6 |
| AC-2 pilot | 12 to 16 |
| AC-3 | about 27 to 36 |
| AC-4, per-frame | about 45 to 60 |
| AC-4, sheet method | about 9 to 18 |
| Total, per-frame | about 87 to 118 |
| Total, sheet method | about 51 to 76 |

Per-call price is not known to me. The user said not to worry about cost; these numbers are guardrails. Reaching a cap stops the run and asks the user.

## Verification

- **Automated (script in `tools/asset-gen`, reused for every batch)**: portrait bbox and foot line (loose at generation, strict in the final check); scene non-background bbox per frame against the activity median (the earlier numpy method; crouching poses shrink the box, so eyeball outliers); border-color tone against the scene spec; transparent corners and edge halo, tested on the 4 season backgrounds and a magenta one; size and format; metrics hash staleness.
- **Advisory identity metrics** (calibrated in the pilot, never the only gate): black-fur area ratio inside the cat mask, color distribution of the head region, color distance of an eye sample.
- **Identity by eye.** The script builds contact sheets (12 or 18 portraits on neutral grey, a 6x5 scene sheet). The reviewer agent looks at each sheet once, and the verdict is written to the provenance record.
- **Eye checklist per image** (yes/no): black cap and ears with white blaze, spot count and place, black tail, eye color, pink nose and inner ears, flat cel line style, the locked pose, stage proportions; for scenes also the human outfit, framing and background tone. Any "no" means regenerate, at most two retries, then ask the user.

## Master storage

- Decision: masters are committed. Location: `tools/asset-gen/masters/<asset-name>.png`, one file per approved asset, 1024 px PNG (transparent for cats). The hashes are also listed in `docs/design/asset-provenance.md`.
- Size policy:
  - Commit only the approved take. Rejected tries are not committed.
  - Git history keeps every replaced version, so repository size only grows. Rough size: 18 portraits at about 1 to 2 MB plus 30 scene frames at about 2 to 3 MB as PNG, about 100 to 130 MB if scenes are PNG. Avoid committing more than one revision per asset.
  - Proposal only: opaque scene masters could be 1024 JPEG at quality about 92 (about 0.2 to 0.4 MB each), which cuts the total to about 30 to 40 MB. Portraits stay PNG because of transparency. Default stays 1024 PNG until the user says otherwise.
  - The anchor and the 12 to 18 portrait masters matter most. Scene masters are the first candidates to slim down if size becomes a concern.
- `.gitignore` must not exclude this folder. Shipped files in `web/public` stay 640 px.

## Decisions (user, resolved)

| # | Topic | Decision |
|---|---|---|
| 1 | Cost | Do not worry about cost. The call counts in this doc are guardrails only: a run that reaches its cap stops and asks the user. `asset-gen` runs are approved by the user; the rule of showing each batch's prompt before running stays. |
| 2 | AC-2a quality | `high` for the single anchor image. |
| 3 | Masters | Committed to the repo, not a local gitignored folder. Location and size policy: see Master storage. |
| 4 | Control model | No `gpt-image-1` control calls. |
| 5 | Anchor | Made new from the sheet plus the opening crop. Then only that result is a cat ref. |
| 6 | Eye color | Decided from the AC-2a takes. Default yellow. |
| 7 | Frame refs | Frames B to E use the approved frame A plus the anchor (one hop, never chained). |
| 8 | Option B (separate cat in scenes) | Off. All scenes use option A. |
| 9 | Human hair | The dark brown of `mom_of_cats_01.png`. |
| 10 | Scene spec | Confirmed: flat cream background, at least 5% margin, human head about 14 to 18% of frame height, medium line weight. Groom and rest may use a tighter crop (about 22 to 26%). |
| 11 | Extra portraits | Bedridden and delinquent portraits are in the AC-3 batch. |
| 12 | Embedding similarity | Not used. |
| 13 | Seasons | AC-5 not done. Only the code shadow in AC-1. |

## Open questions

None for the user. Pilot results and the AC-2a take will come back to the user for approval at the points defined above (cap reached, failure, anchor pick).

## Implementation notes (2026-10-02)

Done in one pass, decisions taken without further questions per the user.

- **AC-1** (merged): measurement script, placement helper, ground shadow.
- **AC-2a**: 3 takes at `high`; take 1 chosen (two clearly separated body patches, tail visible, yellow eyes). Stored as `tools/asset-gen/masters/cat-anchor.png`. It is the only cat ref since.
- **AC-2 pilot**: P1 passed (2 of 3; take 3 had a translucent body, `semi_transparent` 0.039), P2 passed, P3 passed (corners alpha 0, semi-transparent ratio under 0.02), P4 passed (educate, play, groom frame A each). The pilot used 16 calls (the cap); the Go conditions were met, so the run continued.
- **AC-3**: 18 portraits (12 base + bedridden and delinquent per age) from the anchor only, `gpt-image-1-mini` at `medium`, 2 takes each; selection and metrics rules in `tools/asset-gen/batch1_selection.json`. Rejected: translucent bodies (`semi_transparent` over 0.02), non-zero corner alpha, face-color drift. Retried: adult-sick-chubby (2 more takes), kitten-bedridden (2 more). Chubby prompt was strengthened after the pilot (more clearly round body).
- **AC-4**: 35 scene frames = 7 activities (play, train, groom, rest, educate, outing, and the new job) x 5 frames. Frame A from the anchor + human ref; B to E from anchor + approved A + human ref (one hop). The sheet method was not used. All frames accepted after eye check.
- **Masters**: committed under `tools/asset-gen/masters/` (portraits as 1024 PNG, scenes as 1024 JPEG q92, about 32 MB). Provenance in `tools/asset-gen/provenance.json`.
- **Rate limit**: the API allows 5 input images per minute for this model; `batch_generate.py` retries and spaces calls by the number of refs.
- **Seasons**: unchanged (AC-5 dropped).
- Stage heights 0.55 / 0.75 / 1.0 are now final; lying poses (bedridden) scale by width.
- Calls used: about 100 (AC-2a 3, pilot 16, AC-3 about 40, scenes about 40).
