# AutoTune AI — 5-Year Financial Model

Confidential · Bottom-up · All figures USD

---

## Revenue build

Assumptions (blended):
- Pro seat ARPA = $49/mo → $588/yr
- Workshop ARPA = $349/mo/tech → $4,188/yr per seat; avg 3 seats/shop = $12,564/yr per shop
- Enterprise ARPA = $124,800/yr
- OEM ARPA = $250,000/yr
- API rev = weighted average $0.02 per recommendation
- Bridge hardware ASP: Pro $499 (37% GM), Workshop $1,299 (48% GM)
- Churn: 4% Pro monthly (annualized ≈ 39%), 1.6% Workshop monthly, 0.4% Enterprise, 0% OEM Y1
- Net revenue retention (Workshop+): 118% by Y3

| Segment (paying customers) | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|---:|---:|---:|---:|---:|
| Pro seats            |   3,200 |   9,800 |  24,000 |  46,000 |  75,000 |
| Workshops            |     400 |   1,600 |   4,500 |   9,200 |  15,500 |
| Enterprise tenants   |       6 |      22 |      68 |     140 |     220 |
| OEM contracts        |       0 |       2 |       6 |      12 |      18 |
| Gov / regulator      |       0 |       0 |       2 |       5 |       9 |
| Bridge units sold    |   2,900 |   9,400 |  22,000 |  40,000 |  62,000 |
| Recommendations (M)  |    0.35 |     1.9 |     6.8 |    18.4 |    38.9 |

### Revenue $M

| Line | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|---:|---:|---:|---:|---:|
| Pro                | 1.9  | 5.8  | 14.1 | 27.0 | 44.1 |
| Workshop           | 5.0  | 20.1 | 56.5 | 115.6 | 194.7 |
| Enterprise         | 0.7  | 2.7  | 8.5  | 17.5  | 27.5 |
| OEM                | 0.0  | 0.5  | 1.5  | 3.0   | 4.5 |
| Gov                | 0.0  | 0.0  | 1.2  | 3.0   | 5.4 |
| API                | 0.0  | 0.0  | 0.1  | 0.4   | 0.8 |
| Bridge hardware    | 1.6  | 5.3  | 12.3 | 22.3  | 34.6 |
| **Total revenue**  | **9.2** | **34.4** | **94.2** | **188.8** | **311.6** |
| Software share     | 78%  | 84%  | 87%  | 88%   | 89% |

## Cost build

| Line | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|---:|---:|---:|---:|---:|
| LLM & inference (COGS) | 0.9 | 2.6 | 5.1 | 8.4 | 12.9 |
| Cloud infra (COGS)     | 0.5 | 1.6 | 3.9 | 7.2 | 11.1 |
| Bridge COGS            | 1.0 | 3.3 | 7.4 | 12.9 | 19.0 |
| Support (COGS)         | 0.4 | 1.4 | 3.6 | 7.1 | 11.6 |
| **COGS total**         | 2.8 | 8.9 | 20.0 | 35.6 | 54.6 |
| **Gross margin**       | 70% | 74% | 79% | 81% | 82% |
| R&D                    | 3.9 | 9.6 | 18.6 | 30.0 | 44.0 |
| S&M                    | 2.5 | 7.6 | 20.1 | 40.1 | 62.8 |
| G&A                    | 1.1 | 3.0 | 6.8  | 12.4 | 19.0 |
| **OpEx**               | 7.5 | 20.2 | 45.5 | 82.5 | 125.8 |
| **EBITDA**             | -1.1 | 5.3 | 28.7 | 70.7 | 131.2 |
| EBITDA margin          | -12% | 15% | 30% | 37% | 42% |

## Cash / funding

| Y1 | Y2 | Y3 | Y4 | Y5 |
|---:|---:|---:|---:|---:|
| Seed close (2026-Q4) | $12M | | | | |
| Series A (2027-Q3)   |      | $28M | | | |
| Series B (2029-Q1)   |      |      | $80M | | |
| Ending cash          | 8.5  | 22.1 | 65.4 | 110.6 | 205.8 |

## Sensitivity

- **Workshop CAC** at $2,400 (payback 4.5 mo, LTV/CAC 6.2×).
- **LLM cost** sensitivity: ±25% shifts Y5 GM by ±2 pts (mitigated by caching + small-model tier).
- **OEM slippage** by 12 mo cuts Y5 revenue by 7%, EBITDA by 3 pts.

## Unit economics (steady-state Workshop, Y3)

| Metric | Value |
|---|---|
| ARPA | $12,564 |
| Gross margin | 79% |
| Contribution margin | $9,925 |
| CAC | $2,400 |
| CAC payback | 3.6 months |
| Gross churn | 19% |
| Net churn (with expansion) | -4% (net expansion) |
| LTV (10-yr) | $63,000 |
| LTV / CAC | 26× |
