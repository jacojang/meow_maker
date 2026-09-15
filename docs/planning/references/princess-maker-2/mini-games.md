# PM2 Mini-games and Event Systems (미니 게임)

PM2 has no twitch-skill mini-games. Its "mini-games" are set-piece systems
that test the daughter's stats: the yearly Harvest Festival contests,
errantry (a directly controlled adventure with turn-based fights), palace
conversations, vacations, and a large set of stat-gated random events.

## Harvest Festival (수확제) — every October

Four contests, one entry per year. Skipping the festival turns October into
free time. If she has a rival, not entering the rival's contest costs +10
stress.

| Contest | Scoring | Requirements | Prizes (1st / 2nd / 3rd) | Rival |
|---|---|---|---|---|
| **Combat Tournament** | Knockout bracket of battles. Each fight gives both sides 9 attacks; if nobody drops, the General judges by remaining HP. Up to 300 G per round won. | Fighting ability (see combat below) | Royal Sword + 3000 G + 20 Fighter/Magic Rep / 1000 G + 10 Rep | Anita (fighter) or Wendy (mage) — always her first opponent |
| **Art Festival** | Score = her Art at the moment she painted her entry | A painting from Painting class (100 G materials) | Master Brush + 4000 G + 30 Social Rep / 1200 G + 20 / 800 G | None |
| **Dance Party** | `Art × rand(0.7–1.3)` + `Charisma × rand(0.7–1.3)` + Prime Minister popularity bonus (0–120) | A qualifying dress bought *before* the festival (not the Summer/Winter dress) | Lady's Ring + 3000 G + 40 Social Rep / Artistic merit 1000 G + 30 / Technical merit 500 G + 20 | Patricia |
| **Cooking Contest** | `(Sensitivity / 100) × Cooking × rand(0.7–1.3)` | — | Paradise Egg + 3000 G + 40 Housework Rep / 1000 G + 25 / 500 G + 15 | Marthia |

Details that shape play:
- The Art Festival is the easiest early win: a high-Art painting ("Advent of
  Angels") almost always wins, and there's no rival.
- The Cooking Contest can be won cheaply early (Housework for Cooking, then
  Babysitting for Sensitivity), and the Perfect Flour item guarantees a win.
- NPC contestants are recurring characters (teachers, job bosses, rivals),
  so the festival also shows off the town's cast.
- Contest items have follow-ups: trying to sell the Royal Sword halves her
  Renown with the King and General and lowers Fighter/Social Reputation; the
  Paradise Egg can be eaten or hatched.

## Rivals

At age 14, if one reputation is ≥100, the rival matching her **highest**
reputation confronts her after a class and challenges her to that contest.
The first meeting drops her stress to 0. Rivals' stats scale with age.

| Rival | Reputation | Contest | Also seen |
|---|---|---|---|
| Anita Cassandra | Fighter | Combat Tournament | Works at the armory |
| Wendy Lachesis | Magic | Combat Tournament | Works at the pawn shop, Magic class |
| Patricia Hearn | Social | Dance Party (also enters the Art Festival but never wins it) | Painting class |
| Marthia Shareweare | Housework | Cooking Contest | Assistant chef at the restaurant |

## Errantry (무사수행 / 모험)

Errantry is a schedule option where the player **directly controls the
daughter** on a top-down map of one of four regions around the capital —
the only time the player steers her directly.

| Region | Difficulty | Terrain | Notable places and events | Bandit / boss | Loot |
|---|---|---|---|---|---|
| Eastern Forest | Easy ("safe for a beginning adventurer") | Dense forest and swamps; hidden holes link areas | Fairy tea party (Cooking +20–40, stress → 0); Sacred Tree Elf (trades Combat Skill −5 for each Magic skill +5); Unicorn event | Venezaro (first bandit) | Treasure chests, Ancient Milk |
| Southern Lakes | Not stated ("infested with many aquatic monsters") | Rivers, waterfalls, islands | Fairy tea party and fairy ball (Art, stress → 0) | Bloodrose Vanesta (1500 G bounty) | Black Scale (Combat Defense), gold |
| Northern Glaciers | Advanced | Mountains and glacier | Ket Shi's igloo (height/weight trade); Shrine of the War God (gateway to heaven) | Hurricane Castio (3500 G bounty); the War God (hardest fight) | Free Katana, Ice Shard (stress relief), gold |
| Western Desert | Very dangerous ("rumored to open onto hell") | Desert, ruins, oasis | Dragons in the Ancient Ruins (toll or fight; Dragon Tights; dragon marriage route); Spirit of the Spring (return the Spirit Ring); Lucifon at the Demon's Abode (trades Faith for stats, +Sin) | — | Dragon's Fang, Demon Dress (rare), Ancient Milk, gold |

How an outing works (assembled from scattered wiki mentions; there is no
single mechanics page):
- **Movement and time:** she walks the map during the session; she can
  **camp** at night, which is when fairy, unicorn and Lucifon events trigger.
  Healing Pills can be used while camping.
- **Encounters:** monsters, civilians (flavor dialogue) and bandits appear.
  High **Sensitivity** improves the odds of hiding, fleeing, talking a
  monster out of fighting, and finding items. Some creatures (fairies,
  elves) are only visible above a Sensitivity threshold.
- **Leaving:** exiting through the region's far ("second") exit raises her
  higher of Fighter/Magic Reputation.
- **Defeat:** Cube comes to rescue her (raising their relationship). With
  Charisma ≥100, losing to certain bandits triggers an assault attempt that
  Cube interrupts.
- **Costs:** killing monsters and travelers raises **Sin**; accepting a
  bandit's bribe instead of fighting gives +50 Sin.
- Each completed errantry session counts toward Valkria's effort rewards.

### Combat

Used in errantry, the Combat Tournament, bandit fights and random challenges.

| Value | Source |
|---|---|
| HP | Constitution (reduced by sickness %) |
| MP | Intelligence; each spell costs 10 MP (Power Ring removes the cost) |
| Hit / dodge (melee) | Combat Skill |
| Damage (melee) | Combat Attack (+ Strength/8, weapon) |
| Damage taken (melee) | Combat Defense (armor) |
| Hit / dodge, damage, resistance (magic) | Magic Skill / Attack / Defense |
| Morale | The higher of her Fighter/Magic Reputation |

- Fights are turn-based; commands seen on the wiki are melee attack, magic,
  items (Healing Pill heals 20–50 HP, Grenade does 1–80 damage and always
  hits), and fleeing.
- **Morale works like a second health bar:** damage also drains the enemy's
  morale, and an enemy out of morale flees. Enemies with low morale relative
  to HP (e.g. demons: 50 morale, 260+ HP) almost always escape; Grenades
  don't drain morale. Bosses have very high morale (bandits 880–970, War God
  999).
