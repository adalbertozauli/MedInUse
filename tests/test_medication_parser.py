import unittest

from services.medication_parser import extract_medications, format_medications, infer_schedule


class MedicationParserTest(unittest.TestCase):
    def test_examples_from_spec(self) -> None:
        lines = [
            "Losartana 50mg",
            "Tomar 01 comprimido, de 12/12 horas.",
            "Anlodipino 5mg",
            "Tomar 01 comprimido cedo",
            "Amoxicilina 500mg",
            "Tomar 01 comprimido de 8/8 horas",
            "Cefalexina 500mg",
            "Tomar 01 comprimido de 6/6 horas",
        ]

        result = format_medications(extract_medications(lines), one_per_line=True)

        self.assertEqual(
            result,
            "\n".join(
                [
                    "- Losartana 50mg (1-0-1)",
                    "- Anlodipino 5mg (1-0-0)",
                    "- Amoxicilina 500mg (1-1-1)",
                    "- Cefalexina 500mg (1-1-1-1)",
                ]
            ),
        )

    def test_future_posology_variations(self) -> None:
        cases = {
            "Tomar 01 comprimido a cada 12 horas": "1-0-1",
            "Tomar 01 comprimido cada 8 horas": "1-1-1",
            "Tomar 01 comprimido a cada 6 horas": "1-1-1-1",
            "Tomar 01 comprimido ao dia": "1x/dia",
            "Tomar 01 comprimido uma vez ao dia": "1x/dia",
            "Tomar 01 comprimido 1x/dia": "1x/dia",
            "Tomar 01 comprimido 2 vezes ao dia": "1-0-1",
            "Tomar 01 comprimido duas vezes por dia": "1-0-1",
            "Tomar 01 comprimido 3 vezes ao dia": "1-1-1",
            "Tomar 01 comprimido quatro vezes ao dia": "1-1-1-1",
            "Tomar 01 comprimido por semana, 3 meses": "1 comp. semana/12 semanas",
            "Tomar 05 gotas de 12/12 horas": "5 gts-0-5gts",
            "Tomar 05 gotas de 8/8 horas": "5 gts-5gts-5gts",
            "Tomar 10 ml a cada 8 horas": "10ml-10ml-10ml",
            "Tomar 2,5 ml ao dia": "2,5 ml 1x/dia",
            "Tomar 03 gotas cedo": "3 gts-0-0",
            "Tomar 5,0ml de 12/12 horas": "5ml-0-5ml",
            "Tomar 10 unidades à noite": "0-0-10U",
            "Tomar 01 comprimido às 8:00": "1-0-0",
            "Tomar 01 comprimido às 13 horas": "0-1-0",
            "Tomar 01 comprimido às 17h": "0-1-0",
            "Tomar 01 comprimido às 18h": "0-0-1",
            "Tomar 01 comprimido às 8h e às 20h": "1-0-1",
            "Tomar 5ml às 14h": "0-5ml-0",
            "Tomar 10 unidades às 22:00": "0-0-10U",
            "Tomar 01 comprimido no café da manhã, almoço e jantar": "1-1-1",
            "Tomar 01 comprimido 20 minutos antes das refeições": "1-1-1",
            "Tomar 01 comprimido em jejum": "1-0-0",
            "Tomar 01 comprimido ao deitar": "0-0-1",
            "Aspirar 2 puffs pela manhã": "2puffs-0-0",
            "Aplicar 02 jatos em cada narina, 2x/dia": "2puffs-0-2puffs",
            "Aplicar 01 ampola IM a cada 30 dias": "1 ampola/30 dias",
            "Aplicar 01 amp. IM profunda em região glútea 90/90 dias": "1 ampola/90 dias",
            "Tomar 01 comprimido, dose única": "1 comp. dose única",
            "Tomar ½ comprimido, dose única": "0,5 comp. dose única",
            "Tomar 5 ml por semana, 2 meses": "5 ml semana/8 semanas",
            "Tomar 7 gotas por semana, 4 semanas": "7 gotas semana/4 semanas",
        }

        for posology, expected in cases.items():
            with self.subTest(posology=posology):
                self.assertEqual(infer_schedule(posology), expected)

    def test_medication_names_with_ml_are_not_treated_as_posology(self) -> None:
        lines = [
            "Haldol 2mg/ml",
            "Tomar 25 gotas, de 12/12 horas.",
            "Neosine 40mg/ml",
            "Tomar 25 gotas, de 12/12 horas.",
            "Depakene 250mg/5ml",
            "Tomar 10ml de 12/12 horas.",
        ]

        result = format_medications(extract_medications(lines), one_per_line=True)

        self.assertEqual(
            result,
            "\n".join(
                [
                    "- Haldol 2mg/ml (25 gts-0-25gts)",
                    "- Neosine 40mg/ml (25 gts-0-25gts)",
                    "- Depakene 250mg/5ml (10ml-0-10ml)",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
