import streamlit as st

def parse_instruction(instr):
    """Parse a single instruction string (e.g., 'lw$t0,0') into a structured dict."""
    instr = instr.strip()
    if not instr:
        return None
    # Fix: insert space before '$' to split opcode from register
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
            # Check if next instruction reads this register
            if nxt['type'] in ('add', 'sub'):
                if nxt['rs'] == loaded_reg or nxt['rt'] == loaded_reg:
                    stalls += 1
            elif nxt['type'] == 'sw':
                if nxt['rs'] == loaded_reg:
                    stalls += 1
    return stalls

# Streamlit UI
st.set_page_config(page_title="MIPS Load-Use Hazard Detector", layout="centered")
st.title("🔍 MIPS Load-Use Hazard Detector")
st.markdown("""
Enter your MIPS program below (one instruction per line, up to 6 instructions).  
Include `END` on its own line to stop input (as per the lab spec).
""")

# Single multi-line input
user_input = st.text_area(
    "Enter instructions (e.g., lw$t0,0 → add$t2,$t0,$t3 → END)",
    height=200,
    placeholder="lw$t0,0\nadd$t2,$t0,$t3\nEND"
)

if st.button("Analyze Hazards"):
    lines = user_input.strip().split('\n')
    final_instructions = []
    for line in lines:
        clean_line = line.strip()
        if clean_line.upper() == "END":
            break
        if clean_line:  # skip empty lines
            final_instructions.append(clean_line)
        if len(final_instructions) >= 6:
            break

    # Parse valid instructions
    parsed = []
    valid_raw = []
    for raw in final_instructions:
        p = parse_instruction(raw)
        if p and p['type'] not in ('invalid', 'unknown'):
            parsed.append(p)
            valid_raw.append(raw)
        else:
            st.warning(f"⚠️ Skipped invalid instruction: `{raw}`")

    # Count stalls
    total_stalls = count_stalls(parsed) if parsed else 0
    st.success(f"Total Stalls: {total_stalls}")

    # Optional debug view
    with st.expander("Parsed Instructions"):
        if valid_raw:
            for raw, p in zip(valid_raw, parsed):
                st.write(f"`{raw}` → {p}")
        else:
            st.write("No valid instructions.")
