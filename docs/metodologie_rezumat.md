# Rezumat metodologic (Cadru v5 + Matrice v4)

## Statusuri Data Readiness

| Status | Hard fail? | Note |
|--------|------------|------|
| AVAILABLE - CHECKED | Nu | Folosire integrală |
| AVAILABLE - NOT CHECKED | Nu | Sourcing incomplet; nu e zero |
| DERIVED | Nu | Necesită valoare + N + sursă + metodă + cutoff |
| PROXY ONLY | Doar dacă G0 cere nativ | Haircut / confidence cap |
| PENDING OFFICIAL | Nu (de regulă) | Afișează refresh plan |
| SOURCE CONFLICT | Da dacă afectează G0 | Reconciliere obligatorie |
| NOT AVAILABLE | Da doar pe G0 critic | Nu inventa date |
| SMALL SAMPLE | Nu | Prior/shrinkage; fără downgrade mecanic |

## G0–G3

- **G0:** hard gate — input obligatoriu (zero-mass Over 0.5; 1X2 de-vig Șansă Dublă; 12 native cornere)
- **G1:** context soft
- **G2:** calibrare / incertitudine
- **G3:** piață (unde modelul cere)

## Sentinel FootyStats

`-1`, `-2`, `null` → `NOT AVAILABLE` (sau neterminal), **niciodată** 0.
