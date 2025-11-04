import streamlit as st

def parse_instruction(line):
    """
    Parse a single instruction line.
    Returns (opcode, reads_list, writes_list) or (None, [], []) if invalid.
    Opcodes must be lowercase: 'add', 'sub', 'lw', 'sw'
    """
    line = line.strip()
    if not line:
        return None, [], []
    
    # Normalize: insert space after '$' and split by spaces/commas
    normalized = line.replace('$', ' $').replace(',', ' ')
    parts = normalized.split()
    if not parts:
        return None, [], []
    
    op = parts[0]
    if op not in {'add', 'sub', 'lw', 'sw'}:
        return None, [], []
    
    try:
        if op == 'add' or op == 'sub':
            if len(parts) < 4:
                return None, [], []
            rd = parts[1]
            rs = parts[2]
            rt = parts[3]
            # Validate register format: e.g., '$t0'
            if not (rd.startswith('$t') and rs.startswith('$t') and rt.startswith('$t')):
                return None, [], []
            return op, [rs, rt], [rd]
        
        elif op == 'lw':
            if len(parts) < 3:
                return None, [], []
            rd = parts[1]
            if not rd.startswith('$t'):
                return None, [], []
            return op, [], [rd]
        
        elif op == 'sw':
            if len(parts) < 3:
                return None, [], []
            rs = parts[1]
            if not rs.startswith('$t'):
                return None, [], []
            return op, [rs], []
    
    except Exception:
        return None, [], []
    
    return None, [], []

def count_stalls(parsed_instructions):
    stalls = 0
    for i in range(1, len(parsed_instructions)):
        prev_op, _, prev_writes = parsed_instructions[i - 1]
        curr_op, curr_reads, _ = parsed_instructions[i]
        
        if prev_op == 'lw' and prev_writes:
            loaded_reg = prev_writes[0]
            if loaded_reg in curr_reads:
                stalls += 1
    return stalls

def main():
    st.set_page_config(page_title="MIPS Load-Use Hazard Detector", layout="centered")
    st.title("🔍 MIPS Load-Use Hazard Detector")
    st.markdown("""
    Enter up to **6 MIPS instructions** (one per line).  
    Only these lowercase instructions are supported: `add`, `sub`, `lw`, `sw`.  
    Example: `lw $t0, 0` or `add$t1,$t0,$t2`  
    Type `END` to stop early.  
    The tool detects **Load-Use hazards** and counts **stall cycles**.
    """)

    # Session state for input clearing
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""

    def clear_inputs():
        st.session_state.input_text = ""

    # Input text area
    user_input = st.text_area(
        "Enter your MIPS code:",
        value=st.session_state.input_text,
        height=180,
        key="code_input"
    )

    # Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        analyze = st.button("Analyze Stalls")
    with col2:
        st.button("Clear Inputs", on_click=clear_inputs)

    if analyze:
        lines = user_input.strip().split('\n')
        parsed_instructions = []
        instruction_count = 0

        for line in lines:
            if instruction_count >= 6:
                break
            stripped = line.strip()
            if stripped.upper() == "END":
                break
            if not stripped:
                continue

            op, reads, writes = parse_instruction(stripped)
            if op is not None:
                parsed_instructions.append((op, reads, writes))
                instruction_count += 1
            # Skip invalid/malformed lines (do not count toward 6)

        total_stalls = count_stalls(parsed_instructions)
        st.success(f"Total Stalls: {total_stalls}")

        # Debug info (optional)
        with st.expander("Show parsed instructions"):
            for i, (op, reads, writes) in enumerate(parsed_instructions):
                st.code(f"{i+1}: op='{op}', reads={reads}, writes={writes}")

if __name__ == "__main__":
    main()