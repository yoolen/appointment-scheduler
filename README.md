# Appointment Scheduler System Design

This project implements an appointment scheduling system for healthcare providers,
designed to handle enterprise scale (10k+ hospitals) while exploring the trade-offs
between REST and GraphQL APIs.

I recognized significant shortcomings after the interview, so this is a post-mortem to
analyze what I *did* and what I *should have* done. The `Questions and Assumptions`
section is out of band and occurred over the course of the interview, but everything
else is presented in the order I discussed.

## System Design Interview Analysis

### Questions and Assumptions
- **Q:** Do we need to populate hospital, doctor and patient data? \
  **A:** Assume that the hospital, doctor, and patient data has already been prepared.
  - [ ] For this exercise, implement something that stubs out the data for us
- **Q:** What if a doctor is in multiple facilities? \
  **A:** Let's assume each doctor only works at a single hospital.
  - [ ] Consider per hospital scheduling in the future
- **Q:** \*referring to a wireframe\* What does the `+` icon do? \
  **A:** Clicking that would allow adding extra doctors since some patients don't need
   to see a specific doctor.
- **Q:** How many DAUs are we expecting? What's the scale of the hospitals in the
  system? \
  **A:** Let's say there are tens of thousands of hospitals, each with 10s of doctors
  and the same number of staff working in them. Let's say there are hundreds of
  thousands of patients. \
  **Q:** Following on that, I would presume that mostly we'd be fetching schedule
  availabilities all the time and writing fairly often, but the difference between the
  two would probably be only an order of magnitude? \
  **A:** Yes, you can assume 10:1 read:write.
- **Q:** Can we assume that the hospital hours and doctor's availability are given in
  the local timezone? \
  **A:** As opposed to the patient's timezone? \
  **Q:** The only scenario I think that would be an issue would be teledocs? I'm in NJ
  and used a California teledoc before. \
  **A:** For the purpose of this, let's assume these are physical visits, but maybe
  we'll allow different timezones in the future.
- **Q:** Is a doctor's availability the same on a weekly schedule? i.e. will their
  availability on Monday be the same every Monday? \
  **A:** No, each day will have its own schedule.
- **Q:** How long are the appointments and can they start at any time on the hour? \
  **A:** For the purposes of this exercise let's assume appointments are exactly one
  hour long and start on the hour.

### Functional Requirements
All these requirements apply to **Staff** and **Doctors**, patients only interact with
the system through staff and doctors.
- Users must be able to set a doctor's availability on a per day basis
- Users must be able to create, read, update, and delete appointments
- Users must be able to select a hospital and filter available doctors
- Users must be able to select multiple doctors and view their schedules
- Users must be able to select a date range to view availabilities

### Non-Functional Requirements
- **Security** - Since we are dealing with patient data, the system must be secure and
  handle authentication and only allow users to view only what they have permissions for
- **Consistent** - Strong consistency ensures concurrent booking operations maintain
  data integrity and prevent race conditions like double-booking the same time slot
- **Available** - Doctors and staff rely on this system to book their patients; we need
  99.9% uptime during business hours
- **Reliable** - System handles failures gracefully, validates all inputs, and maintains
  correct operation even under high load or component failures
- **Performant** - Since a lot of people are going to be using the system and multiple
  bookings may take place simulataneously, the system must be responsive (<200ms
  response time for schedule retrieval)
- **Scalable** - As more facilities, doctors, staff, and patients are added, the system
  should be able to scale horizontally to accomodate new growth
- **Maintainable** - As more features are added and system complexity increases, the
  code should stay readable, clear, and well tested

> [!TIP]\
> **Consistency** is about the **DATA** state and integrity! \
> **Reliability** is about correct **SYSTEM** behavior!

### Scale Requirements
- **Hospitals**: 10,000+ facilities
- **Users per hospital**: 10-100 doctors, 10-100 staff
- **Read/Write ratio**: ~10:1 (more calendar views than bookings)

### Models

#### 
- Hospital
  - id: int (auto-increment)
  - name: str
  - address: str
  - timezone: ZoneInfo/tzinfo
  - open: Time
  - close: Time

