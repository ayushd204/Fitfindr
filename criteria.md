# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
My search uses keywords from the query, so an unusual phrasing may miss a listing that would otherwise fit. Four of five allows one miss while still requiring the normal query to work reliably.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
The empty-results branch is deterministic and returns before either model tool is called, so it should stop every time.

---

## 3. The selected listing reaches the outfit tool

For 5 matching queries, `session["selected_item"]` is the same listing dict passed to `suggest_outfit` in all 5 runs.

**Why this target:**
The loop selects one result and passes that saved value to the next tool, so this state handoff should be consistent every time.


---

## 4. The fit card includes listing details

For 5 different items, at least 4 fit cards mention the correct item's title, price, and platform.

**Why this target:**
The model writes the caption, so wording can vary and it may occasionally miss a detail. The item, price, and platform are the useful facts the caption should preserve.


---

## 5. Search respects the price ceiling

For 5 searches with a price ceiling, every returned listing costs no more than that ceiling.

**Why this target:**
The price ceiling is a direct numeric filter on the local listing data, so all returned results should satisfy it every time.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
