"""
Run this script once to generate a sample Excel template.
Usage: python generate_sample.py
"""
import pandas as pd

data = {
    "ISIN":             ["IN0020220128", "IN0020210079", "IN0020220201", "IN0020200045"],
    "SECURITY NAME":    ["MH SDL 2034",   "GJ SDL 2033",   "AP SDL 2030",   "PB SDL 2032"],
    "STATE":            ["Maharashtra",   "Gujarat",       "Andhra Pradesh","Punjab"],
    "MATURITY":         [2034, 2033, 2030, 2032],
    "YTM (%)":          [7.64, 7.58, 7.89, 7.95],
    "G-SEC YIELD (%)":  [7.10, 7.10, 7.10, 7.10],
    "LAST CUT-OFF (%)": [7.58, 7.55, 7.82, 7.88],
    "LIQUIDITY":        ["High", "High", "Low", "Low"],
    "FACE VALUE":       [100, 100, 100, 100],
}

df = pd.DataFrame(data)
df.to_excel("sample_bond_data.xlsx", index=False)
print("✅ sample_bond_data.xlsx created!")
print("\nRequired columns your Excel MUST have:")
print("  • YTM (%)")
print("  • G-SEC YIELD (%)")
print("  • LAST CUT-OFF (%)")
print("\nOptional columns:")
print("  • ISIN, SECURITY NAME, STATE, MATURITY, LIQUIDITY, FACE VALUE")
