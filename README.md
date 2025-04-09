# mendoza_diagnostic_center_system

## Release Notes
**v 0.0.1**
First Version
April 9, 2025

- Getting hang of django framework using Claude
- Was able to build the structure of the Patients and Transactions modules
- Was able to build the outline for Tests and Companies modules too
- Patients Module
  - can add new patient
  - can verify if patient is new or not
    - if patient is new, a new patient id is generated. if a patient is old, it will show the patient id
    - checking is based on unique last name, first name, middle name, gender, and birthdate combination
  - when viewing patient details, it will show all transactions related to that patient
    - user is redirected to transaction views when clicked
  - can delete patient
  - can update patient
- Transaction Module
  - can add a new transaction given that the patient is already created
  - can edit and update a transaction
  - has active transactions view
  - has all transactions view
  - can delete a transaction
