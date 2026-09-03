#!/usr/bin/env python3
"""
DXF → MPRX Converter per WoodWOP 7.2 (Homag)
Converte file DXF in formato MPRX per macchine CNC Homag

Lavorazioni supportate:
- Foratura: verticale, orizzontale, inclinata
- Fresatura contorno
- Scalatura: dritta, inclinata
- Tasca: verticale, orizzontale, inclinata

Layer DXF riconosciuti:
- FORI_VERT      → Foratura verticale
- FORI_HORIZ     → Foratura orizzontale
- FORI_INCL      → Foratura inclinata
- CONTORNO       → Fresatura contorno
- SCALATURA      → Scalatura dritta
- SCALATURA_INCL → Scalatura inclinata
- TASCA_VERT     → Tasca verticale
- TASCA_HORIZ    → Tasca orizzontale
- TASCA_INCL     → Tasca inclinata
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import ezdxf
import math
import os
import json
import argparse
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Foro:
    x: float
    y: float
    z: float = 0.0
    diametro: float = 5.0
    profondita: float = 13.0
    tipo: str = "verticale"  # verticale, orizzontale, inclinata
    angolo: float = 0.0


@dataclass
class Contorno:
    punti: List[Tuple[float, float]]
    profondita: float = 0.0
    larghezza_utensile: float = 8.0


@dataclass
class Tasca:
    punti: List[Tuple[float, float]]
    profondita: float = 0.0
    angolo_parete: float = 0.0
    finitura: bool = True


@dataclass
class Scalatura:
    x1: float
    y1: float
    x2: float
    y2: float
    profondita: float = 0.0
    larghezza: float = 8.0
    inclinata: bool = False
    angolo: float = 0.0


class DXFToMPRXConverter:
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_default_config()
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config.update(json.load(f))

        self.fori: List[Foro] = []
        self.contorni: List[Contorno] = []
        self.tasche: List[Tasca] = []
        self.scalature: List[Scalatura] = []

    def _load_default_config(self) -> Dict:
        return {
            "pezzo": {
                "lunghezza": 800.0,
                "larghezza": 600.0,
                "spessore": 18.0,
                "materiale": "Pannello truciolare"
            },
            "utensili": {
                "foratura": {"diametro_default": 5.0, "numero": 201},
                "fresatura": {"diametro": 8.0, "numero": 101},
                "scalatura": {"diametro": 8.0, "numero": 102},
                "tasca": {"diametro": 12.0, "numero": 103}
            },
            "layer_mapping": {
                "FORI_VERT": {"tipo": "foratura", "orientamento": "verticale"},
                "FORI_HORIZ": {"tipo": "foratura", "orientamento": "orizzontale"},
                "FORI_INCL": {"tipo": "foratura", "orientamento": "inclinata"},
                "CONTORNO": {"tipo": "contorno"},
                "SCALATURA": {"tipo": "scalatura", "inclinata": False},
                "SCALATURA_INCL": {"tipo": "scalatura", "inclinata": True},
                "TASCA_VERT": {"tipo": "tasca", "orientamento": "verticale"},
                "TASCA_HORIZ": {"tipo": "tasca", "orientamento": "orizzontale"},
                "TASCA_INCL": {"tipo": "tasca", "orientamento": "inclinata"},
                "0": {"tipo": "contorno"}
            }
        }

    def parse_dxf(self, dxf_path: str) -> None:
        """Legge il DXF e classifica le entità per layer"""
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()

        for entity in msp:
            layer = entity.dxf.layer.upper()
            mapping = self.config["layer_mapping"].get(
                layer, self.config["layer_mapping"].get("0")
            )

            if mapping["tipo"] == "foratura":
                self._parse_foro(entity, mapping)
            elif mapping["tipo"] == "contorno":
                self._parse_contorno(entity)
            elif mapping["tipo"] == "scalatura":
                self._parse_scalatura(entity, mapping)
            elif mapping["tipo"] == "tasca":
                self._parse_tasca(entity, mapping)

    def _parse_foro(self, entity, mapping: Dict):
        orientamento = mapping.get("orientamento", "verticale")

        if entity.dxftype() == 'CIRCLE':
            center = entity.dxf.center
            diametro = entity.dxf.radius * 2
            self.fori.append(Foro(
                x=center[0], y=center[1], z=0.0,
                diametro=diametro,
                profondita=self.config["pezzo"]["spessore"],
                tipo=orientamento
            ))
        elif entity.dxftype() == 'POINT':
            location = entity.dxf.location
            self.fori.append(Foro(
                x=location[0], y=location[1], z=0.0,
                diametro=self.config["utensili"]["foratura"]["diametro_default"],
                profondita=self.config["pezzo"]["spessore"],
                tipo=orientamento
            ))

    def _parse_contorno(self, entity):
        punti = self._get_punti_entity(entity)
        if punti and len(punti) >= 3:
            self.contorni.append(Contorno(
                punti=punti,
                profondita=self.config["pezzo"]["spessore"],
                larghezza_utensile=self.config["utensili"]["fresatura"]["diametro"]
            ))

    def _parse_scalatura(self, entity, mapping: Dict):
        punti = self._get_punti_entity(entity)
        if punti and len(punti) >= 2:
            inclinata = mapping.get("inclinata", False)
            self.scalature.append(Scalatura(
                x1=punti[0][0], y1=punti[0][1],
                x2=punti[-1][0], y2=punti[-1][1],
                profondita=self.config["pezzo"]["spessore"] / 2,
                larghezza=self.config["utensili"]["scalatura"]["diametro"],
                inclinata=inclinata,
                angolo=45.0 if inclinata else 0.0
            ))

    def _parse_tasca(self, entity, mapping: Dict):
        punti = self._get_punti_entity(entity)
        if punti and len(punti) >= 3:
            orientamento = mapping.get("orientamento", "verticale")
            self.tasche.append(Tasca(
                punti=punti,
                profondita=self.config["pezzo"]["spessore"] / 2,
                angolo_parete=0.0,
                finitura=True
            ))

    def _get_punti_entity(self, entity) -> List[Tuple[float, float]]:
        punti = []

        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            punti = [(start[0], start[1]), (end[0], end[1])]

        elif entity.dxftype() == 'LWPOLYLINE':
            punti = [(p[0], p[1]) for p in entity.get_points()]
            if entity.closed and punti[0] != punti[-1]:
                punti.append(punti[0])

        elif entity.dxftype() == 'POLYLINE':
            for vertex in entity.vertices:
                punti.append((vertex.dxf.location[0], vertex.dxf.location[1]))
            if entity.is_closed and punti[0] != punti[-1]:
                punti.append(punti[0])

        elif entity.dxftype() == 'ARC':
            center = entity.dxf.center
            radius = entity.dxf.radius
            start_angle = math.radians(entity.dxf.start_angle)
            end_angle = math.radians(entity.dxf.end_angle)

            if entity.dxf.start_angle > entity.dxf.end_angle:
                end_angle += 2 * math.pi

            num_segments = max(20, int(radius * 2))
            for i in range(num_segments + 1):
                angle = start_angle + (end_angle - start_angle) * i / num_segments
                punti.append((
                    center[0] + radius * math.cos(angle),
                    center[1] + radius * math.sin(angle)
                ))

        elif entity.dxftype() == 'CIRCLE':
            center = entity.dxf.center
            radius = entity.dxf.radius
            num_segments = max(20, int(radius * 2))
            for i in range(num_segments + 1):
                angle = 2 * math.pi * i / num_segments
                punti.append((
                    center[0] + radius * math.cos(angle),
                    center[1] + radius * math.sin(angle)
                ))

        elif entity.dxftype() == 'SPLINE':
            punti = [(p[0], p[1]) for p in entity.flattening(0.1)]

        return punti

    def generate_mprx(self, output_path: str):
        """Genera il file MPRX in formato XML"""
        root = ET.Element("woodwop")
        root.set("version", "7.2")

        # Info programma
        info = ET.SubElement(root, "programInfo")
        ET.SubElement(info, "description").text = "Generato da DXF"
        ET.SubElement(info, "author").text = "DXF-MPRX Converter"

        # Variabili pezzo
        vars_elem = ET.SubElement(root, "variables")
        pezzo = self.config["pezzo"]

        var_l = ET.SubElement(vars_elem, "variable")
        ET.SubElement(var_l, "name").text = "L"
        ET.SubElement(var_l, "value").text = str(pezzo["lunghezza"])
        ET.SubElement(var_l, "description").text = "Lunghezza pezzo"

        var_b = ET.SubElement(vars_elem, "variable")
        ET.SubElement(var_b, "name").text = "B"
        ET.SubElement(var_b, "value").text = str(pezzo["larghezza"])
        ET.SubElement(var_b, "description").text = "Larghezza pezzo"

        var_h = ET.SubElement(vars_elem, "variable")
        ET.SubElement(var_h, "name").text = "H"
        ET.SubElement(var_h, "value").text = str(pezzo["spessore"])
        ET.SubElement(var_h, "description").text = "Spessore pezzo"

        # Geometria pezzo
        panel = ET.SubElement(root, "panel")
        ET.SubElement(panel, "length").text = "L"
        ET.SubElement(panel, "width").text = "B"
        ET.SubElement(panel, "thickness").text = "H"
        ET.SubElement(panel, "material").text = pezzo["materiale"]

        # Aggiungi tutte le lavorazioni
        for i, foro in enumerate(self.fori):
            self._add_foro_macro(root, foro, i)

        for i, contorno in enumerate(self.contorni):
            self._add_contorno_macro(root, contorno, i)

        for i, scalatura in enumerate(self.scalature):
            self._add_scalatura_macro(root, scalatura, i)

        for i, tasca in enumerate(self.tasche):
            self._add_tasca_macro(root, tasca, i)

        # Formattazione XML
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

        print(f"\n✅ File MPRX generato: {output_path}")
        print(f"   Fori: {len(self.fori)}")
        print(f"   Contorni: {len(self.contorni)}")
        print(f"   Scalature: {len(self.scalature)}")
        print(f"   Tasche: {len(self.tasche)}")

    def _add_foro_macro(self, root, foro: Foro, index: int):
        macro = ET.SubElement(root, "macro")
        macro.set("name", f"Foro_{index+1}")
        macro.set("type", "drilling")

        if foro.tipo == "verticale":
            macro.set("subtype", "vertical")
        elif foro.tipo == "orizzontale":
            macro.set("subtype", "horizontal")
        elif foro.tipo == "inclinata":
            macro.set("subtype", "inclined")

        ET.SubElement(macro, "toolNumber").text = str(
            self.config["utensili"]["foratura"]["numero"]
        )
        ET.SubElement(macro, "toolDiameter").text = str(foro.diametro)
        ET.SubElement(macro, "x").text = str(foro.x)
        ET.SubElement(macro, "y").text = str(foro.y)
        ET.SubElement(macro, "z").text = str(foro.z)
        ET.SubElement(macro, "depth").text = str(foro.profondita)

        if foro.tipo == "inclinata":
            ET.SubElement(macro, "angle").text = str(foro.angolo)

    def _add_contorno_macro(self, root, contorno: Contorno, index: int):
        macro = ET.SubElement(root, "macro")
        macro.set("name", f"Contorno_{index+1}")
        macro.set("type", "routing")
        macro.set("subtype", "contour")

        ET.SubElement(macro, "toolNumber").text = str(
            self.config["utensili"]["fresatura"]["numero"]
        )
        ET.SubElement(macro, "toolDiameter").text = str(contorno.larghezza_utensile)
        ET.SubElement(macro, "depth").text = str(contorno.profondita)

        contour = ET.SubElement(macro, "contour")
        for i, (x, y) in enumerate(contorno.punti):
            point = ET.SubElement(contour, "point")
            point.set("index", str(i))
            ET.SubElement(point, "x").text = str(round(x, 3))
            ET.SubElement(point, "y").text = str(round(y, 3))

    def _add_scalatura_macro(self, root, scalatura: Scalatura, index: int):
        macro = ET.SubElement(root, "macro")
        macro.set("name", f"Scalatura_{index+1}")
        macro.set("type", "grooving")

        if scalatura.inclinata:
            macro.set("subtype", "inclined")
        else:
            macro.set("subtype", "straight")

        ET.SubElement(macro, "toolNumber").text = str(
            self.config["utensili"]["scalatura"]["numero"]
        )
        ET.SubElement(macro, "toolDiameter").text = str(scalatura.larghezza)
        ET.SubElement(macro, "depth").text = str(scalatura.profondita)
        ET.SubElement(macro, "x1").text = str(scalatura.x1)
        ET.SubElement(macro, "y1").text = str(scalatura.y1)
        ET.SubElement(macro, "x2").text = str(scalatura.x2)
        ET.SubElement(macro, "y2").text = str(scalatura.y2)

        if scalatura.inclinata:
            ET.SubElement(macro, "angle").text = str(scalatura.angolo)

    def _add_tasca_macro(self, root, tasca: Tasca, index: int):
        macro = ET.SubElement(root, "macro")
        macro.set("name", f"Tasca_{index+1}")
        macro.set("type", "pocket")
        macro.set("subtype", "vertical")

        ET.SubElement(macro, "toolNumber").text = str(
            self.config["utensili"]["tasca"]["numero"]
        )
        ET.SubElement(macro, "depth").text = str(tasca.profondita)
        ET.SubElement(macro, "wallAngle").text = str(tasca.angolo_parete)
        ET.SubElement(macro, "finish").text = "true" if tasca.finitura else "false"

        contour = ET.SubElement(macro, "contour")
        for i, (x, y) in enumerate(tasca.punti):
            point = ET.SubElement(contour, "point")
            point.set("index", str(i))
            ET.SubElement(point, "x").text = str(round(x, 3))
            ET.SubElement(point, "y").text = str(round(y, 3))


def main():
    parser = argparse.ArgumentParser(
        description="Converte file DXF in formato MPRX per WoodWOP 7.2"
    )
    parser.add_argument("input", help="File DXF di input")
    parser.add_argument("output", help="File MPRX di output")
    parser.add_argument("--config", "-c", help="File JSON di configurazione")
    args = parser.parse_args()

    converter = DXFToMPRXConverter(config_file=args.config)
    converter.parse_dxf(args.input)
    converter.generate_mprx(args.output)


if __name__ == "__main__":
    main()
