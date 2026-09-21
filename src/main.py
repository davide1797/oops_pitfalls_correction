import requests
from pathlib import Path
import xml.etree.ElementTree as ET
from rdflib import Graph, URIRef

OOPS_ENDPOINT = "https://oops.linkeddata.es/rest"

def query_oops_with_content(ontology_rdf, pitfalls="", output_format="XML"):
    xml_payload = f"""
    <?xml version="1.0" encoding="UTF-8"?>
        <OOPSRequest>
            <OntologyURI></OntologyURI>
            <OntologyContent><![CDATA[
        {ontology_rdf}
            ]]></OntologyContent>
            <Pitfalls>{pitfalls}</Pitfalls>
            <OutputFormat>{output_format}</OutputFormat>
        </OOPSRequest>
        """

    headers = {
        "Content-Type": "application/xml",
        "Accept": "application/xml"
    }

    response = requests.post(
        OOPS_ENDPOINT,
        data=xml_payload.encode("utf-8"),
        headers=headers,
        timeout=180
    )

    response.raise_for_status()
    return response.text


OOPS_NS = {"oops": "http://www.oeg-upm.net/oops"}

def oops_to_prompt(oops_xml: str) -> str:
    root = ET.fromstring(oops_xml)

    lines = []
    lines.append("The ontology has the following OOPS pitfalls:\n")

    count = 0
    for pitfall in root.findall("oops:Pitfall", OOPS_NS):
        name = pitfall.findtext("oops:Name", default="", namespaces=OOPS_NS).strip()
        description = pitfall.findtext("oops:Description", default="", namespaces=OOPS_NS).strip()

        lines.append(f"{count+1} - {name}, {description[:-1]} on the following elements")
        count += 1

        affected_elements = pitfall.findall(
            "oops:Affects/oops:AffectedElement", OOPS_NS
        )

        for elem in affected_elements:
            lines.append(elem.text.strip())

        lines.append("")  # blank line between pitfalls

    return "\n".join(lines).strip()

def remove_ttl_comments(input_file: str, output_file: str):
    lines = Path(input_file).read_text(encoding="utf-8").splitlines()

    cleaned_lines = [
        line for line in lines if not line.strip().startswith("#")
    ]

    Path(output_file).write_text("\n".join(cleaned_lines), encoding="utf-8")
    print(f"Saved cleaned ontology to {output_file}")

def clean_ttl_content(input_file: str, output_file: str) -> str:
    ALLOWED_PREDICATES = {
        "rdf:type",
        "rdfs:label",
        "skos:definition",
        "owl:inverseOf",
        "rdfs:range",
        "rdfs:domain",
        "rdfs:subClassOf",
        "rdfs:subPropertyOf"
    }
    lines = Path(input_file).read_text(encoding="utf-8").splitlines()
    cleaned_lines = []

    print(f"Original TTL has {len(lines)} lines")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        if len(parts) < 3:
            continue 
        
        maybe_predicate = parts[0].strip()
        predicate = parts[1].strip()
        if maybe_predicate in ALLOWED_PREDICATES or predicate in ALLOWED_PREDICATES:
            cleaned_lines.append(line)
    
    Path(output_file).write_text("\n".join(cleaned_lines), encoding="utf-8")
    print(f"Saved cleaned TTL to {output_file} ({len(cleaned_lines)} triples kept)")

def clean_ttl(input_file:str, output_file:str):
    ALLOWED_PREDICATES = {
        "#label",
        "#definition",
        "#inverseOf",
        "#domain",
        "#range",
        "#subClassOf",
        "#subPropertyOf",
        "#type"
    }

    g = Graph()
    g.parse(input_file, format="turtle")

    # Nuovo grafo filtrato
    filtered = Graph()

    # Copia namespace/prefix
    for prefix, namespace in g.namespaces():
        filtered.bind(prefix, namespace)

    print(len(filtered))
    # Filtra triple
    for s, p, o in g:
        for allowed in ALLOWED_PREDICATES:
            if allowed in p:
                filtered.add((s, p, o))

    # Salva risultato
    filtered.serialize(destination=output_file, format="turtle")

