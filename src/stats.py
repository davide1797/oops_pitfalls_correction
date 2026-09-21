from scipy.stats import chi2_contingency
import pandas as pd

# Matrice di contingenza
data = {
    'Successi': [129, 49, 36, 135, 109],
    'Fallimenti': [20, 100, 113, 14, 40]
}
contingency_table = pd.DataFrame(data, 
    index=['Mistral', 'Llama', 'Gemma', 'DeepSeek', 'Gemini'])

# Chi-quadro
chi2, p_value, dof, expected = chi2_contingency(contingency_table)
print(f"p-value: {p_value}")