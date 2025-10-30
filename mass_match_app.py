import streamlit as st
import itertools

# --- Title ---
st.title("🧮 Mass Match Finder")
st.markdown("Enter a target mass, tolerance, and choose which combinations to run.")

# --- Input ---
target = st.number_input("🎯 Target number to match", format="%.5f")
tolerance = st.number_input("🎯 Acceptable error/tolerance (e.g., 0.1)", value=0.1, format="%.5f")

# --- Data Lists ---
data_lists = {
    "Linear": [
        174.058, 197.084, 127.063, 147.055, 87.055,
        200.095, 170.113, 207.113, 114.042, 114.042,
        101.047, 129.042, 131.040
    ],
    "Cyclic": [
        173.051, 197.084, 127.063, 147.055, 87.055,
        200.095, 170.113, 207.113, 114.042, 114.042,
        101.047, 129.042, 130.032
    ]
}

# --- User selection for main list ---
selected_list_name = st.selectbox("Select the dataset to use:", list(data_lists.keys()))
selected_list = data_lists[selected_list_name]
sum_selected = sum(selected_list)

# --- Secondary List (List2) ---
list2_raw = [
    174.058, 173.051, 197.084, 127.063, 147.055,
    87.055, 200.095, 170.113, 207.113, 114.042,
    101.047, 129.042, 130.032, 131.040, 42.010,
    0.984, 2.015, '+71.037', '+242.109', '+56.06', '-15.977', '+252.082',
    '+230.11', '-18.010', '-14.015', '-17.026',
    '+100.05', '+222.06', '-33.987', '-1.007', '+1896.83'
]

# --- Split into + and - groups ---
list2_add, list2_sub = [], []
for item in list2_raw:
    if isinstance(item, str):
        if item.startswith('+'):
            list2_add.append(float(item[1:]))
        elif item.startswith('-'):
            list2_sub.append(float(item[1:]))
    else:
        list2_add.append(item)
        list2_sub.append(item)

# --- Custom result names ---
custom_names = {
    "Linear + (1896.83,)": "Linear_Dimer",
    "Linear + (56.06,)": "Linear + tBu",
    "Cyclic + (1896.83,)": "Cyclic_Dimer",
    "Cyclic + (0.984,)": "Cyclic_Deamination"
}

# --- Combination Type Toggles ---
st.subheader("⚙️ Choose which combination types to include:")
run_main_only = st.checkbox(f"{selected_list_name} only", True)
run_additions = st.checkbox(f"{selected_list_name} + additions", True)
run_subtractions = st.checkbox(f"{selected_list_name} - subtractions", True)
run_sub_add = st.checkbox(f"{selected_list_name} - sub + add combinations", True)
run_list2_only = st.checkbox("List2 only combinations", False)

# --- Helper functions ---
def within_tolerance(value):
    return abs(value - target) <= tolerance

def add_result(description, value, steps, results):
    if within_tolerance(value):
        error = abs(value - target)
        if description in custom_names:
            description += f" = {custom_names[description]}"
        results.append((len(steps), error, description, value, error))

# --- Calculation ---
results = []

if run_main_only:
    add_result(f"{selected_list_name} only", sum_selected, [], results)

if run_additions:
    for r in range(1, 4):
        for combo in itertools.combinations_with_replacement(list2_add, r):
            value = sum_selected + sum(combo)
            add_result(f"{selected_list_name} + {combo}", value, combo, results)

if run_subtractions:
    for r in range(1, 4):
        for combo in itertools.combinations(list2_sub, r):
            value = sum_selected - sum(combo)
            add_result(f"{selected_list_name} - {combo}", value, combo, results)

if run_sub_add:
    for sub in list2_sub:
        for add in list2_add:
            if sub == add:
                continue
            value = sum_selected - sub + add
            add_result(f"{selected_list_name} - ({sub},) + ({add},)", value, [sub, add], results)

if run_list2_only:
    all_list2 = list2_add + [-v for v in list2_sub]
    for r in range(2, 6):
        for combo in itertools.combinations_with_replacement(all_list2, r):
            value = sum(combo)
            add_result(f"List2 only {combo}", value, combo, results)

# --- Results display ---
st.divider()
if results:
    st.success(f"Found {len(results)} matching combinations within ±{tolerance:.5f}")
    for _, _, desc, val, error in sorted(results, key=lambda x: (x[0], x[1])):
        st.write(f"🔹 `{desc}` = **{val:.5f}** (error: {error:.5f})")
else:
    st.warning("No matches found with current settings.")