def clean_ttl_content2(input_file: str, output_file: str) -> str:
    ALLOWED_PREDICATES = {
        "rdf:type",
        "rdfs:label",
        "skos:definition",
        "owl:inverseOf",
        "rdfs:range",
        "rdfs:domain",
        "rdfs:subClassOf",
        "rdfs:subPropertyOf"
    }

    lines = Path(input_file).read_text(encoding="utf-8").splitlines()

    cleaned_lines = []
    current_subject = None
    kept_predicates = []

    def flush_statement():
        """Write the current subject + kept predicates correctly."""
        nonlocal kept_predicates
        if not current_subject or not kept_predicates:
            kept_predicates = []
            return

        for i, (pred, obj) in enumerate(kept_predicates):
            sep = " ;" if i < len(kept_predicates) - 1 else " ."
            cleaned_lines.append(f"{current_subject} {pred} {obj}{sep}")

        kept_predicates = []

    for raw in lines:
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        # New subject line
        if line.endswith("."):
            line = line[:-1].strip()
            end_statement = True
        else:
            end_statement = False

        # Split subject / predicate / object
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue

        subject, predicate, obj = parts

        # New subject → flush previous
        if subject != current_subject:
            flush_statement()
            current_subject = subject

        # Keep only allowed predicates
        if predicate in ALLOWED_PREDICATES:
            kept_predicates.append((predicate, obj.rstrip(";")))

        if end_statement:
            flush_statement()
            current_subject = None

    # Flush remaining
    flush_statement()

    Path(output_file).write_text("\n".join(cleaned_lines), encoding="utf-8")
    print(f"Saved cleaned TTL to {output_file} ({len(cleaned_lines)} triples kept)")

