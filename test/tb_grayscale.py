# Grayscale testbench- Uses an image as input. Output is scaled down to optimize runtime. 
# Weights should sum to 255, feel free to change image, weights, and scaling 
# Parts of the testbench will require modification when making a pipelined module. 

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly
from cocotb.clock import Clock
import os

# If not installed, use pip install Pillow. WSL has Pillow installed
# https://pillow.readthedocs.io/en/stable/reference/Image.html 
from PIL import Image

CLOCK_PERIOD_NS = 10

# Downscale image output to make simulation run faster.
SCALING = 8      # 1 renders full image size.

async def reset_dut(dut):
    await FallingEdge(dut.clk)
    dut.reset.value      = 1
    dut.R.value = 0
    dut.G.value = 0
    dut.B.value = 0
    dut.RGB_valid.value = 0
    dut.WR.value = 76
    dut.WG.value = 150
    dut.WB.value = 29
    await RisingEdge(dut.clk)
    dut.reset.value = 0

''' STIMULI '''
async def stimuli_generator(dut, img):
    width = int(img.width/SCALING)
    height = int(img.height/SCALING)
    await FallingEdge(dut.clk)
    dut.RGB_valid.value = 1
    for j in range(height):
        for i in range(width):
           xy = (i*SCALING, j*SCALING)
           RGB = img.getpixel(xy)
           dut.R.value = RGB[0]
           dut.G.value = RGB[1]
           dut.B.value = RGB[2]
           await FallingEdge(dut.clk)
    dut.RGB_valid.value = 0

    
''' MONITORS and checks '''
async def overflow_check(dut):
    while True:
        await RisingEdge(dut.overflow)
        assert False, "Overflow has occured"
        
async def gray_check(dut):
    while True:
        await RisingEdge(dut.clk)
        await ReadOnly()
        CheckR = dut.WR.value.to_unsigned() * dut.R.value.to_unsigned()
        CheckG = dut.WG.value.to_unsigned() * dut.G.value.to_unsigned()
        CheckB = dut.WB.value.to_unsigned() * dut.B.value.to_unsigned()
        if dut.Y_valid.value == True:
            CheckGray = (CheckR+CheckG+CheckB)>>8
            assert CheckGray == int(dut.Y.value), (
                f"Model value: {CheckGray} != simulated value: {int(dut.Y.value)} ")

async def valid_check(dut):
    while True:
        await FallingEdge(dut.clk)
        await ReadOnly()
        data_valid = dut.RGB_valid.value
        await RisingEdge(dut.clk)
        await ReadOnly()
        assert data_valid == dut.Y_valid.value, "Y_valid does not follow RGB_ready"
        

async def monitor(dut):
    cocotb.start_soon(overflow_check(dut))
    cocotb.start_soon(gray_check(dut))
    cocotb.start_soon(valid_check(dut))

async def grayscale_builder(dut, gray):
    for j in range(gray.height):
      for i in range(gray.width):
        await RisingEdge(dut.clk)
        await ReadOnly()
        if dut.Y_valid.value == True:
            Y_value = int(dut.Y.value)
            gray.putpixel((i,j), Y_value)
        else:    
          i= i-1

''' @cocotb test starts everything '''
@cocotb.test()
async def main_test(dut):
    dut._log.info("### Opening image ###")
    img = Image.open('images/mc.jpg')
    width = int(img.width/SCALING)
    height = int(img.height/SCALING)
    gray = Image.new('L', (width, height)) # L for Luma = grayscale has only 1 value per pixel

    dut._log.info("### Starting test ###")
    cocotb.start_soon(Clock(dut.clk, CLOCK_PERIOD_NS, unit='ns').start())
    await reset_dut(dut)
    cocotb.start_soon(monitor(dut))
    cocotb.start_soon(grayscale_builder(dut, gray))
    await stimuli_generator(dut, img);
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut._log.info("### Test finished, saving grayscale image ###")
    
    img.close()
    if not os.path.isdir('./output'):
        os.mkdir('./output')  
    gray.save("output/grayscale.png")
    dut._log.info("### Grayscale image saved to output folder ###")
    gray.close()
    
