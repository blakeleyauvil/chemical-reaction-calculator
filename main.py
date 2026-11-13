
from drafter import *
from dataclasses import dataclass
from bakery import assert_equal


@dataclass
class Result:
    """Stores the results of a chemical reaction calculation."""
    name: str
    limiting_reactant: str
    theoretical_yield: float
    percent_yield: float


@dataclass
class State:
    """Stores information used throughout the website."""
    reaction: str
    reactant1_mass: float
    reactant2_mass: float
    actual_yield: float
    history: list[Result]
    current_result: Result


# Converts grams into moles
def grams_to_moles(grams: float, molar_mass: float) -> float:
    """Takes grams and molar mass and returns the number of moles."""
    return grams / molar_mass


# Calculates percent yield
def percent_yield(actual: float, theoretical: float) -> float:
    """Takes actual and theoretical yield and returns percent yield."""
    return actual / theoretical * 100


# HOME PAGE
@route
def index(state: State) -> Page:
    """Displays the home page with calculator and history buttons."""
    return Page(state, [
        Header("Chemical Reaction Calculator"),
        "Calculate limiting reactant, theoretical yield, and percent yield.",
        Button("Calculator", select_reaction),
        Button("History", history)
    ])


# SELECT REACTION
@route
def select_reaction(state: State) -> Page:
    """Lets the user choose a balanced chemical reaction."""
    return Page(state, [
        Header("Select a Reaction"),
        SelectBox("reaction", [
            "2H2 + O2 -> 2H2O",
            "N2 + 3H2 -> 2NH3",
            "2Na + Cl2 -> 2NaCl"
        ]),
        Button("Continue", calculator),
        Button("Home", index)
    ])


# CALCULATOR PAGE
@route
def calculator(state: State, reaction: str = "") -> Page:
    """Displays textboxes for the user to enter reactant masses."""
    if reaction != "":
        state.reaction = reaction

    if state.reaction == "":
        return select_reaction(state)

    return Page(state, [
        Header("Enter Masses"),
        "Reaction: " + state.reaction,
        "Mass of Reactant 1 (g):",
        TextBox("mass1"),
        "Mass of Reactant 2 (g):",
        TextBox("mass2"),
        "Actual Yield (g):",
        TextBox("actual"),
        Button("Calculate", calculate),
        Button("Home", index)
    ])


# CALCULATE RESULTS
@route
def calculate(state: State, mass1: str,
              mass2: str, actual: str) -> Page:
    """Uses the entered masses to calculate the reaction yields."""

    try:
        state.reactant1_mass = float(mass1)
        state.reactant2_mass = float(mass2)
        state.actual_yield = float(actual)
    except ValueError:
        return Page(state, [
            Header("Invalid Input"),
            "Please enter numbers.",
            Button("Try Again", calculator)
        ])

    if state.reactant1_mass <= 0 or state.reactant2_mass <= 0:
        return Page(state, [
            Header("Invalid Input"),
            "Reactant masses must be positive.",
            Button("Try Again", calculator)
        ])

    if state.actual_yield < 0:
        return Page(state, [
            Header("Invalid Input"),
            "Actual yield cannot be negative.",
            Button("Try Again", calculator)
        ])

    # Information for each reaction
    if state.reaction == "2H2 + O2 -> 2H2O":
        name1, name2 = "H2", "O2"
        mm1, mm2, mm3 = 2.016, 32.0, 18.015
        c1, c2, c3 = 2, 1, 2

    elif state.reaction == "N2 + 3H2 -> 2NH3":
        name1, name2 = "N2", "H2"
        mm1, mm2, mm3 = 28.014, 2.016, 17.031
        c1, c2, c3 = 1, 3, 2

    else:
        name1, name2 = "Na", "Cl2"
        mm1, mm2, mm3 = 22.99, 70.90, 58.44
        c1, c2, c3 = 2, 1, 2

    # Convert grams to moles
    moles1 = grams_to_moles(state.reactant1_mass, mm1)
    moles2 = grams_to_moles(state.reactant2_mass, mm2)

    # Calculate possible product from each reactant
    product1 = moles1 / c1 * c3
    product2 = moles2 / c2 * c3

    # Find the limiting reactant
    if product1 < product2:
        limiting = name1
        product_moles = product1
    elif product2 < product1:
        limiting = name2
        product_moles = product2
    else:
        limiting = "Neither (exact ratio)"
        product_moles = product1

    # Calculate theoretical and percent yield
    theoretical = product_moles * mm3
    percent = percent_yield(state.actual_yield, theoretical)

    # Store the current calculation
    state.current_result = Result(
        state.reaction,
        limiting,
        theoretical,
        percent
    )

    return results(state)


# RESULTS PAGE
@route
def results(state: State) -> Page:
    """Displays the limiting reactant and calculated yields."""
    result = state.current_result

    return Page(state, [
        Header("Results"),
        "Reaction: " + result.name,
        "Limiting Reactant: " + result.limiting_reactant,
        "Theoretical Yield: " +
            str(round(result.theoretical_yield, 2)) + " g",
        "Percent Yield: " +
            str(round(result.percent_yield, 2)) + "%",
        Button("Save Result", save_result),
        Button("New Calculation", select_reaction),
        Button("Home", index)
    ])


# SAVE RESULT
@route
def save_result(state: State) -> Page:
    """Saves the current calculation to the history list."""

    state.history.append(state.current_result)

    return Page(state, [
        Header("Result Saved"),
        "Your calculation has been saved.",
        Button("View History", history),
        Button("New Calculation", select_reaction),
        Button("Home", index)
    ])


# HISTORY PAGE
@route
def history(state: State) -> Page:
    """Displays all the calculations saved by the user."""
    content = [Header("Calculation History")]

    if len(state.history) == 0:
        content.append("No saved calculations.")

    for result in state.history:
        content.append("Reaction: " + result.name)
        content.append("Limiting: " + result.limiting_reactant)
        content.append("Theoretical Yield: " +
                       str(round(result.theoretical_yield, 2)) + " g")
        content.append("Percent Yield: " +
                       str(round(result.percent_yield, 2)) + "%")

    content.append(Button("Clear History", clear_history))
    content.append(Button("Home", index))

    return Page(state, content)


# CLEAR HISTORY
@route
def clear_history(state: State) -> Page:
    """Removes all saved calculations from the history list."""
    state.history = []
    return history(state)


# TESTS
assert_equal(grams_to_moles(32, 32), 1.0)
assert_equal(percent_yield(8, 10), 80.0)


# START WEBSITE
start_server(State(
    "", 0.0, 0.0, 0.0, [],
    Result("", "", 0.0, 0.0)
))

