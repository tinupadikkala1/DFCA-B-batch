import streamlit as st

# Initialize session state for the input text
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

def parse_instruction(instr):
    instr = instr.strip()
    if not instr:
        return None
    normalized = instr.replace('$', ' $').replace(',', ' ')
    parts = normalized.split()
    if len(parts) < 1:
        return {'type': 'invalid'}
    op = parts[0]
    try:
        if op == 'add' or op == 'sub':
            if len(parts) < 4:
                return {'type': 'invalid'}
            rd, rs, rt = parts[1], parts[2], parts[3]
            return {'type': op, 'rd': rd, 'rs': rs, 'rt': rt}
        elif op == 'lw':
            if len(parts) < 2:
                return {'type': 'invalid'}
            rd = parts[1]
            return {'type': 'lw', 'rd': rd}
        elif op == 'sw':
            if len(parts) < 2:
                return {'type': 'invalid'}
            rs = parts[1]
            return {'type': 'sw', 'rs': rs}
        else:
            return {'type': 'unknown'}
    except Exception:
        return {'type': 'invalid'}

def count_stalls(parsed_instructions):
    stalls = 0
    for i in range(len(parsed_instructions) - 1):
        curr = parsed_instructions[i]
        nxt = parsed_instructions[i + 1]
        if curr['type'] == 'lw':
            loaded_reg = curr['rd']
            if nxt['type'] in ('add', 'sub'):
                if nxt['rs'] == loaded_reg or nxt['rt'] == loaded_reg:
                    stalls += 1
            elif nxt['type'] == 'sw':
                if nxt['rs'] == loaded_reg:
                    stalls += 1
    return stalls

# --- UI ---
st.set_page_config(page_title="MIPS Load-Use Hazard Detector", layout="centered")
st.title("🔍 MIPS Load-Use Hazard Detector")
st.markdown("""
Enter your MIPS program below (one instruction per line, up to 6 instructions).  
Include `END` on its own line to stop input.
""")

# Clear button: resets session state and forces refresh
if st.button("🗑️ Clear Inputs"):
    st.session_state.input_text = ""
    # No need for st.rerun() — next render will pick up empty state

# Text area tied to session state using 'value' and updating on change
user_input = st.text_area(
    "Enter instructions (e.g., lw$t0,0 → add$t2,$t0,$t3 → END)",
    value=st.session_state.input_text,
    height=200,
    key="instruction_input"  # important for state consistency
)

# Always sync session state with current widget value
st.session_state.input_text = user_input

# Analyze button
if st.button("Analyze Hazards"):
    lines = user_input.strip().split('\n')
    final_instructions = []
    for line in lines:
        clean = line.strip()
        if clean.upper() == "END":
            break
        if clean:
            final_instructions.append(clean)
        if len(final_instructions) >= 6:
            break

    parsed = []
    valid_raw = []
    for raw in final_instructions:
        p = parse_instruction(raw)
        if p and p['type'] not in ('invalid', 'unknown'):
            parsed.append(p)
            valid_raw.append(raw)
        else:
            st.warning(f"⚠️ Skipped invalid instruction: `{raw}`")

    total_stalls = count_stalls(parsed) if parsed else 0
    st.success(f"Total Stalls: {total_stalls}")

    with st.expander("Parsed Instructions"):
        if valid_raw:
            for raw, p in zip(valid_raw, parsed):
                st.write(f"`{raw}` → {p}")
        else:
            st.write("No valid instructions.")
