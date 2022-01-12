# QR-Code-Reader

This project is a QR-code scanner to track people attending
[MelbPC](https://www.melbpc.org.au/) and [MelCC](https://melcc.org.au/) events.

It is intended to be used on the mobile device (phone or tablet) of someone authoirised by the club... it is not accessible by the public.

## How it works

### Backend

The backend regularly duplicates a minimal set of tables (read-only) from the CiviCRM database. These are referenced in a Django / REST API backend.

Members are accepted, or denied based on this duplicate data, and recorded.

Attendance is then pushed back upstream to a CiviCRM database, and purged from the local DB.

### Frontend

The [frontend](frontend/) is written in vue3, and all back-end access is done via the django REST API.

## Documentation

- [Development Setup](doc/setup-dev.md) (public)
- [Attendance Scanner - Howto](https://forum.melbpc.org.au/t/871) (internal to club)

## Contributions

At this time [2022-01-12] this project is very specific to our ([MelbPC](https://www.melbpc.org.au/)/[MelCC](https://melcc.org.au/)) use case.

However, questions, and contributions are welcome.