- Winning mostly with melee raises Fighter Reputation; mostly with magic,
  Magic Reputation.

### Random challengers

With enough Fighter or Magic Reputation, named fighters challenge her when
leaving the town menu or between schedule slots. Refusing costs −15 of the
higher reputation; winning gives +10. A "dojo destroyer" can also raid the
Fencing school.

## Palace talk (궁정 방문)

One conversation per month. Each person needs a minimum **Decorum**, raises
**Renown** based on a stat they favor, and has a per-visit cap and a total cap.
Every person she can talk to holds a position she can reach as an adult.

| Person | Decorum needed | Favors | Renown per visit | Total cap |
|---|---|---|---|---|
| Palace Guard | 10 | Refinement (1 per 5) | ≤15 | 40 |
| Royal Knight | 30 | Refinement (1 per 8) | ≤25 | 50 |
| General | 50 | Charisma (1 per 5) | ≤50 | 120 |
| Minister of State | 70 | Intelligence (1 per 10) | ≤60 | 100 — also gives a Dance Party bonus |
| Archbishop | 80 | Faith (1 per 10) | ≤60 | 120 |
| Royal Concubine | 85 | Conversation (1 per 10) | ≤10 | 120 |
| Queen | 90 | Temperament (1 per 10) | ≤10 | 160 |
| King | 95 | Fighter Reputation (1 per 10) | No cap | 300 |
| Young Officer | Any (only on January 31st) | — | — | Raises the hidden Prince relationship |
| Court Jester | Conversation 40+ | — | Social Rep −15, Sensitivity +15 per visit | Visits her home after 7/14/21 talks (hint, Royal Harp, farewell) |

## Vacations (바캉스)

A schedule slot costing 100 G at age 10 (+10 G per year). Every vacation
raises the father relationship by 3%. Not available while sick.

| Destination | Spring | Summer | Autumn | Winter |
|---|---|---|---|---|
| Sea | Stress −3/day | Stress −6/day, weight −~2.2 lb | Stress −3/day | Stress −2/day |
| Mountains | Stress −3/day, Sensitivity +1/day | Same as spring | Stress −6/day, Sensitivity +2/day, weight +~2.2 lb | Same as spring (blocked during a snowstorm event) |

Items can trigger vacation events (e.g. a Mermaid Tear at the sea →
Charisma +50, Sensitivity +20).

## Supernatural and random events

Most are one-time or conditional visits that make the world feel reactive to
the build. Effort-reward mentors (Valkria, Fay, Paimon, Domovoi) are in
[`raising-system.md`](raising-system.md#effort-rewards-노력-보상-방문자).

| Event | Trigger | Outcome |
|---|---|---|
| Fairies | Camp at specific spots with Sensitivity 50–200 | Cooking or Art boost, stress → 0 |
| Tree Elf | Sensitivity 200+, no iron equipment | Combat Skill −5 → each Magic skill +5 |
| Unicorn | Camp in the forest holding the Unicorn Flute | Return it: Sensitivity +50; refuse: Sensitivity halved |
| Spirit of the Spring | Bring the Spirit Ring to the desert oasis | Return it: Refinement +50, and a year later Sensitivity +100 and 2000 G; refuse: Sensitivity halved |
| Ket Shi | Carry a Cat's Eye to his cabin/igloo | Height ±0.5 in or weight −2 lb |
| Lucifon | Camp at the Demon's Abode | Faith ≥20: +1–50 to a chosen stat for −1–15 Faith and +25 Sin. Faith <20: she drinks his wine (+~80 Sin; required for the Lucifon marriage) |
| Dragons | Desert ruins | Young Dragon toll (200 G) or fight; Old Dragon gives Dragon Tights at 15+ with Charisma 100+; proposal leads to the Dragon Youth marriage (10,000 G engagement gift) |
| The War God | Northern shrine | Very hard fight; win → War God Sword and +100 stat from the patron deity |
| Skeleton Knight | Graveyard job with Fighter Rep ~100 | Duel; win → 2539 G |
| P.D. Karl (demon) | Morality is her highest stat | Offers 10 G per Morality point for all of it |
| Flirty Punk | Age 14+, Charisma highest | Date → "In Love" status |
| Dirty Old Man | Charisma highest (age 14+/15+) | Mistress offer → "Mistress" status |
| Suitor | Charisma and Refinement 200+ (or Perfume) | Marriage proposal with a 500–1000 G gift; accepting lowers the father relationship |
| Traveling Salesman | Gold crosses set thresholds (3 visits) | Rare items, several of which start the events above |
| Fortune Teller | Occasional visit | For a fee, reveals the ending she'd currently get |
| Heat / cold wave | Seasonal | Cube asks her to change dresses; without the right one she loses Constitution, with it stress −5 |
