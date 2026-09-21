import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


algoritmi = {
    "mistral": {
        "ontopfas": 1, "ontopfas_totale": 15,
        "exo": 5, "exo_totale": 15,
        "greenai": 6, "greenai_totale": 10,
        "agrifood": 5, "agrifood_totale": 20,
        "ontopfas-star": 1, "ontopfas-star_totale": 15
    },
    "llama": {
        "ontopfas": 1, "ontopfas_totale": 1,
        "exo": 0, "exo_totale": 10,
        "greenai": 0, "greenai_totale": 10,
        "agrifood": 1, "agrifood_totale": 10,
        "ontopfas-star": 0, "ontopfas-star_totale": 5
    },
    "gemma": {
        "ontopfas": 0, "ontopfas_totale": 6,
        "exo": 1, "exo_totale": 5,
        "greenai": 1, "greenai_totale": 6,
        "agrifood": 0, "agrifood_totale": 4,
        "ontopfas-star": 0, "ontopfas-star_totale": 6
    },
    "deepseek": {
        "ontopfas": 1, "ontopfas_totale": 7,
        "exo": 1, "exo_totale": 8,
        "greenai": 3, "greenai_totale": 6,
        "agrifood": 3, "agrifood_totale": 7,
        "ontopfas-star": 8, "ontopfas-star_totale": 15
    },
    "gemini": {
        "ontopfas": 9, "ontopfas_totale": 15,
        "exo": 3, "exo_totale": 11,
        "greenai": 7, "greenai_totale": 11,
        "agrifood": 7, "agrifood_totale": 7,
        "ontopfas-star": 18, "ontopfas-star_totale": 19
    }
}

metriche = ["ontopfas", "exo", "greenai", "agrifood", "ontopfas-star"]
colori = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]

nomi_algoritmi = list(algoritmi.keys())
x = np.arange(len(nomi_algoritmi))
larghezza = 0.15


fig, ax = plt.subplots(figsize=(12, 6))

for i, metrica in enumerate(metriche):
    valori = [algoritmi[a][metrica] for a in nomi_algoritmi]
    totali = [algoritmi[a][f"{metrica}_totale"] for a in nomi_algoritmi]

    pos = x + (i - 2) * larghezza

    ax.bar(
        pos,
        totali,
        width=larghezza,
        color=colori[i],
        edgecolor="black"
    )

    ax.bar(
        pos,
        valori,
        width=larghezza,
        color="none",
        edgecolor="black",
        hatch="////"
    )

ax.set_xticks(x)
ax.set_xticklabels(nomi_algoritmi)
ax.set_ylabel("# Axioms")
#ax.set_title("Confronto valori vs totali per algoritmo e metrica")

legend_elements = [
    Patch(facecolor=colori[i], edgecolor="black", label=metriche[i])
    for i in range(len(metriche))
]

ax.legend(handles=legend_elements)

plt.tight_layout()
plt.show()