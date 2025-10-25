import streamlit as st

def parse_instruction(instr):
    """Parse a single instruction string into structured dict."""
    if not instr:
        return None
    # Normalize: insert space before '$' and split by commas/spaces
    normalized = instr.replace('$', ' $').replace(',', ' ')
    parts = normalized.split()
    if not parts:
        return None
    op = parts[0]
    try:
        if op == 'add' or op == 'sub':
            rd, rs, rt = parts[1], parts[2], parts[3]
            return {'type': op, 'rd': rd, 'rs': rs, 'rt': rt}
        elif op == 'lw':
            rd = parts[1]
            return {'type': 'lw', 'rd': rd}
        elif op == 'sw':
            rs = parts[1]
            return {'type': 'sw', 'rs': rs}
        else:
            return {'type': 'unknown'}
    except IndexError:
        return {'type': 'invalid'}

def count_stalls(parsed_instructions):
    stalls = 0
    n = len(parsed_instructions)
    for i in range(n - 1):
        curr = parsed_instructions[i]
        next_instr = parsed_instructions[i + 1]
        if curr['type'] == 'lw':
            loaded_reg = curr['rd']
            # Check if next instruction reads loaded_reg
            reads_it = False
            if next_instr['type'] in ('add', 'sub'):
                if next_instr['rs'] == loaded_reg or next_instr['rt'] == loaded_reg:
                    reads_it = True
            elif next_instr['type'] == 'sw':
                if next_instr['rs'] == loaded_reg:
                    reads_it = True
            if reads_it:
                stalls += 1
    return stalls

# Streamlit UI
st.set_page_config(page_title="MIPS Load-Use Hazard Detector", layout="centered")
st.title("🔍 MIPS Load-Use Hazard Detector")
st.markdown("""
This tool analyzes a sequence of up to 6 simplified MIPS instructions  
and counts **stall cycles** caused by **Load-Use data hazards**.
""")

# Instruction inputs
instructions = []
st.subheader("Enter Instructions (max 6)")
cols = st.columns(6)
for i in range(6):
    instr = cols[i].text_input(f"Instruction {i+1}", key=f"instr_{i}", placeholder="e.g., lw$t0,0")
    if instr:
        instructions.append(instr)

# Early END option
if st.checkbox("✅ Stop early (simulate 'END')"):
    pass  # We'll just use non-empty instructions

# Remove empty strings
instructions = [instr.strip() for instr in instructions if instr.strip()]

# Validate: only allow up to 6, and stop at first empty (simulate END)
final_instructions = []
for instr in instructions:
    if instr.upper() == "END":
        break
    final_instructions.append(instr)
    if len(final_instructions) >= 6:
        break

# Process
if st.button("Analyze Hazards"):
    if not final_instructions:
        st.success("Total Stalls: 0")
    else:
        # Parse
        parsed = []
        valid_instructions = []
        for instr in final_instructions:
            p = parse_instruction(instr)
            if p and p['type'] != 'invalid':
                parsed.append(p)
                valid_instructions.append(instr)
            else:
                st.warning(f"⚠️ Skipping invalid instruction: `{instr}`")

        if not parsed:
            st.success("Total Stalls: 0")
        else:
            stalls = count_stalls(parsed)
            st.success(f"Total Stalls: {stalls}")

            # Optional: show debug info
            with st.expander("View parsed instructions"):
                for i, (raw, p) in enumerate(zip(valid_instructions, parsed)):
                    st.write(f"{i+1}. `{raw}` → {p}")