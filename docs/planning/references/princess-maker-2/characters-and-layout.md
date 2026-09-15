# PM2 Characters, Visual Design and Layout (캐릭터 디자인 및 레이아웃)

Who's in the game and what role each character plays, how the main screen
is laid out, and how the daughter's appearance communicates her state.

The wiki's screenshots couldn't be retrieved (see [`README.md`](README.md#sources-and-caveats)),
so layout here is reconstructed from the wiki's text descriptions, not from
looking at the screens.

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

From the wiki's interface tour, which lists the main screen's elements but
not their exact placement. The main screen shows the daughter herself (she
visibly changes with status and vanishes when she runs away), an information
panel, and command buttons.

| Area | Contents |
|---|---|
| Personal information panel | Name, age, blood type, zodiac sign, equipment icons (weapon, armor), three status-effect boxes, body measurements, money |
| The daughter | Drawn on the main screen; changes with status and outfit (see below). Disappears when she has run away. |
| Command buttons (in the tour's order) | **Status** (top-left; stats and skills) · **Interact** (talk / pocket money / scold) · **Diet** (4 options) · **Personal info** (in-depth screen) · **Town** (armory, tailor, church, pawn shop, restaurant, hospital) · **Castle** (palace talk) · **Inventory** · **System** (star icon: save / load / quit). The tour doesn't cover the schedule command, though Cube runs the monthly schedule. |
| In-depth personal screen | Age, blood type, sign, measurements, Renown; sickness % and delinquency % |

Other screens described on the wiki:
- **Schedule scenes:** each class/job slot plays as a short animated scene of
  her at the activity, with per-day success or failure shown (e.g. her
  failing at the bar, being unable to keep up in dance class, the boss
  turning her away).
- **Errantry:** a region map where the player walks her around, with an
  adventure-selection button per region, camp scenes and battle screens.
- **Event scenes:** illustrated visits (fairy tea party, rival meeting,
  suitors, visitors at the door) with dialogue.
- **Ending:** a stat roll, the ending illustration and text, the patron
  deity's comments and the final score.

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
