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

Run from this folder using Python 3. You need no external dependencies.

    py -B -m unittest -v

## Domain model

Ryan built the domain model in plain Python. The modules hold every business
rule and do no I/O, so the application service can load, save and publish
around them.

| Module | Contents | Rules |
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

1. The application service loads the request, the pool and the driver.
2. It calls `request.submit(driver, pool)`. The request checks, in order:
   it is still DRAFT (BR2), the driver and pool match the request, the pool
   holds every vehicle (BR6), and the driver holds a qualification for each
   category (BR4). Any failure raises an error and leaves the request in DRAFT
   with no event.
3. On success the request moves to SUBMITTED and records one
   `VehicleBorrowRequestSubmitted` event. The service collects it with
   `request.pull_events()`.
4. The event handler calls `pool.reserve_all(request_id, vehicle_ids)`. The pool
   checks every vehicle before it reserves any (BR5). If a vehicle has another
   request's reservation, the pool raises `VehicleAlreadyReserved` and changes
   nothing.
5. The handler calls `request.confirm()` on success or
   `request.reject_reservation()` on failure. Both require SUBMITTED.

### Guards beyond BR1–BR6

- `submit` rejects a driver or pool that differs from the one on the request,
  so a caller cannot pass BR4 with another driver's record.
- Request fields are read-only properties. Status changes go through `submit`,
  `confirm` and `reject_reservation`.
- `reserve_all` rejects an empty or duplicate list. A retry by the same request
  succeeds instead of rejecting the request.
- The pool treats `" car-01 "` and `"CAR-01"` as the same vehicle.

### Known limits

- Reservations never end. Vehicle returns sit outside the scope.
- The request stores the duration, and availability ignores it. The proposal
  bases availability on active reservations only.

## T3 duplicate vehicle IDs

The test supplies a car, a truck, and the same car again. It expects ValueError.
The initial model sits in evidence/t3_before.py. The red and green logs capture
the same test before and after Ryan added the duplicate-ID check.

The test now builds the request with all five constructor arguments (request ID,
driver ID, pool ID, vehicle IDs and duration). The assertion has not changed.

## Pending

- Architecture: `SubmitVehicleBorrowRequest`, the in-memory repositories, the
  event handler and the command-line entry point.
- Testing: T1, T2 and T4–T8. David has a draft suite covering them.
- Group decision: where the driver record lives. The proposal names two
  repositories, one per aggregate, and the service needs the driver too.
