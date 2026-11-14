# Open Pool Vehicle Borrowing

## Assign the four lead roles

| Lead role | Team member | First responsibility |
| --- | --- | --- |
| Domain | To assign | Own the scope, terminology and approved BR1–BR6. Lead Slides 1–3. |
| Domain model | To assign | Model VehicleBorrowRequest, VehiclePool and driver eligibility. Lead Slides 4–6 and present the event on Slide 10. |
| Architecture | To assign | Wire the application service, in-memory repositories and event handler. Lead Slides 7–9 and present the walkthrough on Slide 13. |
| Testing | To assign | Own T1–T8 and the TDD evidence. Lead Slides 11–12 and present traceability on Slide 15. |

The domain lead presents the rejected design choice on Slide 14. All four review integration.

## T3 duplicate vehicle IDs

Run from this folder using Python 3. No external dependencies are required.

    py -B -m unittest -v

The test supplies a car, a truck, and the same car again. It expects ValueError.
The initial model is preserved in evidence/t3_before.py. The red and green logs
capture the same test before and after adding the duplicate-ID check.

This starter implements the duplicate-ID portion of BR3. The non-empty request
rule and the rest of the borrowing workflow are pending.
