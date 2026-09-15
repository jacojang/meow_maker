# PM2 Status System (주인공 상태 정보 관리)

Every value the game tracks on the daughter, how each one moves, and the
status effects that trigger from them. Activities that change these values
are in [`raising-system.md`](raising-system.md).

Names vary by version; the main name is used here, with DOS/Refine names in
parentheses.

## Profile (personal information)

| Field | Behavior |
|---|---|
| Name, birth date | Chosen at start. Birth date sets the zodiac sign → patron deity → starting stats. Game starts on the birthday, in year 1200. |
| Age | 10 → 18. The game ends at 18. Unlocks jobs, dresses, rivals and suitors. |
| Blood type | Monthly modifier: **A** Morality +3 and Stress +2; **B** Stress −2; **O** none; **AB** Sensitivity +3 (the Statistics page says +2). |
| Height | Random 136–152 cm at start; grows ~0.15 cm/month (more if kept healthy). Sets the overweight threshold. |
| Weight | Starts at `height(cm) × 0.95 − 100` kg. Changed by diet, food, vacations, items. |
| Bust / Waist | Bust starts at half the initial height; waist = `0.15 × height + 0.5 × weight + 12.5` cm. Flavor only. |
| Renown (Popularity / Connections) | Raised by palace talk. Every 100 = 5% shop discount, max 50% at 1000. |
| Money | Shared household gold. |
| Equipment | Weapon, armor, dress. |

## General stats