> [!NOTE]\
> In discussing timezones I suggested that we could store the the open/close times
> naively, along with the timezone; I compared this to how MongoDB stores all datetimes
> in UTC, requiring us to handle conversions later.
>
> **Q:** Why would you choose to store the times this way over just `UTC`? \
> **A:** Storing in `UTC` would require us to convert to localize the information to
> each user/client, either in the backend or once it got to the frontend.
> 
> While technically correct, the real value of storing naive times + timezone is
> preserving business intent and handling daylight saving time correctly.
>
> Open and close times are not absolute moments in time, they are recurring schedules.
> When a business says "9 AM to 5 PM Eastern year-round," storing just `UTC` times
> creates a fundamental problem: during DST transitions, the business would appear to
> open at different local times throughout the year (9 AM in winter, 10 AM in summer).
> With naive + timezone storage, the conversion logic automatically handles EST vs EDT
> at query time, ensuring the business always opens at 9 AM local time regardless of
> season. This approach also avoids needing separate database records for standard vs
> daylight time, or complex conditional logic to handle DST transitions in the
> application layer.
>
> The decomposed format makes it trivial to recompose local datetimes for any user's
> timezone while maintaining the original business rules. Otherwise would need to use
> frontend helpers to convert into a user localized string and then parse it.

- Doctor
  - id: int (auto-increment)
  - name: str
  - hospital_fk: int
  - availability: dict[Date, list[dict[str, Time]]]

> [!NOTE]\
> I discussed one potential implementation where you could keep an array for a given
> year in a dict and just store start and stop times for each index where each index
> represented a day. This approach would give very fast lookups and allow actions like
> slicing to get ranges of data, but the write performance would be not great. So I
> switched availablity just be a dict mapping a date to a start and end time. \
> **Q:** What would happen if a doctor had multiple shifts of availability in a day? \
> **A:** Instead of storing the dict
>
> I should have gone into more detail about the trade-offs of different storage options.
> Looking at this approach of storing a blob in the table, I'm definitely treating this
> more like a document store than a relational database; although PostgreSQL does
> support JSON/JSONB well now.
>
> If I wanted to avoid this approach and stay normalized I could have kept an
> availability table that would track the doctor, the date, and each time range as
> a `start_time` and `end_time`. This table could be used to join against an appointment
> collection or be used by an API to return the availabilities to be used by the
> frontend: \
> ex. response:
> ```json
>  {
>    "doctor_id": 101,
>    "date": "2024-08-26",
>    "available_slots": [
>      {
>        "time": "09:00",
>        "duration": 60,
>        "bookable": true
>      },
>      {
>        "time": "10:00",
>        "duration": 60,
>        "bookable": true
>      },
>      {
>        "time": "14:00",
>        "duration": 60,
>        "bookable": true
>      }
>    ]
>  }
> ```
>
> That other possibility of a prepopulated Appointment table with "available" slots
> (since we know they always start on the hour and will run exactly one hour) might look
> like this. \
> ex:
> ```sql
> -- Presume a table of appointments
> CREATE TABLE appointments (
>   id INT PRIMARY KEY AUTO_INCREMENT,
>   doctor_fk INT NOT NULL,
>   appointment_time DATETIME NOT NULL,
>   patient_fk INT NULL,
>   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
>   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
>   
>   FOREIGN KEY (doctor_fk) REFERENCES doctors(id),
>   FOREIGN KEY (patient_fk) REFERENCES patients(id),
>
>   -- Prevent double bookings
>   UNIQUE KEY unique_doctor_time (doctor_fk, appointment_time),
>   -- Optimize availability queries
>   INDEX idx_doctor_availability (doctor_fk, appointment_time, patient_fk)
> )
>
> -- Setting availability for 2024-08-19, 9AM-5PM
> INSERT INTO appointment VALUES
> (1, 101, '2024-08-19 09:00:00', NULL),
> (2, 101, '2024-08-19 10:00:00', NULL),
> (3, 101, '2024-08-19 11:00:00', NULL),
> ...
> (8, 101, '2024-08-19 16:00:00', NULL),
> ```
>
> - Pros
>   - Existence can be used to indicate availability
>   - Atomic booking operations (easily handle race conditions)
>   - Quick queries for availability
>   - Bulk operations can be handled easily
>   - Everything is handled in the appointment table
>   - Collection acts as a log of patients
> - Cons
>   - Lots of storage overhead, could be sparse, could be millions of entries
>     - 10000 hospitals * 10 doctors * 8 hours a day = 800000 entries per day
>     - In 1 year -> 800000 * 365 = 292M entries a year
>   - This wouldn't be maintainable/extensible, what if doctors wanted to change to
>     shorter appointments or change their start times?
>   - Extra checks when removing availability (what if slot was already booked?)
> - Other considerations
>   - Could perform regular cleanup on past appointments to keep the size of the
>   data down.
>   - This would allow caching and easily removing entries as they are booked.
>   - `appointment_time` stored as naive DATETIME (no timezone info in the field itself)
>   would need to join with doctor/hospital timezone to properly display for end user.



