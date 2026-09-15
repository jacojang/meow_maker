# PM2 Characters, Visual Design and Layout (캐릭터 디자인 및 레이아웃)

Who's in the game and what role each character plays, how the main screen
is laid out, and how the daughter's appearance communicates her state.

Layout details come from two sources: the wiki's text descriptions (its own
screenshots couldn't be retrieved), and screenshots of the **Regeneration**
remake (2024, Korean Nintendo Switch version) in a
[Naver blog post](https://m.blog.naver.com/114632/223503790979) that were
viewed directly. Each point below says which source it comes from. The
original DOS/PC-98 screens may differ in detail. Images are not stored in
this repo because they're third-party copyrighted material.

## Core cast

| Character | Role | Design notes from the wiki |
|---|---|---|
| **The daughter (Olive)** | The raised character. Descends from heaven in an orb of light; otherwise fully human. Player picks her name and birth date. | Long, brown, curly hair; brown eyes. "Official" outfit is a pink dress with a red bow on the chest. Designed to look distinct from the first game's daughter. |
| **The player (the Swordsman / father)** | Hero who defeated Lucifon; lives on a royal stipend. Never shown on screen, even in his own ending. | Characterized only through dialogue (townsfolk expect a lot from "the hero's daughter"). |
| **Cube** | Butler. A demon nobleman serving the player. The in-game guide: manages the schedule and diet, warns about weather, announces visitors, accompanies her to the festival, rescues her in errantry, nurses her when sick, supervises her when delinquent. Hidden relationship stat; marriage candidate. | Dark-skinned, youthful-looking demon. Became the series' recurring steward. |
| **Patron deity** | Chosen by birth date. Appears when saving, when the inventory is full, and to judge the ending. | One of 10 planetary gods (see [`status-system.md`](status-system.md#starting-stats-by-patron-deity)). |

## NPC roster by function

The wiki groups PM2's cast by what they *do* for the loop — a useful template
for planning a supporting cast.

| Group | Members | Function |
|---|---|---|
| Palace folk | Guard, Royal Knight, General, Minister of State, Archbishop, Royal Concubine, Queen, King, Young Officer (the Prince), Court Jester | Monthly Renown conversations gated by Decorum; each represents a career she can end up in |
| Townsfolk / shopkeepers | Zen (armory), Maura (tailor), Shalom (pawn shop), Balbon (restaurant), Sister Lee (church), Dr. Lombardini (hospital) | Town menu services |
| Teachers | Tobi (dance), Leftor (fencing), Carl Fox (fighting), Putnam (magic), Filkins (painting), Comstock (poetry), Bartholomew (protocol), Barcleo (science), General Kruger (strategy), Sister Lee (theology) | One per class; several reappear as contest judges or contestants |
| Job bosses | Cube, Radania, Sister Lee, Bongor, Deginzi, Balbon, Hoss, Sara, Toscal, Ko, Baran, Dimitri, The Countess, Sam, Baron Tellmark | One per job; shown in work scenes and when turning her away |
| Rivals | Anita (fighter), Wendy (mage), Patricia (socialite), Marthia (cook) | Same-age girls who each mirror one reputation; also work in town |
| Admirers | Flirty Punk, Suitor, Dirty Old Man | Charisma/Refinement-triggered temptations and proposals |
| Fighters and bandits | ~15 named tournament fighters; bandits Venezaro, Bloodrose Vanesta, Hurricane Castio | Combat challenges with escalating stats and bounties |
| Supernaturals | Patron gods, War God, Lucifon, Valkria, Fay, Paimon, Domovoi, P.D. Karl, fairies, dragons, Ket Shi, mermaid, unicorn, tree elf, Spirit of the Spring, Bird of Paradise, Skeleton Knight | Stat-gated visits that grant, trade or take away stats |
| Other | Civilians met on errantry, Fortune Teller, Traveling Salesman | Flavor, foresight, rare items |

Character-writing patterns:
- **Cube carries all tutorial and system messaging in character** (each job
  and class has a one-line Cube description, e.g. *"Help out on the farm on
  the edge of town."*). There's no separate narrator UI.
- **Rivals have short, strongly typed voices** (Anita taunts, Patricia
  mocks, Marthia is shy, Wendy is polite) that make each reputation feel like
  a personality.
- **Civilians have 3–5 rotating one-liners** each, which also leak gameplay
  hints ("Monsters to the east of the castle aren't that bad...").

## Main screen layout

Composition as seen in the Regeneration screenshots (proportions approximate):

```
┌──────────┬───────────────────────────────┬────────────────┬──────────────┐
│ 1210     │                               │ Name / surname │ General      │
│ May 5    │                               │ AGE · STAR ·   │ stats (10)   │
│ tue   4  │   Room background             │ GOLD           ├──────────────┤
├──────────┘   (bed, window, flowers,      │ status/equip   │ Combat /     │
│               wall pictures)             │ boxes          │ magic (6)    │
│                                          │ diet text      ├──────────────┤
│              Daughter — full-body        │ body measures  │ Reputations  │
│              standing sprite             │ command icons  │ (4)          │
│                                          │ [ SCHEDULE ]   ├──────────────┤
│  ┌─────────────────────────┐             └────────────────┤ Housework /  │
│  │ Cube's dialogue  [face] │                              │ social (6)   │
│  └─────────────────────────┘                              │              │
└───────────────────────────────────────────────────────────┴──────────────┘
```

| Area | Contents | Source |
|---|---|---|
| Date box (top-left) | Year (e.g. 1210), month name and number, weekday, and a large day number | Screenshots |
| Room + daughter (center) | Bedroom background with the daughter as a full-body standing sprite. Her sprite shows the equipped outfit (default pink dress; a teal dress in an age-13 save). She visibly changes with status and vanishes when she runs away. | Screenshots; status changes from the wiki |
| Profile panel (upper right of the room) | Given name and family name; AGE; STAR (zodiac icon); GOLD; a row of small status/equipment boxes; current diet as a phrase ("무리하지 않는다"); body measurements (height, weight, bust/waist/hip, e.g. `151 43 75/56/78`); a row of pictorial command icons; a large **SCHEDULE** button | Screenshots |
| Stat column (far right, always visible) | Four panels of labeled red gauge bars with numbers. Korean labels: **General** 체력·근력·지능·기품·매력·도덕성·신앙·업보(Sin)·감수성·스트레스 / **Combat** 전투기술·공격력·방어력·마법기술·마력·항마력 / **Reputation** 전사평가·마법평가·사교평가·가사평가 / **Skills** 예의범절·예술·화술·요리·청소세탁·성품 | Screenshots |
| Dialogue box (bottom-left) | Cube's lines with his face portrait beside the text (e.g. the morning greeting "Good morning, Master. It is I, your butler, Cube.") | Screenshots |
| Commands | The wiki's tour lists, in order: **Status** (top-left button), **Interact** (talk / pocket money / scold), **Diet** (4 options), **Personal info** (in-depth screen with Renown, sickness % and delinquency %), **Town** (armory, tailor, church, pawn shop, restaurant, hospital), **Castle** (palace talk), **Inventory**, **System** (star icon: save / load / quit). In the screenshots these are the pictorial icon row plus the separate SCHEDULE button; the star icon is visible, but the other icons can't be matched to commands from the images alone. | Wiki + screenshots |

Design takeaway: the full stat sheet stays on screen at all times, so the
player watches numbers move without opening a menu, while the center of the
screen is given to the character art.

## Other screens

**Schedule execution** (screenshots). A window overlays the room while a slot
plays out day by day:
- Top-left: a running money box — "사용금액 60G" (amount spent) for a class,
  "수입 10G" (income) for a job.
- Center: a small animated panel of the activity (a classroom with a teacher
  at the blackboard; a farm with the farmer and a windmill).
- Right: a text box with the activity, the day count and a one-line result,
  e.g. "자연과학 3일째 / 서서히 성과가 나오고 있습니다." ("Science, day 3 /
  results are slowly showing"), "농장 2일째 / 오늘은 농장에서 실수를 한 것
  같다…" ("Farm, day 2 / she seems to have made a mistake today").
- Bottom: two small panels with only the gauges this activity changes
  (e.g. Intelligence/Faith and Magic Defense/Stress for Science;
  Constitution/Strength and Refinement/Stress for the farm). The date box and
  the right-hand stat column update as the days tick by.
- Per the wiki, failures and refusals are shown too (failing at the bar,
  unable to keep up in dance class, the boss turning her away).

**Battle** (screenshots + wiki). Inside an ornate frame, a large enemy sprite
sits over the dungeon map. The top-right box shows the date, her current HP
and MP and gold, plus equipment icons. Along the bottom: the enemy's panel
(name, HP, MP, 전사평가, 마법평가, 전의/morale gauges), a message box ("전투
개시" — battle start) and the daughter's matching panel. A small command
menu offers Attack and Magic (a third option isn't legible in the screenshot).
The right-hand stat column stays visible.

**Errantry map** (wiki). A region map where the player walks her around,
with an adventure-selection button per region and camp scenes.

**Events and vacations** (screenshots + wiki). A full-width illustration
(mountain meadow, swimming in the sea, a forest) replaces the room, with the
date box still shown. A small overlay shows only the stats being changed
(e.g. 스트레스 2 / 감수성 30). Visitor events use illustrated scenes with
dialogue (fairy tea party, rival meeting, suitors).

**Palace and festival** (small trailer frames only, so details are
uncertain). What appears to be the palace places a small daughter sprite in a
large hall background; what appear to be festival scenes use ornate frames
with several characters lined up.

**Ending** (wiki + screenshots). A stat roll, then a full illustration of her
in the career's outfit (the post compares the Archbishop, Soldier and Royal
Guard Officer illustrations between the original and Regeneration), the
ending text, the patron deity's comments and the final score.

**Regeneration additions** (screenshots). The remake redraws the art and adds
animated cutscenes for raising scenes, plus a gallery menu for past
illustrations, endings and vacation scenes.

## How the daughter's appearance communicates state

A major PM2 design choice: most state is visible on the main portrait, so
the player notices problems without opening menus.

| State | Visual signal |
|---|---|
| Age | Wiki screenshots are captioned by age (10, 11, 12, 13, 17), which suggests age-specific art; the wiki doesn't describe this explicitly. |
| Outfit | The equipped dress is drawn on her; seasonal and special dresses are visible choices. |
| Sick | Sick portrait; a separate **bedridden** portrait above 90% sickness. |
| Delinquent | Delinquent portrait (rebellious look), plus a "caught wasting money" scene. |
| Overweight | No status icon — her sprite visibly becomes heavier. |
| In Love | A "LOVE" icon appears in her status box; a daydreaming scene. |
| Runaway | She's missing from the main screen for the month. |
| Charisma is her highest stat | Has a visual indicator (the wiki notes Sensitivity being highest has none). |
| Arrested | Arrest-and-release scene. |

## Clothing

Dresses are both a visual customization and a stat system.

| Dress | Where | Price | Effect | Restrictions |
|---|---|---|---|---|
| Plain Dress | Starting outfit | 10 G | None; can't be sold | None |
| Summer Dress | Tailor | 70 G | Protects Constitution in heat waves; stress −5 when used | None |
| Winter Dress | Tailor | 120 G | Protects Constitution in cold waves; stress −5 when used | None |
| Cotton Dress | Tailor | 500 G | Refinement +15; valid for the Dance Party | No weight limit |
| Silk Dress | Tailor | 2000 G | Refinement +40 | Age 13+, weight limit |
| Leather Dress | Tailor | 3000 G | Charisma +50, Morality −20; best Dance Party dress | Age 14+, weight limit |
| Spikey Dress | Tailor | 2800 G | Sensitivity +40, Morality −30 | Age 13+, weight limit |
| Demon Dress | Rare drop from desert demons | (worth 3000 G) | Charisma +45, Morality −100 | Age 14+, weight limit |
| Dragon Tights | Old Dragon gift | (worth 1200 G) | Charisma +28, Magic Defense +12 | Age 15+, weight limit |
| Siren Robe | Traveling Salesman | 4000 G | Charisma +40 | No weight limit |

General rules: most dresses need age 13+ and all can be worn at 15+; being
overweight locks out most stat dresses; the Dance Party requires a dress
other than the Summer/Winter dress.
