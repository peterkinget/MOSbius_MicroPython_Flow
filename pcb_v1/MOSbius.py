# PK is making changes on 2025-02-23 
import time

class mosbius_mk1:
    # Constants defining the number of buses and registers
    NO_BUSES = 10
    NO_REGISTERS = 65
    
    # Clock cycle time in microseconds
    T_CLK_HALF_CYCLE_US = 10
    
    # List of valid pin numbers (excluding programming pins 2, 3, and 4)
    VALID_PIN_ENUM = [1] + list(range(5, NO_REGISTERS + 4))
    
    def __init__(self, pin_en=None, pin_clk=None, pin_data=None):
        # Initialize an empty bitstream
        self.bitstream = [0] * self.NO_BUSES * self.NO_REGISTERS 
        # Assign GPIO pin objects
        self.pin_en = pin_en
        self.pin_clk = pin_clk
        self.pin_data = pin_data
 
    def convert_pcb_pin_to_register(self, pin):
        """Convert a PCB pin number to the corresponding register index."""
        if pin == 1:
            register = 1
        else:
            register = pin - 3  # Skip EN, CLK, and DATA pins
        return register

    def convert_register_to_pcb_pin(self, register):
        """Convert a register index to the corresponding PCB pin number."""
        if register == 1:
            pin = 1
        else:
            pin = register + 3  # Skip EN, CLK, and DATA pins
        return pin

    def create_bitstream(self, dict_connections):
        """Generate the bitstream based on a dictionary of bus-to-pin connections."""
        self.bitstream = [0] * self.NO_BUSES * self.NO_REGISTERS  # Reset bitstream
        
        for bus in range(1, self.NO_BUSES + 1):
            if f'{bus}' in dict_connections:
                pin_list = dict_connections[f'{bus}']
            else:
                # PK change: if bus is not listed, than just keep empty
                # raise ValueError(f'JSON file error: missing bus entry {bus}.')
                pin_list = []
                
            for pin in pin_list:
                if pin in self.VALID_PIN_ENUM:
                    register = self.convert_pcb_pin_to_register(pin)
                    bit_addr = (bus - 1) * self.NO_REGISTERS + (register - 1)
                    self.bitstream[bit_addr] = 1
                else:
                    raise ValueError(f'JSON file error: invalid MOSbius Pin Number {pin}.')

    def program_bitstream(self):
        """Program the bitstream to the hardware via GPIO pins."""
        print('Programming bitstream')
        
        if self.pin_en is None:
            print('Warning: GPIO pins not initialized. Abort programming.')
            return

        # Initialize GPIO pin states
        self.pin_data.value(0)
        self.pin_clk.value(0)
        self.pin_en.value(0)
        
        for k in reversed(range(len(self.bitstream))):
            bit = self.bitstream[k]
            self.pin_data.value(bit)
            
            # Toggle clock signal
            self.pin_clk.value(1)
            time.sleep_us(self.T_CLK_HALF_CYCLE_US)
            self.pin_clk.value(0)
            time.sleep_us(self.T_CLK_HALF_CYCLE_US)

        self.pin_en.value(1)  # Enable programming
        print('Programming completed')
        
    def export_bitstream_to_csv(self):
        """Export the generated bitstream to a CSV file for debugging or external use."""
        print('Exporting bitstream')
        
        with open("bitstream.csv", "w") as file:
            file.write('0,0,0\n')  # Initial state
        
            for k in reversed(range(len(self.bitstream))):
                bit = self.bitstream[k]
                file.write(f'0,1,{bit}\n')
                file.write(f'0,0,{bit}\n')
                
            file.write('1,0,0\n')  # Final state
        
        print('Export completed')
        
    def display_connections(self):
        """Print a visual representation of bus-to-pin connections."""
        print('Connections:')
        print('    BUS    ', end='')
        for bus in range(1, self.NO_BUSES + 1):
            print(f'{bus} ', end='')
        print('')
        
        for register in range(1, self.NO_REGISTERS + 1):
            pin = self.convert_register_to_pcb_pin(register)
            print(f'    PIN {pin:02} ', end='')
            for bus in range(1, self.NO_BUSES + 1):
                bit_addr = (bus - 1) * self.NO_REGISTERS + (register - 1)
                if self.bitstream[bit_addr]:
                    print('X ', end='')  # Mark active connections
                else:
                    print('| ', end='')  # Mark inactive connections
            print('')

    def print_connections(self):
        """Prints a list of active connections for each bus."""
        print('Connections:')
        for bus in range(1, self.NO_BUSES + 1):
            print(f'    BUS{bus}: [ ', end='')
            for register in range(1, self.NO_REGISTERS + 1):
                bit_addr = (bus - 1) * self.NO_REGISTERS + (register - 1)
                if self.bitstream[bit_addr]:
                    pin = self.convert_register_to_pcb_pin(register)
                    print(f'{pin:02} ', end='')
            print(']')
