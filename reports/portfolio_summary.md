# Drug Development Portfolio Optimization - Portfolio Summary

## Executive conclusion

The analysis compares four ways to allocate pharmaceutical R&D capital across a 114-project pipeline.

- **Therapeutic-area risk-neutral model:** 46 projects, $2,305.09M total expected value.
- **Variance-constrained example:** almost the same expected value with a modest reduction in standard deviation.
- **Company-wide budget:** 53 projects and $2,466.60M total expected value, but greater portfolio volatility.
- **95% VaR model:** demonstrates that a zero-loss requirement is so conservative that it produces an all-cash portfolio.

## Business interpretation

Budget silos reduce capital-allocation efficiency because unused funds in one therapeutic area cannot move to stronger opportunities elsewhere. Pooling the budget improves expected value and capital utilization, but it also enables riskier portfolios.

The most defensible strategy is therefore:
1. use a company-wide capital pool;
2. preserve the required pipeline mix;
3. add an explicit variance or VaR control;
4. choose a portfolio near the efficient-frontier knee rather than an extreme point.

## Portfolio skills demonstrated

- Mixed-integer optimization
- Pharmaceutical R&D portfolio selection
- Quadratic portfolio variance
- Efficient frontier construction
- Budget-allocation strategy
- 95% Value at Risk
- Gurobi modeling
- Business interpretation of optimization results
