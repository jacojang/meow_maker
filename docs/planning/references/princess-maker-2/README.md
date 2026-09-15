# Princess Maker 2 — Reference

Meow Maker is a cat-raising game modeled on *Princess Maker 2* (Gainax,
1993). This folder summarizes how PM2 works so Planning work can borrow from
(or deliberately diverge from) a proven design. It's reference material, not
a spec — nothing here is a Meow Maker decision.

## Read only what you need

| File | Covers |
|---|---|
| [`raising-system.md`](raising-system.md) | Monthly schedule, classes, jobs, money, stress relief, effort rewards, shops/items |
| [`status-system.md`](status-system.md) | All stats and what moves them, reputations, hidden stats, starting stats, status effects, parent interactions, diet/body |
| [`mini-games.md`](mini-games.md) | Harvest Festival contests, errantry (adventure) and combat, rivals/challengers, palace talk, vacations, supernatural events |
| [`characters-and-layout.md`](characters-and-layout.md) | Daughter/butler/player roles, NPC roster by function, main-screen UI layout, how the daughter's visuals change, clothing |
| [`endings.md`](endings.md) | How the ending is determined, ending categories, final score, marriages |

## The game in one page

**Premise.** A wandering swordsman (the player) saves the kingdom from the
demon lord Lucifon and settles in the capital on a 500 G/year royal stipend.
A patron deity hands him a girl (Olive) to raise; how she turns out decides
whether mankind has repented.

**Length.** The daughter is raised from age 10 to 18 — 8 in-game years. The
game ends on her 18th birthday with an ending, a score (max 1000), and the
patron deity's verdict. The only early game over is the daughter dying from
untreated illness.

**Core loop (each month).**
1. Optional pre-schedule actions: talk to her, give pocket money, scold, set
   her diet, shop in town, talk to someone at the palace.
2. Fill the month's **3 schedule slots** with a class, part-time job,
   errantry (adventure), free time, or vacation.
3. Each slot plays out day by day as a short animated scene; stats, stress
   and money change per day.
4. End of month: events may fire (visitors, suitors, weather, rivals,
   status changes), then the next month begins.

**Central tension.** Almost every productive activity raises **stress**.
Stress above Constitution makes her sick; stress above her Morality/Faith
makes her delinquent. Both wreck efficiency, so the player constantly trades
growth time for recovery time — and money (classes cost, jobs pay) gates
which kind of growth is available.

**Build identity.** Stats feed four **reputations** (Fighter, Magic, Social,
Housework). The highest reputation, relative gaps between them, and a few
key stats (Art, Morality, Sin, Charisma) pick one of ~74 endings plus an
optional marriage.

**Annual set piece.** Every October the **Harvest Festival** offers four
contests (combat, dance, art, cooking) that test the build and award money,
reputation and unique items.

## Patterns worth noting for Planning

Observations about PM2's design, for discussion — not decisions:

- **Every activity is a trade-off.** Nearly every job raises some stats and
  lowers others; only Church work lowers nothing positive. This keeps choices
  interesting without a skill tree.
- **"Highest stat" triggers.** Several random events key off whichever stat
  is currently highest (Charisma → suitors/love, Sensitivity → running away,
  Morality → a demon buying it). The player manages balance, not just totals.
- **Two currencies of time.** Schedule slots are scarce; some stress relief
  (cake, dolls, pocket money) costs money but no slot, which makes money
  convertible into time.
- **Effort rewards.** Supernatural mentors visit after N sessions of a
  discipline *and* a reputation threshold, giving escalating gifts — a
  long-term goal layered on the monthly loop.
- **Visible state.** Sickness, delinquency, weight and love all change how
  the daughter is drawn on the main screen, so status is readable without
  opening menus.
- **Age gating.** Jobs, dresses, rivals and suitors unlock by age, so the
  8-year arc has distinct early/mid/late phases.

## Sources and caveats

- Source: [Princess Maker Wiki — Princess Maker 2](https://princessmaker.fandom.com/wiki/Princess_Maker_2)
  and the ~200 sub-pages it links, retrieved 2026-09-15 via the wiki's
  MediaWiki API (the HTML site blocks automated fetches).
- The wiki mixes data from the DOS/PC-98, Refine and Regeneration versions,
  and some pages disagree with each other; conflicts are called out inline
  where found.
- Wiki images (UI screenshots, sprites) couldn't be retrieved — the image CDN
  rejects non-browser requests. Layout notes instead combine the wiki's text
  with Regeneration (2024 remake, Korean Switch version) screenshots from
  [this Naver blog post](https://m.blog.naver.com/114632/223503790979),
  viewed 2026-09-15. Those images aren't stored in the repo (third-party
  copyrighted material).
- The wiki has no dedicated page for errantry controls or the battle screen;
  that section is assembled from scattered mentions and is incomplete.
