# Deal Status Reference (dlflstat)

Based on the provided status mapping table, loan period statuses are defined as follows:

## Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 1 | Open | Active/ongoing loan |
| 2 | Close | Normally closed loan |
| 3 | Sold | Loan sold to another entity |
| 4 | Restructured | Loan terms modified |
| 5 | Prolonged | Loan term extended |
| 6 | Annulled | Loan cancelled |
| 7 | Deactivated | Loan deactivated |
| 8 | Financial institution liquidation | Lender liquidated |
| 9 | Contract cancellation with the bureau of credit histories | Contract cancelled with credit bureau |
| 10 | Replacement of the borrower, transfer of debt | Borrower changed, debt transferred |
| 11 | Purchased | Claim rights acquired from another company, transferred upon first transfer of contract |
| 12 | Deactivated (bankruptcy) | Deactivated due to bankruptcy |
| 13 | Closed without repayment | Closed but not repaid |

## Closed Loan Definition

For the purpose of calculating "closed loans ratio", loans are considered **closed** if:
- `deal_status > 1` (any status except "Open")
- OR `actual_end_date` is filled

This approach ensures comprehensive coverage of all completed loan statuses, not just normally closed ones.

## Implementation Note

The original solution used only `actual_end_date` to determine closed loans. However, the status mapping indicates that multiple statuses (2-13) represent different types of loan completion/closure, which should be included in the closed loan ratio calculation.
