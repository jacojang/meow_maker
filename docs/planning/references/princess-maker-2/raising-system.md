# PM2 Raising System (육성)

How the player spends time and money to grow the daughter. Stat definitions
are in [`status-system.md`](status-system.md).

## Monthly schedule

- Each month has **3 schedule slots** (the wiki refers to "all 3 parts of a
  month"). A slot is roughly 10 days; one filled slot is a "session".
- Slot options: **class**, **part-time job**, **errantry** (adventure, see
  [`mini-games.md`](mini-games.md)), **free time**, **vacation**. When sick,
  free time becomes **rest** and vacation becomes **sanatorium**.
- Classes and jobs resolve **day by day**; each day is a success or a
  failure. Vacation effects are quoted as counting Sundays, which implies
  Sundays are off for classes/jobs (not stated explicitly on the wiki).
- The player also gets a **500 G royal stipend per year**, the only income
  besides jobs, contests, errantry loot and a few events.

## Classes (교육)

Pay tuition per day to raise stats/skills, with low stress. Some skills can
*only* be raised through classes.

- **Levels:** Novice → Adept after 6 sessions → Expert after 5 more → Master
  after 5 more. Higher levels cost more and usually raise stats faster.
- **Wasted days:** if she's too stressed or distracted on a day, she gains
  nothing that day but tuition is still charged. (Jobs, by contrast, always
  apply their stat changes.)
- **Rival trigger:** attending any class at age 14 can trigger a rival
  encounter (see [`mini-games.md`](mini-games.md#rivals)).
- The wiki gives no per-day stress numbers for classes.

| Class | Teacher | Tuition/day (Nov/Adp/Exp/Mst) | Per-day effect by level (Nov / Adp / Exp / Mst) |
|---|---|---|---|
| Dance | Tobi | 50 / 70 / 90 / 110 G | Constitution +1 at all levels; Charisma +0–1 / +0–1 / +0–2 / +1–2; Art +0–1 / +1 / +1–2 / +2–3 |
| Fencing | Leftor | 40 / 70 / 130 / 190 G | Combat Skill +0–1 at all levels; Combat Attack +1 / +1–2 / +1–3 / +1–4 |
| Fighting (Kung-fu) | Carl Fox | 30 / 40 / 50 / 60 G | Combat Skill +1 / +1–2 / +1–3 / +1–4; Combat Defense 0 / +0–1 / +0–1 / +0–1 |
| Magic | Putnam | 60 / 70 / 80 / 90 G | Magic Skill +1 / +1–2 / +1–3 / +1–4; Magic Attack +0–2 / +0–3 / +0–4 / +0–5 |
| Painting | Filkins | 40 / 50 / 60 / 80 G | Sensitivity +0–1 at all levels; Art +1 / +1–2 / +1–3 / +1–4 |
| Poetry | Comstock | 40 / 60 / 80 / 100 G | Intelligence +0–1 / +0–2 / +0–3 / +0–4; Refinement +0–1; Sensitivity +1 / +1–2 / +1–4 / +2–5; Art +0–1 |
| Protocol (Manners) | Bartholomew | 40 / 50 / 60 / 70 G | Decorum and Refinement each +1 / +1–2 / +1–3 / +1–4 |
| Science | Barcleo | 30 / 40 / 50 / 60 G | Intelligence +1–4 / +2–6 / +3–8 / +4–12; Faith 0 / −0–1 / −0–2 / −0–3; Magic Defense 0 / −0–1 / −0–1 / −0–1 |
| Strategy | General Kruger | 50 / 70 / 90 / 110 G | Intelligence +1–2 / +2–3 / +3–4 / +4–5; Sensitivity −0–1; Combat Skill +0–1 |
| Theology | Sister Lee | 40 / 60 / 80 / 100 G | Intelligence +1 / +1 / +1–2 / +1–3; Faith +1–2 / +1–3 / +1–4 / +1–5; Magic Defense +0–1 |

Class-specific extras:
- **Painting:** about every 4 sessions Filkins asks her to paint (materials
  100 G). The painting is her Art Festival entry; the painting produced
  depends on her Art at that moment.
- **Fencing:** a random "dojo destroyer" challenger may appear; losing or
  refusing closes the school for several weeks.
- **Magic:** filling all 3 slots of a month with Magic summons Fay, who
  raises one magic skill by 20% of its value.

## Part-time jobs (아르바이트)

Earn money with more stress; most trade one stat for another.

- **Pay only for successful days.** Stat changes and stress apply every day
  regardless of success.
- **Perfect-session bonus:** succeeding on every day of a session pays +50%.
  A single failed day loses the bonus, so a lower-paying job she never fails
  usually beats a higher-paying one she sometimes fails.
- **Raises:** +20% of current wage (min +1 G). The first comes after roughly
  89 successful days; up to 4 raises. Housework never pays.
- **Success** depends on stress and the job's required stats (listed below).
- **Delinquency ≥ ~60%:** every job except Housework and Church turns her away.
- Working a job enough can make it her adult career (see [`endings.md`](endings.md)).

Stat changes are per working day. Pay shows the base wage → the wage after all 4 raises.

| Job | Unlocks at age | Boss | Pay (G/day) | Stat changes per day | Stress per day | Success depends on |
|---|---|---|---|---|---|---|
| Housework | 10 | Cube | 0 | Cooking +0–1, Cleaning +0–1, Temperament +0–1, Sensitivity −2; Father relationship +~0.5% | +1 | Constitution |
| Babysitting | 10 | Radania | 4 → 9 | Sensitivity +1, Charisma −1; Maternal Instinct +~0.5 | +3 | Constitution |
| Church | 10 | Sister Lee | 1 → 5 | Faith +2, Morality +1, Sin −2 | +1 | Constitution |
| Farm | 10 | Bongor | 10 → 21 | Constitution +1, Strength +1, Refinement −1 | +3 | Constitution |
| Inn | 10 | Deginzi | 8 → 17 | Cleaning +0–1, Combat Skill −0–1 | +2 | Constitution |
| Restaurant | 10 | Balbon | 8 → 17 | Cooking +0–1, Combat Skill −0–1 | +2 | Constitution, Cooking |
| Lumberjack | 11 | Hoss | 12 → 25 | Strength +2, Refinement −2 | +4 | Constitution, Strength |
| Salon | 11 | Sara | 20 → 42 | Sensitivity +1, Strength −1 | +3 | Constitution, Sensitivity, Art |
| Masonry | 12 | Toscal | 18 → 38 | Constitution +2, Charisma −1 | +3 | Constitution, Art |
| Hunter | 12 | Ko | 8 → 17 | Constitution +1, Combat Skill +0–1, Refinement −1, Sin +0–1; Maternal Instinct −1 | +3 | Constitution, Intelligence |
| Graveyard | 13 | Baran | 8 → 17 | Sensitivity +1, Magic Defense +0–1, Charisma −1 | +5 | Constitution, Faith |
| Bar | 14 | Dimitri | 12 → 25 | Cooking +0–1, Conversation +0–1, Intelligence −2 | +5 | Constitution, Charisma |
| Tutor | 14 | The Countess | 20 → 42 | Morality +1, Charisma −1; Maternal Instinct +~0.5 | +7 | Constitution, Intelligence |
| Sleazy Bar | 15 | Sam | 45 → 95 | Charisma +2, Sin +2, Faith −3, Morality −3, Temperament −0–1; Father relationship −1% | +12 | Constitution, Charisma |
| Cabaret | 16 | Baron Tellmark | 35 → 70 | Charisma +3, Sin +1, Refinement −2, Intelligence −1, Temperament −0–1 | +8 | Constitution, Charisma, Art |

Notes:
- No job raises Refinement or Intelligence; Housework is the only job that
  raises the father relationship; Church is the only job with no downside.
- Conversation can only be raised at the Bar (plus one supernatural gift).
- Some jobs host a special event (e.g. the Skeleton Knight at the Graveyard
  once Fighter Reputation is ~100; beating him pays 2539 G).
- The overview and individual job pages disagree on some intermediate raise
  amounts; base and max pay above match the individual job pages.

## Stress relief (스트레스 해소)

| Method | Cost | Effect | Side effects |
|---|---|---|---|
| Pocket money (pre-schedule) | 20 G at age 10, +10 G per year | Stress −20, once/month | Doesn't work when sick or delinquent |
| Scold (pre-schedule) | Free | When delinquent: stress −(father relationship value), relationship +5 | If not delinquent: relationship −2; if sick: stress +5 and relationship drops |
| Free time (slot) | 0 G or 10 G/day with money | Stress −5/day (−10/day with money) | Father relationship −1%/day; delinquent daughter may waste money |
| Supervised free time (slot, delinquent only) | — | Stress ~−2/day, blocks money-wasting | Father relationship −1%/day; Cube relationship +5% if he catches her |
| Vacation (slot) | 100 G at age 10, +10 G per year | See seasonal table in [`mini-games.md`](mini-games.md#vacations-바캉스) | Father relationship +3% |
| Rest (slot, sick only) | Cube: free / Father: 10 G/day | Stress −2/day | Cube or father relationship +1%/day |
| Sanatorium (slot, sick only) | 20 G/day | Stress −11/day | — |
| Hospital (town, sick only) | 2× sickness % in G | Stress set to Constitution − 1 | — |
| Restaurant food (town) | Cake 80 G, Seafood 120 G | Cake stress −50 (+2.2 lb), Seafood stress −30 (+0.7 lb) | One meal/month; eating unpaid forces a free work shift. (Meat, 200 G, gives Constitution +15 and +2.6 lb but no stress relief) |
| Items (Pawn Shop) | Doll 120 G | Stress −40, Sensitivity +5 | Selling it later *raises* stress by the same amount |
| Fairies (errantry) | — | Stress → 0 | Also grants skills (and can lower Constitution) |
| Rival first meeting | — | Stress → 0 | — |
| Weather-appropriate dress | Summer/Winter dress | Stress −5 when a heat/cold wave hits | Without the dress, Constitution drops |
| Blood type B | — | Stress −2/month | — |
| Skipping the Harvest Festival | — | All of October becomes free time | Same as free time without money |

## Effort rewards (노력 보상 방문자)

Four supernatural mentors visit at the end of a month once **both** a
session count (classes/jobs/errantry in their discipline) and a reputation
threshold are met. Each gives an escalating gift.

| Visitor | Counts sessions of | Visit 1 | Visit 2 | Visit 3 | Visit 4 |
|---|---|---|---|---|---|
| Valkria (war goddess) | Fencing, Fighting, errantry | 5 sessions + Fighter 100 → Combat Skill +3 | 10 + 200 → Combat Attack +4 | 20 + 300 → Combat Defense +5 | 40 + 400 → Valkria Sword |
| Fay (sorceress) | Magic | 4 + Magic 100 → Magic Skill +3 | 8 + 200 → Magic Attack +4 | 16 + 300 → Magic Defense +5 | 32 + 400 → Power Ring (spells cost no MP) |
| Paimon (demon of success) | Painting, Dance, Protocol | 8 + Social 100 → Decorum +3 | 16 + 200 → Art +4 | 32 + 300 → Conversation +5 | 64 + 400 → Perfume (attracts suitors) |
| Domovoi (kitchen spirit) | Housework, Bar, Restaurant | 15 + Housework 100 → Cooking +3 | 30 + 200 → Cleaning +4 | 60 + 300 → Temperament +5 | 120 + 400 → Perfect Flour (always wins Cooking Contest) |

## Money sinks and shops (마을)

| Place | What it does |
|---|---|
| Armory (Zen) | Weapons and armor for errantry/fights |
| Tailor (Maura) | Dresses — seasonal protection, stat bonuses, needed for the Dance Party |
| Pawn Shop (Shalom) | Stat items (Book Intelligence +8 / 120 G, Doll Sensitivity +5 & stress −40 / 120 G, Poetry Book Sensitivity +12 / 400 G, Teacup Refinement +10 / 500 G), Healing Pill (heals 20–50 HP) 30 G, Grenade (1–80 damage) 100 G; buys anything back at half price |
| Restaurant (Balbon) | One meal a month (see stress relief) |
| Church (Sister Lee) | 100 G donation → Sin −10 |
| Hospital (Dr. Lombardini) | Only treats a sick daughter |
| Palace | One conversation per month to raise Renown (see [`mini-games.md`](mini-games.md#palace-talk-궁정-방문)) |

Other money-related systems:
- **Renown discounts:** every 100 Renown = 5% off in shops, up to 50% at 1000.
- **Birthday gift:** once a year the player can buy her a Pawn Shop item
  (skipping it lowers the father relationship).
- **Inventory:** most items apply their stat bonus just by being held;
  consumables are used. Inventory space is limited — the patron deity
  appears to suggest selling when it's full.
- **Traveling Salesman:** visits up to 3 times when the player's gold crosses
  set thresholds (1000 G first, 5000 G last; the middle threshold is 2000 G
  on his page but 3000 G on the main page). One purchase per visit from:
  Spirit Ring 1000 G, Unicorn Flute 1000 G, Demon Pendant 1200 G, Buxomize
  Pill 1200 G, Venus Jewels 1500 G, Siren Robe 4000 G. Several of these start
  a quest (return the item to its owner for a bigger reward).
- **Items that keep giving:** Venus Jewels (+20 Charisma/Refinement, plus
  Charisma/Refinement/Sensitivity each birthday), Paradise Egg (eat for
  Constitution +50, or let it hatch for Sensitivity +100).
