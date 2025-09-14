import streamlit as st
import json
import os

# -----------------------
# Configuration / helper
# -----------------------

GRADE_POINTS = {
    "S": 10,
    "A": 9,
    "B": 8,
    "C": 7,
    "D": 6,
    "E": 5,
    "F": 0
}

SUBJECTS_JSON = "subjects.json"
NUM_SEMS = 5

DEFAULT_SUBJECTS = {
    "sem1": [
        {"code": "MA201", "name": "Mathematics-I", "credits": 4.0},
        {"code": "ME202", "name": "EG", "credits": 3.0},
        {"code": "EE201", "name": "Basic Electrical Engineering", "credits": 4.0},
        {"code": "EE202", "name": "Basic Electrical Engineering Laboratory", "credits": 1.5},
        {"code": "CS201", "name": "Programming for Problem Solving", "credits": 3.0},
        {"code": "CS202", "name": "Programming Laboratory", "credits": 1.5}
    ],
    "sem2": [
        {"code": "MA202", "name": "Mathematics-II", "credits": 4.0},
        {"code": "PH201", "name": "Physics", "credits": 4.0},
        {"code": "PH202", "name": "Physics Laboratory", "credits": 1.5},
        {"code": "CY201", "name": "Chemistry", "credits": 4.0},
        {"code": "CY202", "name": "Chemistry Laboratory", "credits": 1.5},
        {"code": "ME201", "name": "Workshop and Manufacturing Practice", "credits": 1.5},
        {"code": "HS201", "name": "English for Communication", "credits": 3.0}
    ],
    "sem3": [
        {"code": "SH201", "name": "Biology for Engineers", "credits": 2.0},
        {"code": "EC235", "name": "EDDS", "credits": 3.0},
        {"code": "CS203", "name": "COA", "credits": 4.0},
        {"code": "CS204", "name": "Data Structures", "credits": 3.0},
        {"code": "CS205", "name": "OOPL", "credits": 3.0},
        {"code": "EC236", "name": "EDDS Laboratory", "credits": 1.5},
        {"code": "CS206", "name": "Data Structures Laboratory", "credits": 1.5},
        {"code": "CS207", "name": "OOPL Laboratory", "credits": 1.5}
    ],
    "sem4": [
        {"code": "MA206", "name": "Mathematics for Computing", "credits": 4.0},
        {"code": "CS208", "name": "Operating Systems", "credits": 3.0},
        {"code": "CS209", "name": "DAA", "credits": 3.0},
        {"code": "CS210", "name": "DBMS", "credits": 3.0},
        {"code": "CS211", "name": "Software Engineering", "credits": 4.0},
        {"code": "CS212", "name": "Operating Systems Laboratory", "credits": 1.5},
        {"code": "CS213", "name": "DAA Laboratory", "credits": 1.5},
        {"code": "CS214", "name": "DBMS Laboratory", "credits": 1.5}
    ],
    "sem5": [
        {"code": "HS202", "name": "IEM", "credits": 3.0},
        {"code": "CS215", "name": "Platform Technologies", "credits": 3.0},
        {"code": "CS216", "name": "Computer Networks", "credits": 3.0},
        {"code": "CS217", "name": "ATCD", "credits": 4.0},
        {"code": "CS218", "name": "Platform Technologies Laboratory", "credits": 1.5},
        {"code": "CS219", "name": "Computer Networks Laboratory", "credits": 1.5},
        {"code": "CSY06/CSY03", "name": "MAD/Python", "credits": 3.0},
        {"code": "NILL", "name": "Open Elective", "credits": 3.0}
    ]
}


def ensure_subjects_file():
    if not os.path.exists(SUBJECTS_JSON):
        with open(SUBJECTS_JSON, "w") as f:
            json.dump(DEFAULT_SUBJECTS, f, indent=2)


def load_subjects():
    ensure_subjects_file()
    with open(SUBJECTS_JSON, "r") as f:
        return json.load(f)