### CAP Theorem Decision: Consistency over Availability

**Why Consistency was chosen:**
- **Double-booking prevention**: Critical that two patients cannot book the same time slot
- **Safety-critical operations**: Medical appointments directly impact patient care
- **Financial/operational impact**: Double-bookings create chaos and potential liability
- **User trust**: Healthcare staff must have complete confidence in the system

**How to achieve Consistency at Scale:**
- **Database partitioning** by hospital/region (each facility's data is largely independent)
- **Read replicas** to handle the 10:1 read/write ratio efficiently
- **Strategic caching** for calendar views and availability lookups
- **Optimistic locking** for appointment conflict resolution
- **Strong consistency within each hospital partition**

**Where Eventual Consistency is acceptable:**
- Notifications and alerts
- Analytics and reporting
- Cross-hospital data synchronization (rare use case)
- Audit logs and historical data

### Things I Discussed v. Things I Should Have Discussed

### Questions and Guidance
Questions that were asked of me to help guide me towards a better solution

### REST vs GraphQL Comparison

This implementation provides both API approaches to demonstrate:

**REST Advantages:**
- Simpler implementation and debugging
- Better HTTP caching semantics
- Easier integration with existing healthcare systems
- More predictable performance patterns
- Industry standard for healthcare integrations

**GraphQL Advantages:**
- Single endpoint for complex calendar queries
- Efficient data fetching (appointments + doctor + patient info in one request)
- Better support for real-time subscriptions
- Flexible client queries for different calendar views
- Reduced over-fetching for mobile clients

## Architecture Decisions

### Data Partitioning Strategy
```
Hospital A Partition    Hospital B Partition    Hospital C Partition
├── Appointments       ├── Appointments        ├── Appointments
├── Doctors            ├── Doctors             ├── Doctors
├── Staff              ├── Staff               ├── Staff
└── Patients          └── Patients            └── Patients
```

### Consistency Guarantees
- **Strong consistency** within each hospital partition
- **Eventual consistency** for cross-partition reporting
- **ACID transactions** for appointment booking operations
- **Optimistic concurrency control** to handle simultaneous bookings

### Scalability Patterns
- Horizontal partitioning by hospital
- Read replicas for calendar views
- Redis caching for frequently accessed availability data
- Load balancing across partition replicas

## Technical Implementation

- **Backend**: Django + DRF + Graphene GraphQL
- **Database**: PostgreSQL with partitioning
- **Frontend**: Vue 3 + TypeScript with API switching capability
- **Caching**: Redis for session and availability data
- **Authentication**: JWT with role-based access control

## Key Learning Outcomes

1. **Domain-driven consistency requirements**: Understanding when business rules demand strong consistency
2. **Partitioning strategies**: How to scale while maintaining consistency where needed
3. **API paradigm trade-offs**: Concrete comparison between REST and GraphQL approaches
4. **Healthcare system constraints**: Reliability and trust requirements in medical software

## Future Considerations

- **Multi-region deployment** with cross-region eventual consistency
- **Event sourcing** for complete audit trails
- **FHIR integration** for healthcare interoperability
- **Real-time conflict resolution** UI patterns

### Things I Should Have Asked About
> `TODO`