| Stat | Role | Mainly raised by | Mainly lowered by |
|---|---|---|---|
| Constitution (Stamina) | HP in battle, work ability. **Stress > Constitution → sick.** | Robust diet, Farm, Masonry, Dance | Slim-down/weight-loss diets, missing weather dresses |
| Strength | +1 Combat Attack per 8 points | Farm, Lumberjack | Salon |
| Intelligence | Spell count (each spell costs 10 MP) | Science, Poetry, Strategy, Theology | Bar, Cabaret |
| Refinement (Elegance) | Grades most Social endings; Ruling Queen needs 800 | Protocol | Farm, Lumberjack, Hunter, Cabaret |
| Charisma (Glamour) | Marriages, Bar/Cabaret work, Dance Party. **Rises by its starting value every birthday.** −2/month when overweight. | Dance, Cabaret, events | Babysitting, Masonry, Graveyard |
| Morality (Morals) | **Stress > max(Morality, Faith) → delinquent.** Gates good endings/marriages. | Church, Tutor, blood type A | Sleazy Bar, shady deals |
| Faith | Same delinquency check as Morality | Church, Theology | Science (Adept+), sinful acts |
| Sin | Pushes toward dark endings; −1 final score per point | Killing monsters/travelers on errantry, Sleazy Bar, Cabaret, evil deals | Church work, donations (100 G = −10), getting arrested |
| Sensitivity | Hide/flee/talk and item-finding on errantry; seeing fairies and elves; Cooking Contest | Mountain vacations, dolls, Poetry, Painting, Salon, Babysitting | Housework, Strategy |
| Stress | Work/study efficiency; drives sickness and delinquency. No effect on final score. | Nearly every job and class | See stress relief in [`raising-system.md`](raising-system.md#stress-relief-스트레스-해소) |

## Skills

| Group | Skill | Role | Raised by |
|---|---|---|---|
| Combat | Combat Skill | Hit and dodge chance | Fighting, Fencing, Hunter |
| Combat | Combat Attack | Physical damage (+ Strength/8, weapons) | Fencing |
| Combat | Combat Defense | Physical damage taken | Fighting (Adept+), armor, Black Scales |
| Magic | Magic Skill | Spell hit and dodge chance; can't be lowered | Magic, Fay |
| Magic | Magic Attack | Spell damage; can't be lowered | Magic, Fay |
| Magic | Magic Defense | Spell damage taken | Theology, Graveyard; lowered by Science |
| Social | Decorum | Which palace folk she can talk to; can't be lowered | Protocol, Paimon |
| Social | Art (Artistry) | Dance Party, painting quality, Salon/Masonry/Cabaret success. **Highest housework/social skill → Artistic ending.** | Painting, Poetry, Dance, fairies, Master Brush |
| Social | Conversation (Eloquence / Speech) | Talking to the Concubine and Jester; some endings | Bar only (+ Paimon) |
| Housework | Cooking | Cooking Contest | Housework, Restaurant, Bar, fairies |
| Housework | Cleaning | Housework Reputation only | Housework, Inn |
| Housework | Temperament (Temper / Personality) | Talking to the Queen; lowers runaway chance | Housework only |

## Reputations

Each reputation is the **sum of three skills**, plus bonuses earned from
contests and fights. The highest reputation largely decides the ending
category (see [`endings.md`](endings.md)).

| Reputation | Sum of | Also raised by | Lowered by |
|---|---|---|---|
| Fighter | Combat Skill + Attack + Defense | Winning challenges/tournament mostly with melee, catching bandits, Dragon's Fang | Refusing a challenge, trying to sell the Royal Sword, arrest, running away |
| Magic | Magic Skill + Attack + Defense | Winning fights mostly with magic | Refusing a challenge, arrest, running away |
| Social | Decorum + Conversation + Art | Winning the Art Festival or Dance Party | Selling the Royal Sword, arrest, talking to the Jester, running away |
| Housework | Cooking + Cleaning + Temperament | Winning the Cooking Contest | Arrest, running away |

In battle, her **morale** equals whichever of Fighter/Magic Reputation is higher.

## Hidden stats

Not shown until the ending; hinted through conversation.

| Stat | Effect | Raised by | Lowered by |
|---|---|---|---|
| Relationship with father | Lowers runaway chance; scold effectiveness; father marriage | Vacations, talking, birthday gifts, nursing her when sick, Housework | Free time, skipping her birthday gift, falling in love, pointless scolding, refusing her rival contest, Sleazy Bar, accepting suitors |
| Relationship with Cube | Cube marriage | Cube nursing her, rescuing her in errantry, catching her wasting money, consoling her after a tournament loss | Falling in love |
| Relationship with the Prince | Prince marriage (96 — i.e. all 8 yearly meetings — per the Statistics page; 90% per the Special Marriages page) | Meeting the Young Officer every January 31st | Falling in love |
| Maternal instinct | Flavor in generic marriage; affects Princess of Darkness score | Babysitting, Tutor | Hunter |

## Starting stats by patron deity

The birth date's zodiac sign picks a patron deity, which sets all starting
values (none start with Stress, Sin or Combat Defense). The deity also
judges the ending and grants **+100** to one stat if she defeats the War God.

| Deity (sign, dates) | Con | Str | Int | Ref | Cha | Mor | Fai | Sen | War God bonus |
|---|---|---|---|---|---|---|---|---|---|
| Saturn (Capricorn, 12/22–1/19) | 25 | 20 | 17 | 15 | 10 | 38 | 20 | 13 | Refinement |
| Uranus (Aquarius, 1/20–2/18) | 17 | 18 | 42 | 12 | 10 | 13 | 8 | 28 | Sensitivity |
| Neptune (Pisces, 2/19–3/20) | 16 | 15 | 15 | 32 | 31 | 24 | 30 | 45 | Intelligence |
| Mars (Aries, 3/21–4/19) | 45 | 45 | 13 | 10 | 7 | 14 | 21 | 6 | Morality |
| Venus (Taurus, 4/20–5/20) | 33 | 28 | 23 | 25 | 24 | 32 | 20 | 19 | Charisma |
| Mercury (Gemini, 5/21–6/21) | 19 | 18 | 36 | 14 | 14 | 7 | 10 | 35 | Intelligence |
| Moon (Cancer, 6/22–7/22) | 18 | 18 | 24 | 29 | 33 | 25 | 30 | 33 | Sensitivity |
| Sol (Leo, 7/23–8/22) | 50 | 50 | 7 | 42 | 18 | 23 | 10 | 9 | Refinement |
| Mercury (Virgo, 8/23–9/22) | 14 | 5 | 28 | 45 | 30 | 32 | 35 | 31 | Intelligence |
| Venus (Libra, 9/23–10/23) | 25 | 22 | 30 | 24 | 20 | 20 | 21 | 26 | Charisma |
| Hades (Scorpio, 10/24–11/22) | 28 | 20 | 22 | 9 | 42 | 10 | 27 | 39 | Sensitivity |
| Jupiter (Sagittarius, 11/23–12/21) | 38 | 35 | 24 | 23 | 11 | 10 | 12 | 20 | Faith |

Starting skills and reputations also differ per deity (e.g. Hades starts
with Magic Skill/Attack 30, Mars with Combat Skill 38, Mercury-Virgo with
Cooking/Cleaning/Temperament 29–30; Jupiter's Decorum 8 is too low to talk to
anyone at the palace). Full tables are on the wiki's *Patron Gods* page.

## Status effects (상태 이상)

Shown as three status boxes next to the equipment icons, and most also
change how the daughter is drawn on the main screen.

| Effect | Trigger | Consequences | Cure / prevention |
|---|---|---|---|
| **Sick** | Stress > Constitution. Sickness % accumulates; ≥10% = officially sick. | Poor efficiency at jobs and classes; battle HP reduced by sickness %; no free time/vacation (rest or sanatorium instead); no pocket money or restaurant. **>90% = bedridden; bedridden >2 months = death (only game over).** | Rest, sanatorium, hospital; lower stress below Constitution |
| **Delinquent** | Stress > max(Morality, Faith). Delinquency % accumulates; ≥10% = official. | Poor efficiency for the whole month; may waste money (especially in free time); ≥~60% turned away from all jobs except Housework/Church; ≥~90% may be arrested for joining a gang → stress and Sin (or Refinement) drop, but **all reputations −90%**. | Scold (with a good father relationship), supervised free time; lower stress below Morality/Faith |
| **In Love** | Age ≥14, Charisma is her highest stat, and she accepts a Flirty Punk's date (likelier with low Morality, high stress, low father relationship). | 3 months of dozing in class and poor work; father/Cube/Prince relationships −6. | Wait it out; keep another stat above Charisma |
| **Mistress** | Charisma is her highest stat and a rich old man's offer is accepted (age ≥14 on one page, ≥15 on another). | Small monthly income, but Morality and Refinement drop each month. | Scold with a high father relationship; keep Morality high |
| **Overweight** | Weight(kg) > `0.95 × height(cm) − (age + 87)` — the threshold gets stricter each birthday. | No status icon; her sprite visibly gets heavier. Charisma −2/month; can't wear most stat dresses. | Diet, summer sea vacation, Ancient Milk, Ket Shi |
| **Runaway** | Random, whenever Sensitivity is her highest stat. | She disappears from the main screen for the month (only stats/items/save usable); all reputations −10%. | Keep another stat above Sensitivity (e.g. Housework lowers it) |

## Parent interactions (pre-schedule)

| Action | Effect |
|---|---|
| Father–daughter talk | Builds the father relationship; reveals hints about her condition and hidden stats. |
| Pocket money | Stress −20 once a month (20 G at 10, +10 G per year). |
| Scold | Only useful when delinquent — see [`raising-system.md`](raising-system.md#stress-relief-스트레스-해소). |
| Diet | Set monthly; see below. |
| Birthday gift | Once a year; skipping it lowers the father relationship. |

## Diet

| Diet | Cost/month | Effect | Weight change/month |
|---|---|---|---|
| Normal | 30 G | — | +0.13 to +0.48 |
| Robust (Hearty) | 80 G | Constitution +10 | +0.64 to +0.78 |
| Slim down | 10 G | Constitution −5 | +0.02 to +0.07 |
| Weight loss | 5 G | Constitution −20 | −0.05 to −1.79 |

(The wiki doesn't state the weight unit for this table; other pages use pounds.)
Cube will switch her back to Robust if she gets too thin.
