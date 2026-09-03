"""
step_dxf_generico - come step_dxf_definitivi ma per i lavori DIVERSI dal 21032:
  - frontali cassetto SX/CX/DX NON uniti (ogni pezzo un file)
  - programmi unici con la versione GENERICA (niente regole CNC)
  - NIENTE sezionatura
"""

import step_dxf_definitivi as s

s.MODO_GENERICO = True

if __name__ == "__main__":
    s.main()
