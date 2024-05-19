# AutoVerilog

An auto flow for VCS+Verdi+DC

## Configuration

1. **Virtual Machine Requirements:**
   
   - Python 3
   
2. **Modifications in `newone.py`:**
   
   - **Lines 172-175:** Modify the library paths
     
     ```python
     set DESIGN_PATH "/home/summer/Synopsys/syn/FreePDK/FreePDK45/osu_soc/lib/files"
     set search_path "$search_path $DESIGN_PATH"
     set target_library "gscl45nm.db"
     set link_library "* $target_library"
     ```
   - **Lines 238-239:** Update the reset and clock names
     
     ```python
     set RST_NAME "rst_n"
     set CLK_NAME "clk"
     ```

## Usage

1. **Creating a New Project:**
   
   - Run the following command to create a new project. The `top_module_name` will also be the name of the subdirectory.
     ```bash
     python3 newone.py [top_module_name]
     ```
   
2. **Primary Commands within the Project:**
   
   - **Compile and Simulate:**
     
     ```bash
     make compile
     # This deletes cache and executes VCS simulation.
     ```
   - **View Waveforms:**
     
     ```bash
     make verdi
     ```
   - **Perform Logic Synthesis:**
     ```bash
     make syn
     # This opens Design Compiler (dc) to perform logic synthesis.
     ```

## Demo

The file `Demo` is a well-done counter by Verilog. You could check the settings thought it
