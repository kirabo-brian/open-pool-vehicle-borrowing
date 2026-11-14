# Open Pool Vehicle Borrowing

## Assign the four lead roles

| Lead role | Team member | First responsibility |
| --- | --- | --- |
| Domain | Muyama Joyce | Own the scope, terminology and approved BR1–BR6. Lead Slides 1–3. |
| Domain model | Watts Ryan Eric | Model VehicleBorrowRequest, VehiclePool and driver eligibility. Lead Slides 4–6 and present the event on Slide 10. |
| Architecture | Ssentaaba Brian Kirabo | Wire the application service, in-memory repositories and event handler. Lead Slides 7–9 and present the walkthrough on Slide 13. |
| Testing | Kazibwe David | Own T1–T8 and the TDD evidence. Lead Slides 11–12 and present traceability on Slide 15. |

The domain lead presents the rejected design choice on Slide 14. All four review integration.

## Run the tests

Run from this folder using Python 3.10 or later. You need no external dependencies.

    py -B -m unittest -v

This runs all eight tests, T1–T8. The latest output is in `evidence/final_test_run.txt`.

Other commands:

    py -B -m interface.cli                       # small demo of the two use cases
    py -B evidence/check_layer_dependencies.py   # proves dependencies point inward

## Project layout

    domain/            value object, aggregates, domain service, event, errors
    application/       application service, event handler, DTOs, repository abstractions
    infrastructure/    in-memory repositories and driver directory, in-process event bus
    interface/         minimal entry point (composition root)
    evidence/          TDD and architecture evidence

## Domain model

Ryan built the domain model in plain Python. The modules hold every business
rule and do no I/O, so the application service can load, save and publish
around them.

| Module (in `domain/`) | Contents | Rules |
| --- | --- | --- |
| `borrowing_duration.py` | `BorrowingDuration` value object: 1 to 7 whole days | BR1 |
| `vehicle_borrow_request.py` | `VehicleBorrowRequest` aggregate and `RequestStatus` | BR2, BR3, guards BR4 and BR6 |
| `vehicle_pool.py` | `VehiclePool` aggregate: pool membership and active reservations | BR5, BR6 |
| `driver.py` | `Driver` and `DriverEligibilityService` | BR4 |
| `events.py` | `VehicleBorrowRequestSubmitted` event | BR2, BR5 |
| `vehicle_category.py` | `VehicleCategory` (CAR, TRUCK) | BR4 |
| `errors.py` | `DomainError` and one error per rejection reason | all |
| `identifiers.py` | `clean_id`: rejects blank IDs, trims and uppercases the rest | BR3 |

### Workflow

1. The application service (`SubmitVehicleBorrowRequestService`) looks up the pool and
   the driver (BR6), refuses a request ID that already exists (`RequestAlreadyExists`),
   builds the duration (BR1) and the draft request (BR3), and saves the draft.
2. It calls `request.submit(driver, pool)`. The request checks, in order:
   it is still DRAFT (BR2), the driver and pool match the request, the pool
   holds every vehicle (BR6), and the driver holds a qualification for each
   category (BR4). Any failure raises an error and leaves the request in DRAFT
   with no event.
3. On success the request moves to SUBMITTED and records one
   `VehicleBorrowRequestSubmitted` event. The service collects it with
   `request.pull_events()` and publishes it on the in-process bus.
4. The handler (`ReserveVehiclesOnRequestSubmitted`) calls
   `pool.reserve_all(request_id, vehicle_ids)`. The pool checks every vehicle before it
   reserves any (BR5). If a vehicle has another request's reservation, the pool raises
   `VehicleAlreadyReserved` and changes nothing.
5. The handler calls `request.confirm()` on success or
   `request.reject_reservation()` on failure. Both require SUBMITTED.

### Guards beyond BR1–BR6

- `submit` rejects a driver or pool that differs from the one on the request.
- Request fields are read-only properties. Status changes go through `submit`,
  `confirm` and `reject_reservation`.
- `reserve_all` rejects an empty or duplicate list. A retry by the same request
  succeeds instead of rejecting the request.
- IDs are trimmed and uppercased, so `" car-01 "` and `"CAR-01"` are the same vehicle.

### Driver records

Driver is reference data, not an aggregate root, so it has no repository. The service
reads it through a read-only `DriverDirectory` port (in-memory implementation in
`infrastructure/`). The group may revisit this choice.

### Known limits

- Reservations never end. Vehicle returns sit outside the scope.
- The request stores the duration, and availability ignores it. Availability depends on
  active reservations only.

## Business rules and tests

| Rule | Type | Responsible code | Test |
| --- | --- | --- | --- |
| BR1 | Value | `BorrowingDuration` | T1 |
| BR2 | Identity/state | `VehicleBorrowRequest.submit/confirm/reject_reservation` | T2 |
| BR3 | Invariant | `VehicleBorrowRequest` constructor | T3 |
| BR4 | Cross-concept | `DriverEligibilityService` | T4 |
| BR5 | Follow-up | `VehicleBorrowRequestSubmitted`, handler, `VehiclePool.reserve_all` | T5 (T7, T8 end to end) |
| BR6 | Lookup | service + repositories, `VehicleNotInPool`, `RequestAlreadyExists` | T6 |

## T3 duplicate vehicle IDs (TDD evidence)

The test supplies a car, a truck, and the same car again. It expects ValueError.
The initial model sits in `evidence/t3_before.py`. `evidence/t3_red.txt` and
`evidence/t3_green.txt` capture the same test before and after Ryan added the
duplicate-ID check.

The test now builds the request with all five constructor arguments (request ID,
driver ID, pool ID, vehicle IDs and duration). The assertion has not changed.

## AI use

Claude (Anthropic) helped draft the application layer, tests T1, T2 and T4–T8, the
slide deck and parts of this README. The group reviewed the output and can explain it.
