'''
Created on 12 abr. 2020

@author: David
'''

import sys
sys.path.append("/flash/userapp")


from utime import sleep_ms
from uvacbot.ui.buzzer import Buzzer, Sequencer


if __name__ == '__main__':
    
    from pyb import Pin
    
    def beep():
        
        b = Buzzer(Pin.board.D12, 3, 1)
        try:
            
            b.buzz(220.0, 250)
            sleep_ms(500)
            b.trill(220.0, 250)
            sleep_ms(500)
            b.trill(220.0, 250, 10, 5)
            sleep_ms(500)
            b.trill(220.0, 250, 5, 10)
            sleep_ms(500)
            
            b.slide(220.0, 440.0, 500)
            b.slide(440.0, 220.0, 500)
            b.slide(220.0, 440.0, 500)
            b.slide(440.0, 220.0, 500)
            sleep_ms(250)
            b.slide(880.0, 1760.0, 500)

        finally:
            b.cleanup()
        
        
    def playScore():
        
        '''
        seq = "4 Caf"
        seq += "(2c4cde3ffed2e4 $bge1c4 cde)3ggfg2a4 Caf"
        seq += "(2c4cde3ffed2e4 $bge1c4 cde)3fe2f4 cfc"
        seq += "(2f4 cfc2f4 ffg3aa$ba2g4 cgc2g4cgc2g4 gga3$b$b)C$b2a4 cfc"
        seq += "(2f4 cfc2f4 ffg3aa$ba2g4 cgc2g4cgc2g4 gga3$b$b)3ag2f4 fga"
        seq += "(2$b_4$b$bC$b2a4 a$ba2g_4gefg2a"
        seq += "4 fga2$b_4$b$bC$b2a4 a$ba3.C4$b3ag)"
        seq += "2f4 fga"
        seq += "(2$b_4$b$bC$b2a4 a$ba2g_4gefg2a"
        seq += "4 fga2$b_4$b$bC$b2a4 a$ba3.C4$b3ag)"
        seq += "f c f 3 "
        '''
        
        #From https://musescore.com/alvarobuitrago/entradilla-castellana
        '''
        seq = "5DCbC4D EDCbag3C.g 4 de#f_e#fde#fga#fe#f3.d4g_a"
        seq += "#f_e#fde#fga3.#f_.#f4ag#fed3e4d3a.d4/g_#f_e4_d3a.e_.e4e#f"
        seq += "(aaaaaaaa$b$b$b$b$b$b5DC4baaaaaa5C$b4agggggg5$ba4g#f3d_.d4d#f)"
        seq += "(aaaaaaaa$b$b$b$b$b$b5DC4baaaaaa5C$b4agggggg5$ba4g#f3d_.d4de)"
        seq += "#fe#fde#fga#f_e#f3.d4g_a"
        seq += "#fe#fde#fga3.#f_.#f4ag#f_ed3e4d3a.d4/g_#f_e4_d3a"
        seq += "d4a/$b_C_$b4a/$b_C_$b"
        seq += "(4a#fd/$bC$b4a/$bC$b3.a4/D_C_b_4a/b_C_b4a#fd/g_#f_e4d/a_b_a"
        seq += "3d4a/$b_C_$b4a/$b_C_$b)"
        seq += "(4a#fd/$bC$b4a/$bC$b3.a4/D_C_b_4a/b_C_b4a#fd/g_#f_e4d/a_b_a"
        seq += "3.d4/gae4e/aba)"
        seq += "3.d4abCbabagg#fga$b"
        seq += "3.a4ga$baga#fd/g#fe4d/aba3.d4/g#fe4d/aba3.d4ddgdg"
        seq += "(4babggb#fed3d4gdgbabgba3.g4ddgdg)"
        seq += "(4babggb#fed3d4gdgbabgba3.g4ggabC)DbCDE#F5G#F4EDbCDE#F5G#F4E3D4D_3.G5#FG#FE"
        seq += "3.D4CECaCbDbgba#fa3.g4ggabCDbCDE#F5G#F4E3.D4EDCba"
        seq += "bDbgba#fa3.g_.g4de#f_e#fde#fga#f_e#f3.d4g_a#fe#fde#fga"
        seq += "3.#f_.#f4ag#fed3e4d3a.d4/g#fe4d3a.d_d 4 "
        seq += "(4DDDDbCDECabCabCDbgabC|3.a_.a_a)"
        seq += "(4DDDDbCDECabCabCDbgabC|3.a_.a4d#f)"
        seq += "3a4d3a4dad3a4d3a4dad"
        seq += "3.a_.a4d#f3b4g3b4gbg3a4d3a4dad3b4g3b4gbg3.a_.a4de#fd#fde#fga"
        seq += "4#f_e#f3.d4ga#fe#fde#fga3.#f_.#f4ag#fed3e4d3a.d4/g#fe4d3a"
        seq += ".d4CECEC(4DbgCECEC3.D4CECECDgabDCa#f|3.g4CECEC)"
        seq += "(4DbgCECEC3.D4CECECDgabDCa#f|3.g.g4de)#fe#fde#fga#fe#f3.d4ga#fe#fde#fga3.#f.#f4ag"
        seq += "#fed3d4d3a.d4/g#fe4d3a.d4DbC3D4EDCbag3D2G3 "
        '''
        
        #From https://musescore.com/user/10683961/scores/5679136
        #TODO: 20200412 DPM: Maybe some notes were incorrectly set
        
        seq = "O41   2 3 4ba(b#fd#fO3bO4 ba"
        seq += "b#fd#fO3bO4 b#CD#CDb#Cb#Cababgb bab#fd#fO3bO4 bab#fd#fO3bO4 b#C"
        seq += "D#CDb#Cb#Cabab#CD #FE#FDaD#f #FE#FDaD#f #F#G"
        seq += "A#GA#F#G#F#GE#FE#FD#F #FE#FDaD#f #FE"
        seq += "#FDaD#f #F#GA#GA#F#G#F#GE#FE#FD#F BA"
        seq += "B#F5D#F_4#Fb BAB#F5DE_4#Fb BO5#C"
        seq += "D5#CD D4b#C5b#C #C4ab5ab b4gb ba"
        seq += "O4B#F5D#F_4#Fb BAB#F5D#F_4#Fb O5b#C"
        seq += "4D5#CD D4b#C5b#C #C4ab5ab b4#CD #fe" #27
        seq += "O4#FD5aD_4D#f #FE#FD5aD_4D#f #F#G"
        seq += "O5a5#ga a4#f#g5#f#g #g4e#f5e#f #f4d#f #fe"
        seq += "O4#FD5aD_4D#f #FE#FD5aD_4D#f #f#g"
        seq += "a5#ga a4#f#g5#f#g #g4e#f5e#f #f4d#f BA" #35
        seq += "B#F5D#F_4#Fb BAB#F5D#F_4#Fb BO5#C"
        seq += "D5#CD D4b#C5b#C #C4ab5ab b4gb ba"
        seq += "O4B#F5D#F_4#Fb BAB#F5D#F_4#Fb BO5#C"
        seq += "D5#CD D4b#C5b#C #C4ab5ab b4#CD #fe"
        seq += "O4#FD5aD_4D#f #FE#FD5aD_5D#f #F#G"
        seq += "O5a5#ga a4#f#g5f#g #g4e#f5e#f #f4d#f #fe"
        seq += "O4#FD5aD_4D#f #FE#FD5aD_4D#f #F#G" #49
        seq += "A5#GA A4#F#G5#F#G #G4E#F5E#F #F4D#F BAB#FBAB#FBA"
        seq += "B#FBAB#FBA|B#FBAB ba)"
        seq += "(b#fd#fO3bO4 ba"
        seq += "b#fd#fO3bO4 b#CD#CDb#Cb#Cababgb bab#fd#fO3bO4 bab#fd#fO3bO4 b#C"
        seq += "D#CDb#Cb#Cabab#CD #FE#FDaD#f #FE#FDaD#f #F#G"
        seq += "A#GA#F#G#F#GE#FE#FD#F #FE#FDaD#f #FE"
        seq += "#FDaD#f #F#GA#GA#F#G#F#GE#FE#FD#F BA"
        seq += "B#F5D#F_4#Fb BAB#F5DE_4#Fb BO5#C"
        seq += "D5#CD D4b#C5b#C #C4ab5ab b4gb ba"
        seq += "O4B#F5D#F_4#Fb BAB#F5D#F_4#Fb O5b#C"
        seq += "4D5#CD D4b#C5b#C #C4ab5ab b4#CD #fe" #27
        seq += "O4#FD5aD_4D#f #FE#FD5aD_4D#f #F#G"
        seq += "O5a5#ga a4#f#g5#f#g #g4e#f5e#f #f4d#f #fe"
        seq += "O4#FD5aD_4D#f #FE#FD5aD_4D#f #f#g"
        seq += "a5#ga a4#f#g5#f#g #g4e#f5e#f #f4d#f BA" #35
        seq += "B#F5D#F_4#Fb BAB#F5D#F_4#Fb BO5#C"
        seq += "D5#CD D4b#C5b#C #C4ab5ab b4gb ba"
        seq += "O4B#F5D#F_4#Fb BAB#F5D#F_4#Fb BO5#C"
        seq += "D5#CD D4b#C5b#C #C4ab5ab b4#CD #fe"
        seq += "O4#FD5aD_4D#f #FE#FD5aD_5D#f #F#G"
        seq += "O5a5#ga a4#f#g5f#g #g4e#f5e#f #f4d#f #fe"
        seq += "O4#FD5aD_4D#f #FE#FD5aD_4D#f #F#G" #49
        seq += "A5#GA A4#F#G5#F#G #G4E#F5E#F #F4D#F BAB#FBAB#FBA"
        seq += "B#FBAB#FBA)"
        seq += "B#FBAB 3 1   "
        
        s = Sequencer(Buzzer(Pin.board.D12, 3, 1))
        try:            
            s.play(seq)
        finally:
            s.cleanup()
    
    
    #beep()
    playScore()
    