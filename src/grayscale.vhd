library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all; 

entity grayscale is
    generic ( N : natural := 8 );
    port(
        reset, clk              : in  std_ulogic;
        R, G, B, WR, WG, WB     : in  std_ulogic_vector(N-1 downto 0);
        RGB_valid               : in  std_ulogic;
        Y                       : out std_ulogic_vector(N-1 downto 0);     
        overflow, Y_valid       : out std_ulogic;

        -- signal used to indicate that the pipeline is filled
        -- (very handy when pipelines are tens of stages deep)
        valid                   : out std_ulogic
    );
end entity grayscale;


architecture RTL of grayscale is
    signal next_Y, r_Y                                                  : u_unsigned(N-1 downto 0);
    signal next_valid, mid_valid, r_valid, next_overflow, r_overflow    : std_ulogic;

    -- signals used as "queue lanes"
    signal n_R, n_G, n_B                                    : unsigned(2*N-1 downto 0);

    -- signals used to stall the pipeline
    signal mul_ready, calc_ready                            : std_ulogic;
begin
    -- output from registers
    Y        <= std_logic_vector(r_Y);
    overflow <= r_overflow;
    Y_valid  <= r_valid and calc_ready;

    valid   <= calc_ready;

    -- multiplication stage
    ST_MUL: process(all) is
        variable i_R, i_G, i_B : u_unsigned(2*N-1 downto 0);
    begin
        if rising_edge(clk) then
            if reset = '1' then
                mul_ready <= '0';
            else
                i_R := unsigned(WR) * unsigned(R);
                i_G := unsigned(WG) * unsigned(G);
                i_B := unsigned(WB) * unsigned(B);

                n_R <= i_R;
                n_G <= i_G;
                n_B <= i_B;

                -- valid signal must be queued
                mid_valid <= RGB_valid;

                mul_ready <= '1';
            end if;
        end if;
    end process;

    -- next-state calculation logic
    ST_CALC: process(all) is
        variable i_sum      : u_unsigned(2*N+1 downto 0);
        variable i_overflow : std_ulogic;
    begin
        if rising_edge(clk) then
            if reset = '1' then
                calc_ready <= '0';
            elsif mul_ready = '1' then
                i_sum := unsigned("00" & n_R) + unsigned("00" & n_G) + unsigned("00" & n_B);
                i_overflow := or(i_sum(i_sum'left downto i_sum'left-1));

                next_Y <= (others => '1') when i_overflow else i_sum(2*N-1 downto N);
                next_overflow <= i_overflow;
                next_valid <= mid_valid;

                calc_ready <= '1';
            end if;
        end if;
    end process;

    -- register assignment process
    ST_MEM: process(clk, calc_ready) is  
    begin 
        if rising_edge(clk) then 
            if reset = '1' then 
                r_Y        <= (others => '0');
                r_valid    <= '0';
                r_overflow <= '0';
            elsif calc_ready = '1' then
                r_Y         <= next_Y;
                r_valid     <= next_valid;
                r_overflow  <= next_overflow;
            end if;
        end if;
    end process; 
end architecture RTL;
