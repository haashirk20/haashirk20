"""README graphics for haashirk20/alzhiemersML. Numbers come from running ML.train_model
with its fixed split (random_state=16) on alzheimers_disease_data.csv."""
from kit import W, bars, boxes, cells, fillrect, frame, head, hero, kicker, steps, text
from build import JOST, JOST_MED, MONO, SANS

# The app's own Streamlit theme (.streamlit/config.toml): #386641, #6a994e, #a7c957, white text.
THEMES = {
    "dark": {"bg": "#386641", "ink": "#FFFFFF", "dim": 0.74, "line": 0.22, "accent": "#A7C957", "panel": "#6A994E"},
    "light": {"bg": "#F4F8EC", "ink": "#1D3522", "dim": 0.68, "line": 0.16, "accent": "#386641", "panel": "#E1ECCB"},
}


def questionnaire(t):
    """A sketch of the app's form: fields, a slider, a radio, Calculate, and the probability bar."""
    x, y, w = 520, 60, 300
    lab = lambda s, dx, dy: text(t, s, SANS, 12, x + dx, y + dy, op=.85)[0]
    field = lambda dx, dy, fw: f'<rect x="{x + dx}" y="{y + dy}" width="{fw}" height="26" rx="4" fill="{t["bg"]}" fill-opacity=".6"/>'
    return (f'<rect x="{x}" y="{y}" width="{w}" height="280" rx="8" fill="{t["panel"]}"/>'
            + lab("Age", 20, 32) + field(20, 40, 120) + lab("BMI", 160, 32) + field(160, 40, 120)
            + lab("Sleep quality (0 to 10)", 20, 92) + fillrect(t, x + 20, y + 104, 260, 4, .35) + fillrect(t, x + 20, y + 104, 170, 4, 1, accent=True)
            + f'<circle cx="{x + 190}" cy="{y + 106}" r="7" fill="{t["accent"]}"/>'
            + lab("Memory complaints", 20, 138)
            + f'<circle cx="{x + 26}" cy="{y + 154}" r="5" fill="none" stroke="{t["ink"]}"/><circle cx="{x + 86}" cy="{y + 154}" r="5" fill="{t["ink"]}"/>'
            + text(t, "Yes", SANS, 12, x + 36, y + 158)[0] + text(t, "No", SANS, 12, x + 96, y + 158)[0]
            + f'<rect x="{x + 20}" y="{y + 184}" width="110" height="32" rx="6" fill="{t["bg"]}"/>'
            + text(t, "Calculate", JOST_MED, 13, x + 75, y + 205, anchor="middle")[0]
            + text(t, "PROBABILITY OF A DIAGNOSIS", JOST, 10, x + 20, y + 246, op=.75, tracking=0.2)[0]
            + fillrect(t, x + 20, y + 256, 260, 8, .2) + fillrect(t, x + 20, y + 256, 90, 8, 1, accent=True))


def g_hero(t):
    return hero(t, "ML PROJECT  ·  2024", "Alzheimer's\nRisk Predictor",
                "A questionnaire-driven logistic regression model, served as a Streamlit app.",
                [("2,149", "patients"), ("23", "questions"), ("30", "features"), ("69.8%", "test accuracy")],
                "Student ML project. Not a medical tool.", figure=questionnaire)


def g_flow(t):
    h, y = head(t, "HOW IT WORKS", "From a web form to a probability.")
    return (frame(t, 300) + h + steps(t, [
        ("Kaggle data", "2,149 patient rows"),
        ("clean_data", "drop clinical tests, one-hot encode"),
        ("train_model", "elastic-net LR, saga, l1_ratio 0.5"),
        ("Questionnaire", "23 answers become 30 features"),
        ("predict_proba", "probability of a diagnosis"),
    ], 40, y, W - 80, accent=4)
        + text(t, "ML.py", MONO, 11, 40, y + 132, op=t["dim"])[0]
        + text(t, "streamlit.py", MONO, 11, 40 + 3 * (W - 80 + 24) / 5, y + 132, op=t["dim"])[0])


def g_inputs(t):
    h, y = head(t, "WHAT THE MODEL SEES", "Only answers a person knows without a doctor.")
    return (frame(t, 300) + h
            + kicker(t, "KEPT  ·  23 QUESTIONS", 40, y, accent=True)
            + boxes(t, ["Age, BMI, sex, education, ethnicity", "Alcohol, activity, diet, sleep (0 to 10)",
                        "Family history, diabetes, hypertension, …", "Memory complaints, confusion, …"], 40, y + 16, 380)
            + kicker(t, "DROPPED  ·  CLINICAL TESTS", 460, y)
            + boxes(t, ["Blood pressure", "Cholesterol panel", "MMSE score", "Functional assessment, ADL score"], 460, y + 16, 380, dim=True))


def g_results(t):
    h, y = head(t, "RESULTS", "Beats the baseline, misses most positive cases.")
    return (frame(t, 370) + h
            + kicker(t, "ACCURACY ON 430 TEST PATIENTS", 40, y)
            + bars(t, [("Model", 69.8, True), ("Majority-class baseline", 64.2, False)], 40, y + 34, 330)
            + text(t, "Precision 0.62  ·  Recall 0.41, diagnosed class", MONO, 11, 40, y + 160, op=t["dim"])[0]
            + kicker(t, "CONFUSION MATRIX", 500, y)
            + cells(t, [("237", "TRUE NEGATIVE", False), ("39", "FALSE POSITIVE", False),
                        ("91", "FALSE NEGATIVE", True), ("63", "TRUE POSITIVE", False)], 500, y + 18, 167, 84)
            + text(t, "Rows: actual  ·  Columns: predicted", MONO, 10.5, 500, y + 212, op=t["dim"])[0])


GRAPHICS = {
    "hero": (400, g_hero, "Alzheimer's Risk Predictor: 2,149 patients, 23 questions, 30 features, 69.8% test accuracy"),
    "how-it-works": (300, g_flow, "How it works: Kaggle data, clean_data, train_model, questionnaire, predict_proba"),
    "inputs": (300, g_inputs, "Kept: 23 self-reported questions. Dropped: blood pressure, cholesterol, MMSE, functional assessment and ADL"),
    "results": (370, g_results, "Accuracy 69.8% vs 64.2% majority baseline. Confusion matrix: 237 TN, 39 FP, 91 FN, 63 TP"),
}
