import os
import google.generativeai as genai
import json
import pathlib
import textwrap
import re
import time

def clean_json_response(raw_text: str) -> str:
    match = re.search(r'```json\s*([\s\S]*?)\s*```', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

PHYSICS_CHAPTERS = [
    "Electric Charges and Fields",
    "Electrostatic Potential and Capacitance",
    "Current Electricity",
    "Moving Charges and Magnetism",
    "Magnetism and Matter",
    "Electromagnetic Induction",
    "Alternating Current",
    "Electromagnetic Waves",
    "Ray Optics and Optical Instruments",
    "Wave Optics",
    "Dual Nature of Radiation and Matter",
    "Atoms",
    "Nuclei",
    "Semiconductor Electronics: Materials, Devices and Simple Circuits"
]

PHYSICS_TOPICS = [
    # ...same as in annotate_questions_with_topics_physics.py...
    ("1.1", "Introduction"), ("1.2", "Electric Charge"), ("1.3", "Conductors and Insulators"), ("1.4", "Basic Properties of Electric Charge"), ("1.5", "Coulomb’s Law"), ("1.6", "Forces between Multiple Charges"), ("1.7", "Electric Field"), ("1.8", "Electric Field Lines"), ("1.9", "Electric Flux"), ("1.10", "Electric Dipole"), ("1.11", "Dipole in a Uniform External Field"), ("1.12", "Continuous Charge Distribution"), ("1.13", "Gauss’s Law"), ("1.14", "Applications of Gauss’s Law"),
    ("2.1", "Introduction"), ("2.2", "Electrostatic Potential"), ("2.3", "Potential due to a Point Charge"), ("2.4", "Potential due to an Electric Dipole"), ("2.5", "Potential due to a System of Charges"), ("2.6", "Equipotential Surfaces"), ("2.7", "Potential Energy of a System of Charges"), ("2.8", "Potential Energy in an External Field"), ("2.9", "Electrostatics of Conductors"), ("2.10", "Dielectrics and Polarisation"), ("2.11", "Capacitors and Capacitance"), ("2.12", "The Parallel Plate Capacitor"), ("2.13", "Effect of Dielectric on Capacitance"), ("2.14", "Combination of Capacitors"), ("2.15", "Energy Stored in a Capacitor"),
    ("3.1", "Introduction"), ("3.2", "Electric Current"), ("3.3", "Electric Currents in Conductors"), ("3.4", "Ohm’s law"), ("3.5", "Drift of Electrons and the Origin of Resistivity"), ("3.6", "Limitations of Ohm’s Law"), ("3.7", "Resistivity of Various Materials"), ("3.8", "Temperature Dependence of Resistivity"), ("3.9", "Electrical Energy, Power"), ("3.10", "Cells, emf, Internal Resistance"), ("3.11", "Cells in Series and in Parallel"), ("3.12", "Kirchhoff’s Rules"), ("3.13", "Wheatstone Bridge"),
    ("4.1", "Introduction"), ("4.2", "Magnetic Force"), ("4.3", "Motion in a Magnetic Field"), ("4.4", "Magnetic Field due to a Current Element, Biot-Savart Law"), ("4.5", "Magnetic Field on the Axis of a Circular Current Loop"), ("4.6", "Ampere’s Circuital Law"), ("4.7", "The Solenoid"), ("4.8", "Force between Two Parallel Currents, the Ampere"), ("4.9", "Torque on Current Loop, Magnetic Dipole"), ("4.10", "The Moving Coil Galvanometer"),
    ("5.1", "Introduction"), ("5.2", "The Bar Magnet"), ("5.3", "Magnetism and Gauss’s Law"), ("5.4", "Magnetisation and Magnetic Intensity"), ("5.5", "Magnetic Properties of Materials"),
    ("6.1", "Introduction"), ("6.2", "The Experiments of Faraday and Henry"), ("6.3", "Magnetic Flux"), ("6.4", "Faraday’s Law of Induction"), ("6.5", "Lenz’s Law and Conservation of Energy"), ("6.6", "Motional Electromotive Force"), ("6.7", "Inductance"), ("6.8", "AC Generator"),
    ("7.1", "Introduction"), ("7.2", "AC Voltage Applied to a Resistor"), ("7.3", "Representation of AC Current and Voltage by Rotating Vectors — Phasors"), ("7.4", "AC Voltage Applied to an Inductor"), ("7.5", "AC Voltage Applied to a Capacitor"), ("7.6", "AC Voltage Applied to a Series LCR Circuit"), ("7.7", "Power in AC Circuit: The Power Factor"), ("7.8", "Transformers"),
    ("8.1", "Introduction"), ("8.2", "Displacement Current"), ("8.3", "Electromagnetic Waves"), ("8.4", "Electromagnetic Spectrum"),
    ("9.1", "Introduction"), ("9.2", "Reflection of Light by Spherical Mirrors"), ("9.3", "Refraction"), ("9.4", "Total Internal Reflection"), ("9.5", "Refraction at Spherical Surfaces and by Lenses"), ("9.6", "Refraction through a Prism"), ("9.7", "Optical Instruments"),
    ("10.1", "Introduction"), ("10.2", "Huygens Principle"), ("10.3", "Refraction and Reflection of Plane Waves using Huygens Principle"), ("10.4", "Coherent and Incoherent Addition of Waves"), ("10.5", "Interference of Light Waves and Young’s Experiment"), ("10.6", "Diffraction"), ("10.7", "Polarisation"),
    ("11.1", "Introduction"), ("11.2", "Electron Emission"), ("11.3", "Photoelectric Effect"), ("11.4", "Experimental Study of Photoelectric Effect"), ("11.5", "Photoelectric Effect and Wave Theory of Light"), ("11.6", "Einstein’s Photoelectric Equation: Energy Quantum of Radiation"), ("11.7", "Particle Nature of Light: The Photon"), ("11.8", "Wave Nature of Matter"),
    ("12.1", "Introduction"), ("12.2", "Alpha-particle Scattering and Rutherford’s Nuclear Model of Atom"), ("12.3", "Atomic Spectra"), ("12.4", "Bohr Model of the Hydrogen Atom"), ("12.5", "The Line Spectra of the Hydrogen Atom"), ("12.6", "DE Broglie’s Explanation of Bohr’s Second Postulate of Quantisation"),
    ("13.1", "Introduction"), ("13.2", "Atomic Masses and Composition of Nucleus"), ("13.3", "Size of the Nucleus"), ("13.4", "Mass-Energy and Nuclear Binding Energy"), ("13.5", "Nuclear Force"), ("13.6", "Radioactivity"), ("13.7", "Nuclear Energy"),
    ("14.1", "Introduction"), ("14.2", "Classification of Metals, Conductors and Semiconductors"), ("14.3", "Intrinsic Semiconductor"), ("14.4", "Extrinsic Semiconductor"), ("14.5", "p-n Junction"), ("14.6", "Semiconductor Diode"), ("14.7", "Application of Junction Diode as a Rectifier")
]

def generate_physics_annotation_prompt(chapters, topics, questions):
    chapter_lines = [f"{i+1}. {ch}" for i, ch in enumerate(chapters)]
    topic_lines = [f"{num} {name}" for num, name in topics]
    prompt = textwrap.dedent(f"""
    You are an expert in educational content classification.
    You will receive a JSON array of questions from a Class 12 Physics question paper.
    Your task is to annotate each question with:
    - The correct chapter number and chapter name (from the official list below)
    - The correct topic number and topic name (from the official topic breakdown below)
    - Each question must be mapped to one and only one topic and chapter.
    - Insert the fields "chapter": "<number>", "chapter_name": "<name>", "topic": "<number>", "topic_name": "<name>" immediately after the "type" field in each question object.
    - Only use the chapter and topic numbers/names from the lists below.
    - Output the result as a JSON array, with the new fields added to each question.

    Chapters:
    {chr(10).join(chapter_lines)}

    Topics:
    {chr(10).join(topic_lines)}

    Here is the input JSON array of questions:
    ```json
    {json.dumps(questions, ensure_ascii=False, indent=2)}
    ```

    Output only the annotated JSON array.
    """)
    return prompt

def main():
    print("Batch Physics Question Annotator (Gemini)")
    print("="*40)
    data_folder = pathlib.Path("physics_data")
    out_folder = pathlib.Path("physics_data_annotated")
    out_folder.mkdir(exist_ok=True)
    files = list(data_folder.glob("*.json"))
    if not files:
        print(f"No JSON files found in physics_data/!")
        return
    chapters = PHYSICS_CHAPTERS
    topics = PHYSICS_TOPICS
    model = genai.GenerativeModel(model_name="models/gemini-2.5-pro")
    for fpath in files:
        out_path = out_folder / fpath.name
        if out_path.exists():
            print(f"⏭️  Skipping {fpath.name} (already annotated)")
            continue
            
        print(f"\nProcessing: {fpath.name}")
        with open(fpath, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        prompt = generate_physics_annotation_prompt(chapters, topics, questions)
        print("Sending questions to Gemini for annotation...")
        response = model.generate_content(prompt)
        print("Gemini response received. Parsing...")
        try:
            cleaned_json_string = clean_json_response(response.text)
            annotated = json.loads(cleaned_json_string)
        except Exception as e:
            print(f"\n--- ERROR: Failed to parse Gemini's response for {fpath.name}. ---")
            print(f"Error details: {e}")
            print("\n--- Raw Model Response: ---")
            print(response.text)
            print("\n--------------------------")
            continue
        # Reorder fields: insert chapter, chapter_name, topic, topic_name after type
        for i, q in enumerate(annotated):
            if "type" in q and "chapter" in q and "chapter_name" in q and "topic" in q and "topic_name" in q:
                new_q = {}
                for k, v in q.items():
                    new_q[k] = v
                    if k == "type":
                        new_q["chapter"] = q["chapter"]
                        new_q["chapter_name"] = q["chapter_name"]
                        new_q["topic"] = q["topic"]
                        new_q["topic_name"] = q["topic_name"]
                annotated[i] = new_q
        out_path = out_folder / fpath.name
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(annotated, f, indent=4, ensure_ascii=False)
        print(f"✓ Annotated data saved to: {out_path}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        raise ValueError("Gemini API key not found. Please set the GOOGLE_API_KEY environment variable.")
    genai.configure(api_key=GOOGLE_API_KEY)
    main()
