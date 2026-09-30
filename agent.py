"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction. ; a new session dictionary which holds the agents memory for a single run

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    the user query, parsed inputs, search results, selected item, wardrobe, outfit suggestion, fit card, and any error message get in here; 

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)

    def parse_query(text: str) -> dict:
        """Turn the free-text request into inputs for the search tool."""
        import re

        size_match = re.search(
            r"(?<![A-Za-z0-9])(?:XXS|XXL|XS|XL|S|M|L)(?![A-Za-z0-9])",
            text,
            flags=re.IGNORECASE,
        )
        price_match = re.search(
            r"(?:under|below|less than|up to|max(?:imum)?)\s*\$?\s*(\d+(?:\.\d{1,2})?)"
            r"|\$\s*(\d+(?:\.\d{1,2})?)",
            text,
            flags=re.IGNORECASE,
        )

        size = size_match.group(0).upper() if size_match else None
        price_text = (
            next((value for value in price_match.groups() if value), None)
            if price_match
            else None
        )
        max_price = float(price_text) if price_text else None

        # Strip constraints and request filler, leaving searchable keywords.
        description = text
        if size_match:
            description = (
                description[:size_match.start()]
                + " "
                + description[size_match.end():]
            )
        if price_match:
            description = (
                description[:price_match.start()]
                + " "
                + description[price_match.end():]
            )
        description = re.sub(
            r"\b(?:looking for|i am looking for|i'm looking for|find me|find|want|please|size)\b",
            " ",
            description,
            flags=re.IGNORECASE,
        )
        description = re.sub(r"[^\w\s'-]", " ", description)
        description = " ".join(description.split()).strip(" -'") or text.strip()

        return {
            "description": description,
            "size": size,
            "max_price": max_price,
        }

    def nothing_found_message(parsed: dict) -> str:
        """Explain which search constraints the user could loosen."""
        suggestions = ["try broader words for the item"]
        if parsed["size"]:
            suggestions.append("drop the size or try a nearby one")
        if parsed["max_price"] is not None:
            suggestions.append(
                f"raise the price ceiling above ${parsed['max_price']:g}"
            )
        return "No matching listings. You could " + ", or ".join(suggestions) + "."

    def handle_search_results(results: list[dict], parsed: dict) -> bool:
        """Save the branch outcome; return False when the plan should stop."""
        if not results:
            session["error"] = nothing_found_message(parsed)
            return False

        session["selected_item"] = results[0]
        return True

    steps = 0

    def check_next_step() -> None:
        nonlocal steps      
        #this would not create another variable 'steps' inside of the func but instead modify the outer variable 'steps'
        steps += 1
        trace.check_iterations(steps)
        # this is the guard that prevents the maximum iterations going above the max iterations set in config file ; 

    # Each check marks a step in the plan. If search has no matches, return
    # before calling tools that require a selected listing.
    check_next_step()
    parsed = parse_query(query)
    session["parsed"] = parsed

    check_next_step()
    results = search_listings(
        parsed["description"], parsed["size"], parsed["max_price"]
    )
    session["search_results"] = results

    if not handle_search_results(results, parsed):
        return session

    check_next_step()
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"], session["wardrobe"]
    )

    check_next_step()
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"], session["selected_item"]
    )
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
