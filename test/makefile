# Makefile

# defaults
SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl

# VHDL 2008
EXTRA_ARGS +=--std=08

# TOPLEVEL is the name of the toplevel module in your VHDL file
TOPLEVEL = grayscale


#VHDL_SOURCES += $(PWD)/../src/$(TOPLEVEL).vhd
VHDL_SOURCES += $(PWD)/../src/*.vhd

# SIM_ARGS is Simulation arguments. --wave determines name and type of waveform  
SIM_ARGS +=--wave=$(TOPLEVEL).ghw


# -g<GENERIC> is used to set generics defined in the toplevel entity
SIM_ARGS +=-gN=8

# MODULE is the basename of the Python test file
MODULE = tb_$(TOPLEVEL)

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

# removing generated binary of top entity and .o-file on make clean
clean::
	-@rm -f $(TOPLEVEL)
	-@rm -f e~$(TOPLEVEL).o