def save_subjects(data):
    with open(SUBJECTS_JSON, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------
# GPA calculation helpers
# -----------------------

def calc_credit_weighted_gpa(subjects_with_grades):
    """
    Credit-weighted GPA:
      GPA = sum(credits * grade_points) / sum(credits)
    subjects_with_grades: list of dicts with {'code','name','credits','grade'}
    Returns tuple (gpa, numerator, total_credits)
    """
    numerator = 0.0
    total_credits = 0.0
    for s in subjects_with_grades:
        gp = GRADE_POINTS.get(s.get("grade", "F"), 0)
        credits = float(s.get("credits", 0.0))
        numerator += credits * gp
        total_credits += credits
    if total_credits == 0:
        return 0.0, 0.0, 0.0
    gpa = round(numerator / total_credits, 3)
    return gpa, round(numerator, 3), round(total_credits, 3)

# -----------------------
# Streamlit UI
# -----------------------

st.set_page_config(page_title="GPA / CGPA Calculator (Credit-weighted)", layout="wide")
st.title("GPA & CGPA Calculator — credit-weighted (0–10 scale)")

subjects_data = load_subjects()

st.sidebar.header("Notes")
st.sidebar.write("""
- Grade points: S=10, A=9, B=8, C=7, D=6, E=5, F=0  
- GPA formula (per semester, credit-weighted): **GPA = sum(credits * grade_points) / sum(credits)**  
- CGPA formula (cumulative): **CGPA = (Σ Ci * GPi) / (Σ Ci)** where summation runs over ALL courses registered up to the semester.
""")

# Session state for saved GPAs and per-sem numerators/credits
if "saved_gpas" not in st.session_state:
    st.session_state.saved_gpas = {f"sem{i}": None for i in range(1, NUM_SEMS+1)}
if "saved_numerators" not in st.session_state:
    st.session_state.saved_numerators = {f"sem{i}": 0.0 for i in range(1, NUM_SEMS+1)}
if "saved_total_credits" not in st.session_state:
    st.session_state.saved_total_credits = {f"sem{i}": 0.0 for i in range(1, NUM_SEMS+1)}
# included_arrears: track last recorded contribution per arrear subject
# structure: { subject_code: { "original_sem": int, "numerator": float, "credits": float, "grade": "A" } }
if "included_arrears" not in st.session_state:
    st.session_state.included_arrears = {}

st.sidebar.markdown("### Saved semester GPAs")
for i in range(1, NUM_SEMS+1):
    val = st.session_state.saved_gpas.get(f"sem{i}")
    st.sidebar.write(f"Sem {i}: {val if val is not None else 'Not calculated'}")

if st.sidebar.button("Reset all saved GPAs & totals"):
    st.session_state.saved_gpas = {f"sem{i}": None for i in range(1, NUM_SEMS+1)}
    st.session_state.saved_numerators = {f"sem{i}": 0.0 for i in range(1, NUM_SEMS+1)}
    st.session_state.saved_total_credits = {f"sem{i}": 0.0 for i in range(1, NUM_SEMS+1)}
    st.session_state.included_arrears = {}
    # clear raw_sem_totals as well
    if "raw_sem_totals" in st.session_state:
        del st.session_state["raw_sem_totals"]
    st.experimental_rerun()

# Semester selection
sem = st.selectbox("Select semester to enter grades for:", options=list(range(1, NUM_SEMS+1)), index=0)
sem_key = f"sem{sem}"
st.markdown(f"## Semester {sem}")

semester_subjects = subjects_data.get(sem_key, [])
if not semester_subjects:
    st.warning("No subjects defined for this semester in subjects.json. Edit the file or use the 'View / Edit subjects JSON' option below.")
else:
    st.write("Enter grades for this semester's subjects:")
    grades_for_sem = {}
    cols = st.columns(4)
    for idx, subj in enumerate(semester_subjects):
        col = cols[idx % 4]
        with col:
            st.write(f"**{subj['code']}** — {subj['name']} ({subj['credits']} cr)")
            grades_for_sem[subj["code"]] = col.selectbox(
                f"Grade for {subj['code']}",
                options=list(GRADE_POINTS.keys()),
                index=0,
                key=f"{sem_key}_{subj['code']}"
            )

    # Arrears / backlog inclusion
    st.markdown("---")
    st.write("Arrears / cleared backlog")
    include_arrears = st.checkbox("Include cleared arrears from previous semesters in this semester's GPA calculation?")
    arrear_subjects_with_grades = []
    if include_arrears:
        prev_sems = [i for i in range(1, sem)]
        if not prev_sems:
            st.info("No previous semesters available.")
        else:
            chosen_prev_sems = st.multiselect("Select previous semester(s) that have cleared subjects now:", options=prev_sems)
            for p in chosen_prev_sems:
                p_key = f"sem{p}"
                st.markdown(f"**Subjects from Semester {p}**")
                p_subjects = subjects_data.get(p_key, [])
                if not p_subjects:
                    st.write("No subjects defined for that semester.")
                    continue
                for s in p_subjects:
                    include_this = st.checkbox(f"Include {p_key}-{s['code']} — {s['name']} ({s['credits']}cr)", key=f"arrear_{p_key}_{s['code']}")
                    if include_this:
                        grade_choice = st.selectbox(
                            f"Grade after clearing for {s['code']} (Semester {p})",
                            options=list(GRADE_POINTS.keys()),
                            index=0,
                            key=f"arrear_grade_{p_key}_{s['code']}"
                        )
                        arrear_subjects_with_grades.append({
                            "code": s["code"],
                            "name": s["name"],
                            "credits": s["credits"],
                            "grade": grade_choice,
                            "original_sem": p
                        })

    # Compose the list of subjects to calculate GPA (NOTE: do NOT include arrears here)
    subjects_selected_for_calc = []
    for subj in semester_subjects:
        subjects_selected_for_calc.append({
            "code": subj["code"],
            "name": subj["name"],
            "credits": subj["credits"],
            "grade": grades_for_sem[subj["code"]]
        })

    # Calculate GPA
    if st.button("Calculate GPA for this semester"):
        # --- Compute GPA for the current semester using ONLY the semester's own subjects (no arrears) ---
        subjects_only_for_sem = subjects_selected_for_calc  # already only current sem subjects

        gpa_val, numerator, total_credits = calc_credit_weighted_gpa(subjects_only_for_sem)
        st.success(f"Semester {sem} GPA (credit-weighted) = {gpa_val} (rounded to 3 decimals)")
        st.write(f"Numerator = sum(credits * grade_points) = {numerator}")
        st.write(f"Total credits = {total_credits}")
        st.write("Formula used: GPA = numerator / total_credits")

        # Save the current semester's raw totals (without arrears) into session raw_sem_totals
        if "raw_sem_totals" not in st.session_state:
            st.session_state.raw_sem_totals = {
                f"sem{i}": {"numerator": float(st.session_state.saved_numerators.get(f"sem{i}", 0.0)),
                            "credits": float(st.session_state.saved_total_credits.get(f"sem{i}", 0.0))}
                for i in range(1, NUM_SEMS+1)
            }
        # update raw totals for this semester (these are the raw semester totals BEFORE applying arrears)
        st.session_state.raw_sem_totals[sem_key] = {"numerator": float(numerator), "credits": float(total_credits)}

        # --- Record the semester GPA value (for immediate display) ---
        # We'll recompute saved_gpas below after rebuilding totals so they stay consistent.
        st.session_state.saved_gpas[sem_key] = gpa_val

        # --- NEW: record included arrears into the global included_arrears dict ---
        # (we populate included_arrears with arrears' contribution; existing entries get overwritten)
        for a in arrear_subjects_with_grades:
            code = a["code"]
            credits = float(a["credits"])
            gp = GRADE_POINTS.get(a["grade"], 0)
            ar_numerator = round(credits * gp, 3)
            st.session_state.included_arrears[code] = {
                "original_sem": a["original_sem"],
                "numerator": ar_numerator,
                "credits": round(credits, 3),
                "grade": a["grade"]
            }

        # --- REBUILD saved_numerators / saved_total_credits from raw_sem_totals + included_arrears ---
        for i in range(1, NUM_SEMS+1):
            key = f"sem{i}"
            base_num = float(st.session_state.raw_sem_totals.get(key, {}).get("numerator", 0.0))
            base_cred = float(st.session_state.raw_sem_totals.get(key, {}).get("credits", 0.0))
            # add arrear contributions that belong to this semester (original_sem == i)
            add_num = 0.0
            add_cred = 0.0
            for code2, info2 in st.session_state.included_arrears.items():
                if info2["original_sem"] == i:
                    add_num += float(info2.get("numerator", 0.0))
                    add_cred += float(info2.get("credits", 0.0))
            st.session_state.saved_numerators[key] = round(base_num + add_num, 3)
            st.session_state.saved_total_credits[key] = round(base_cred + add_cred, 3)

            # recompute and store the saved_gpas consistently (None if zero credits)
            if st.session_state.saved_total_credits[key] > 0:
                st.session_state.saved_gpas[key] = round(
                    st.session_state.saved_numerators[key] / st.session_state.saved_total_credits[key], 3
                )
            else:
                st.session_state.saved_gpas[key] = None

        st.success("Arrears recorded and applied to their original semester totals (CGPA will include them).")

    st.markdown("---")

# Edit subjects.json
with st.expander("View / Edit subjects JSON (advanced)"):
    st.write("Edit subjects per semester. Example structure: `{ 'sem1': [ {code,name,credits}, ... ], 'sem2': [...], ... }`")
    subj_text = st.text_area("subjects.json content", value=json.dumps(subjects_data, indent=2), height=300, key="subjects_json_editor")
    if st.button("Save subjects JSON"):
        try:
            new_data = json.loads(st.session_state.subjects_json_editor)
            save_subjects(new_data)
            st.success("Saved subjects.json — reload app to pick up new subjects.")
        except Exception as e:
            st.error(f"Invalid JSON: {e}")

# Show saved GPAs and compute CGPA using cumulative numerator/credits from sem 1 onwards
st.markdown("## Saved semester GPAs & CGPA (CGPA uses semesters from 1st onward)")
saved = st.session_state.saved_gpas
cols = st.columns(6)
for i in range(1, NUM_SEMS+1):
    cols[i-1].metric(label=f"Sem {i}", value=saved.get(f"sem{i}") if saved.get(f"sem{i}") is not None else "-")

# Compute CGPA using formula: (sum Ci*GPi) / (sum Ci), summing over semesters 1..NUM_SEMS
# Build base per-semester totals from raw_sem_totals if available, otherwise fall back to saved_numerators/saved_total_credits
base_nums = {}
base_creds = {}
for i in range(1, NUM_SEMS+1):
    key = f"sem{i}"
    if "raw_sem_totals" in st.session_state and st.session_state.raw_sem_totals.get(key) is not None:
        base_num = float(st.session_state.raw_sem_totals.get(key, {}).get("numerator", 0.0))
        base_cred = float(st.session_state.raw_sem_totals.get(key, {}).get("credits", 0.0))
    else:
        base_num = float(st.session_state.saved_numerators.get(key, 0.0))
        base_cred = float(st.session_state.saved_total_credits.get(key, 0.0))
    base_nums[key] = base_num
    base_creds[key] = base_cred

# Collect arrear selections from the current UI checkboxes (if any) so CGPA updates immediately based on what is ticked
arrears_from_ui = {}
for p in range(1, NUM_SEMS+1):
    p_key = f"sem{p}"
    p_subjects = subjects_data.get(p_key, [])
    for s in p_subjects:
        chk_key = f"arrear_{p_key}_{s['code']}"
        grade_key = f"arrear_grade_{p_key}_{s['code']}"
        if chk_key in st.session_state and st.session_state.get(chk_key):
            # a checkbox for this arrear is ticked in the UI — use the selected grade (if available)
            grade = st.session_state.get(grade_key)
            if grade:
                credits = float(s.get("credits", 0.0))
                gp = GRADE_POINTS.get(grade, 0)
                ar_num = round(credits * gp, 3)
                arrears_from_ui[s['code']] = {
                    "original_sem": p,
                    "numerator": ar_num,
                    "credits": round(credits, 3),
                    "grade": grade
                }

# Merge with stored included_arrears (UI selections override stored values)
final_arrears = dict(st.session_state.get("included_arrears", {}))
for code, info in arrears_from_ui.items():
    final_arrears[code] = info

# Persist the merged arrears so they remain available for future recalculations
st.session_state.included_arrears = final_arrears

# Add included arrears contributions into their original semester's base totals (this ensures CGPA includes them exactly once)
if final_arrears:
    for code, info in final_arrears.items():
        orig = int(info.get("original_sem", 0))
        if 1 <= orig <= NUM_SEMS:
            k = f"sem{orig}"
            base_nums[k] = base_nums.get(k, 0.0) + float(info.get("numerator", 0.0))
            base_creds[k] = base_creds.get(k, 0.0) + float(info.get("credits", 0.0))

# Now sum up for CGPA
numerator_sum = sum(base_nums.values())
credits_sum = sum(base_creds.values())

if credits_sum > 0:
    cgpa = round(numerator_sum / credits_sum, 3)
    cols[NUM_SEMS-1].metric(label="CGPA (cum from sem1)", value=cgpa)
    st.success(f"CGPA (cumulative from 1st semester) = {cgpa}")
    st.write(f"Cumulative numerator (Σ Ci*GPi) = {round(numerator_sum,3)}")
    st.write(f"Cumulative credits (Σ Ci) = {round(credits_sum,3)}")
    if final_arrears:
        st.write("Included arrears (currently assigned into original semesters):")
        for code, info in final_arrears.items():
            st.write(f"- {code} (orig sem {info['original_sem']}): grade {info['grade']}, credits {info['credits']}, numerator {info['numerator']}")
else:
    cols[NUM_SEMS-1].metric(label="CGPA (cum from sem1)", value="-")
    st.info("CGPA will be computed after you calculate and save grades for at least one semester.")

st.caption("Note: arrear contributions are now kept in included_arrears and always applied to their original semester totals when you calculate any semester. This guarantees CGPA includes them.")

