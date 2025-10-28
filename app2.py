import streamlit as st

def parse_instruction(line):
    """Parse a single instruction and return (opcode, reads, writes)"""
    line = line.strip()
    if not line:
        return None, [], []
    parts = line.replace(',', ' ').split()
    if not parts:
        return None, [], []
    opcode = parts[0]
    if opcode == 'add' or opcode == 'sub':
        if len(parts) < 4:
            return None, [], []
        rd = parts[1]
        rs = parts[2]
        rt = parts[3]
        return opcode, [rs, rt], [rd]
    elif opcode == 'lw':
        if len(parts) < 3:
            return None, [], []
        rd = parts[1]
        return opcode, [], [rd]
    elif opcode == 'sw':
        if len(parts) < 3:
            return None, [], []
        rs = parts[1]
        return opcode, [rs], []
    else:
        return None, [], []

def count_stalls(instructions):
    """Count Load-Use stalls in a list of parsed instructions"""
    stalls = 0
    n = len(instructions)
    for i in range(1, n):
        prev_op, _, prev_writes = instructions[i - 1]
        curr_op, curr_reads, _ = instructions[i]

        # Only consider if previous was 'lw' and wrote a register
        if prev_op == 'lw' and prev_writes:
            loaded_reg = prev_writes[0]
            if loaded_reg in curr_reads:
                stalls += 1
    return stalls

def main():
    st.set_page_config(page_title="MIPS Load-Use Hazard Detector", layout="centered")
    st.title("MIPS Load-Use Hazard Detector")
    st.markdown("""
    Enter up to **6 MIPS instructions** (one per line).  
    Supported: `add`, `sub`, `lw`, `sw` (e.g., `lw $t0, 0`).  
    Type `END` to stop early.  
    The program detects **Load-Use hazards** and counts **stall cycles**.
    """)

    # Use session state to manage input clearing
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""

    def clear_inputs():
        st.session_state.input_text = ""

    # Text area for input
    user_input = st.text_area(
        "Enter your MIPS code:",
        value=st.session_state.input_text,
        height=200,
        key="code_input"
    )

    # Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        run = st.button("Analyze Stalls")
    with col2:
        st.button("Clear Inputs", on_click=clear_inputs)

    if run:
        lines = user_input.strip().split('\n')
        instructions = []
        for line in lines:
            if line.strip().upper() == "END":
                break
            if len(instructions) >= 6:
                break
            op, reads, writes = parse_instruction(line)
            if op is None:
                continue  # Skip empty or malformed lines
            instructions.append((op, reads, writes))

        total_stalls = count_stalls(instructions)
        st.success(f"Total Stalls: {total_stalls}")

        # Optional: Show parsed instructions for debugging
        with st.expander("Parsed Instructions (for debugging)"):
            for i, (op, reads, writes) in enumerate(instructions):
                st.write(f"{i+1}: {op} | Reads: {reads} | Writes: {writes}")

if __name__ == "__main__":
    main()
