from shock_collar.shock_collar_config import *
import time
import pigpio

class Shock():
    
    def __init__(self):
        
        self.Tx = 17
        self.key = key_
        self.pi = pigpio.pi() # set the 'pi' variable to mean wean we need to access LOCAL pi
        self.pi.set_mode(self.Tx, pigpio.OUTPUT)
        
        if len(self.key) != 16:
            self.key = '0101101101000100'

    #string transmission module
    def transmitter(self, sequence, time_):

        self.pi.wave_clear() # clear existing waveforms

        sequence_wave=[]

        # define times
        start_bit = 840
        start_delay = 800
        bit_duration = 190
        zero_delay = 750
        one_delay = 1500
        EOS_delay = 7600

        sequence_wave.append(pigpio.pulse(1<<self.Tx, 0, start_bit))
        sequence_wave.append(pigpio.pulse(0, 1<<self.Tx, start_delay))

        for x in range(0, 41): #adds the sequence bits to the waveform, in order.
            if int(sequence[x]) == 0:
                sequence_wave.append(pigpio.pulse(1<<self.Tx, 0, bit_duration)) ## fix
                sequence_wave.append(pigpio.pulse(0, 1<<self.Tx, zero_delay))
            else:
                sequence_wave.append(pigpio.pulse(1<<self.Tx, 0, bit_duration)) ## fix
                sequence_wave.append(pigpio.pulse(0, 1<<self.Tx, one_delay))

        sequence_wave.append(pigpio.pulse(0, 0, EOS_delay))
        self.pi.wave_add_generic(sequence_wave)
        waveID = self.pi.wave_create() #save the completed wave and send wave ID to var
        
        self.pi.wave_send_using_mode(waveID, pigpio.WAVE_MODE_REPEAT)
        time.sleep(time_)
        self.pi.wave_tx_stop() # stop waveform

        self.pi.wave_clear() # clear all waveforms

        self.pi.write(self.Tx, 0)
        print("transmission done")


    def transmit(self, mode_,power_,time_=.5,channel_=1):

        print("transmitting now...")
        

        if int(power_) < 3 and mode_ is not 2:
            power_ = 3

        power_binary = '{0:08b}'.format(int(power_))


        if channel_ == 2:
            channel_sequence = '1110'
            channel_sequence_inverse = '0001'
        else: 
            channel_sequence = '1000'
            channel_sequence_inverse = '1110'

        if mode_ == 1:
            ## flash the light on the collar. 
            mode_sequnce = '1000'
            mode_sequnce_inverse = '1110'
        elif mode_ == 3:
            ## vibrate the collar
            mode_sequnce = '0010'
            mode_sequnce_inverse = '1011'
        elif mode_ == 4:
            #shock the collar 
            mode_sequnce = '0001'
            mode_sequnce_inverse = '0111'
        elif mode_ == 2:
            mode_sequnce = '0100'
            mode_sequnce_inverse = '1101' 
        else:
            #mode = 2
            ## beep the collar. it was done like this so the 'else' is a beep, not a shock for safety. 
            mode_sequnce = '0100'
            mode_sequnce_inverse = '1101'


        key_sequence = self.key
        
        sequence = channel_sequence + mode_sequnce + key_sequence + power_binary + mode_sequnce_inverse + channel_sequence_inverse + "0"
        print(sequence)
        while self.pi.wave_tx_busy(): # wait for prior waveform to be sent
            time.sleep(0.2)
        self.transmitter(sequence,time_)