def ask_gemini(prompt) -> str:
    from openai import OpenAI
    client = OpenAI(
        api_key="",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content

    print("\n=== RISPOSTA GEMINI ===\n")
    print(answer)

    return answer

def build_llm_prompt(ontology_rdf, oops_text) -> str:
    return f"""
        You are an ontology engineering expert.

        Below is an ontology and the results of an OOPS! pitfall analysis.

        === OOPS PITFALLS ===
        {oops_text}

        === ONTOLOGY (RDF) ===
        {ontology_rdf}

        Please analyze the ontology and provide concrete axioms to solve every pitfall
        """

def build_llm_prompt2(ontology_rdf) -> str:
    return f"""
        === ONTOLOGY (RDF) ===
        {ontology_rdf}

        You are an ontology engineering expert. Based on the ontology, identify potential ontological pitfalls and propose solutions, including concrete axioms where possible
        """

def build_llm_prompt3(ontology_rdf) -> str:
    return f"""
        === ONTOLOGY (RDF) ===
        {ontology_rdf}

       You are an expert ontologist and knowledge engineer specialized in knowledge representation.

       Your task is to generate high-quality ontology documentation by writing missing rdfs:comment annotations. You can rely exclusively on the information explicitly available in the ontology and its axioms, as well as your knowledge on the domain.

       The generated comments should be suitable for ontology users, developers, and researchers who need clear semantic descriptions of ontology entities.
       
       Identify all ontology entities that do not have an rdfs:comment annotation and write only those comments.
"""

def chunk_text(text, max_chars=4000, overlap=200):
    """
    Split text into chunks with optional overlap.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # keep small overlap for context
    return chunks

def ask_mistral(prompt: str) -> str:
    headers = {
        "Authorization": "",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    return(response.json()["choices"][0]["message"]["content"])

def ask_llama(prompt: str) -> str:
    headers = {
        "Authorization": "",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    return(response.json()["choices"][0]["message"]["content"])

def ask_gemma(prompt: str) -> str:
    headers = {
        "Authorization": "",
        "Content-Type": "application/json"
    }

    data = {
        "model": "google/gemma-3-4b-it",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    return(response.json()["choices"][0]["message"]["content"])

def ask_deepseek(prompt: str) -> str:
    headers = {
        "Authorization": "",
        "Content-Type": "application/json"
    }

    data = {
        "model": "tngtech/deepseek-r1t-chimera:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    print(response.json())
    if "choices" not in response.json():
        return "Error"
    return(response.json()["choices"][0]["message"]["content"])

def ask_nemotron(prompt: str) -> str:
    headers = {
        "Authorization": "",
        "Content-Type": "application/json"
    }

    data = {
        "model": "nvidia/nemotron-nano-12b-v2-vl:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    return(response.json()["choices"][0]["message"]["content"])

if __name__ == "__main__2":
    ontologies = ["ontopfas", "exo", "green_ai", "agri_food", "ontopfas_pitfalls"]
    ontologies = ["agri_food"]
    models = ["gemma"]

    for ontology in ontologies:
        print(f"Processing ontology: {ontology}")
        rdf_path = Path(f"ontologies/original/{ontology}.rdf")  
        ttl_path = Path(f"ontologies/reduced/{ontology}.ttl")  

        ontology_rdf = rdf_path.read_text(encoding="utf-8")
        ontology_ttl = ttl_path.read_text(encoding="utf-8")

        result = query_oops_with_content(
            ontology_rdf,
            pitfalls="",          
            output_format="XML"   
        )

        oops_text = oops_to_prompt(result)

        for model in models:
            export_path = Path(f"ontologies/reduced/{ontology}_{model}.txt")

            print(f"Sending prompt to LLM {model}...")
            oops_message = f"You are an ontology engineering expert. Based on the ontology and the OOPS pitfalls of this prompt, answer with concrete axioms if possible, and if they do not introduce new ontological problems. Answer only with the code of the pitfall and the axioms. {ontology_ttl}{oops_text}"
            pitfalls_message = f"You are an ontology engineering expert. Based on the ontology, find possible ontological pitfalls and how you solve them, with concrete axioms if possible. Answer only with small descriptions and the resolutive axioms. {ontology_ttl}"

            if model == "mistral":
                llm_oops_response = ask_mistral(oops_message)
                llm_pitfalls_response = ask_mistral(pitfalls_message)
            elif model == "llama":
                llm_oops_response = ask_llama(oops_message)
                llm_pitfalls_response = ask_llama(pitfalls_message)
            elif model == "gemma":
                llm_oops_response = ask_gemma(oops_message)
                llm_pitfalls_response = ask_gemma(pitfalls_message)
            elif model == "deepseek":
                llm_oops_response = ask_deepseek(oops_message)
                llm_pitfalls_response = ask_deepseek(pitfalls_message)

            with open(export_path, "w") as f:
                f.write(f"=== OOPS PITFALLS ANALYSIS ===\n{llm_oops_response}\n\n")
                f.write(f"=== PITFALLS DISCOVERY ===\n{llm_pitfalls_response}\n")

if __name__ == "__main__":
    #clean_ttl_content2("ontologies/original/ontopfas.ttl", "ontologies/reduced/ontopfas.ttl")
    #ontology = Path("ontologies/original/exo.rdf").read_text(encoding="utf-8")  
    #ontology = Path("ontologies/original/agri_food.rdf").read_text(encoding="utf-8")
    #ontology = Path("ontologies/original/green_ai.rdf").read_text(encoding="utf-8")
    #ontology = Path("ontologies/original/geo.rdf").read_text(encoding="utf-8")
    #ontology = Path("ontologies/original/ontopfas.rdf").read_text(encoding="utf-8")
    #ontology = Path("ontologies/original/ontopfas_star.rdf").read_text(encoding="utf-8")
    
    #oops_result = query_oops_with_content(ontology, output_format="XML")

    #clean_ttl("ontologies/ontopfas_star.ttl", "ontologies/reduced/ontopfas_star.ttl")
    #clean_ttl("ontologies/ontopfas.ttl", "ontologies/priorities/ontopfas_1.ttl")
    #clean_ttl("ontologies/pizza.ttl", "ontologies/priorities/pizza_3.ttl")
    #clean_ttl("ontologies/proton.ttl", "ontologies/priorities/proton_3.ttl")
    #clean_ttl("ontologies/schema.ttl", "ontologies/priorities/schema_3.ttl")
    #f = open("pitfalls.txt", "w")
    #f.write(oops_result)
    #f.close()
    #print(oops_result)

    reduced_ontology = Path("ontologies/priorities/schema_1.ttl").read_text(encoding="utf-8")
    #oops_result = Path("ontologies/pitfalls/pitfalls_agri_food_reduced.txt").read_text(encoding="utf-8")

    prompt = build_llm_prompt3(reduced_ontology)
    #print(prompt)   

    gemini = ask_gemini(prompt)
    f = open("gemini_schema_1.txt", "w")
    f.write(gemini)
    f.close()
    
