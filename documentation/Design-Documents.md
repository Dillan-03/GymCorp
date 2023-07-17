Design Documents

## Sprint 1 UML:

### State diagrams

```mermaid

stateDiagram
[*] --> LoggedIn
LoggedIn --> MembershipStatus
MembershipStatus --> [*]
LoggedIn --> CancelMembership : select "Cancel Membership"
CancelMembership --> ConfirmCancellation : select "Confirm"
ConfirmCancellation --> MembershipCancelled : select "Confirm"
MembershipCancelled --> [*]
```

```mermaid

stateDiagram
    [*] --> LoggedIn: Customer logs into the portal
    LoggedIn --> BookSession: "Book Session" option is selected
    BookSession --> AvailableSessions: Display all available sessions
    AvailableSessions --> ClassSelected: Customer selects the class to attend
    ClassSelected --> PaymentDetails: Display session details
    PaymentDetails --> PaymentProcessing: Prompt for payment information
    PaymentProcessing --> PaymentSuccess: Payment processing is successful
    PaymentProcessing --> PaymentFailed: Payment processing has failed
    PaymentFailed --> PaymentDetails: Display error message
    PaymentFailed --> PaymentRetry: Customer selects to retry payment
    PaymentRetry --> PaymentProcessing: Prompt for payment information
    PaymentSuccess --> BookingConfirmed: Booking is confirmed
    BookingConfirmed --> EmailSent: Confirmation email is sent to customer
    EmailSent --> [*]: End
    PaymentRetry --> PaymentFailed: Payment processing has failed (retry)
```

### Sequence diagrams

```mermaid

sequenceDiagram
Customer->>+OnlineBookingSystem: Log into portal
Customer->>+OnlineBookingSystem: Select "Membership" option
OnlineBookingSystem->>+Customer: Display "Adult" or "Child" option
Customer->>+OnlineBookingSystem: Select membership type and duration
OnlineBookingSystem->>+Customer: Display payment information form
Customer->>+OnlineBookingSystem: Fill in payment information and submit
OnlineBookingSystem->>+PaymentGateway: Process payment
PaymentGateway-->>-OnlineBookingSystem: Payment confirmed
OnlineBookingSystem->>+Customer: Email membership agreement
Customer-->>-OnlineBookingSystem: Confirm receipt of email
OnlineBookingSystem->>+Customer: Update online portal
```

```mermaid

sequenceDiagram
    participant Customer
    participant OnlineBookingSystem
    participant PaymentGateway
    participant Facility
    participant EmailService
    
    Customer->>+OnlineBookingSystem: Login to portal
    Customer->>+OnlineBookingSystem: Select "Book Session"
    OnlineBookingSystem->>+Facility: Get available sessions
    Facility-->>-OnlineBookingSystem: Returns available sessions
    OnlineBookingSystem->>+Customer: Display available sessions
    Customer->>+OnlineBookingSystem: Select class to attend
    OnlineBookingSystem->>+Facility: Get session details
    Facility-->>-OnlineBookingSystem: Returns session details
    OnlineBookingSystem->>+Customer: Display session details
    Customer->>+OnlineBookingSystem: Enter payment information
    OnlineBookingSystem->>+PaymentGateway: Process payment
    PaymentGateway-->>-OnlineBookingSystem: Returns payment status
    OnlineBookingSystem->>+Customer: Prompt to save payment info
    Customer->>+OnlineBookingSystem: Select "Save payment info"
    OnlineBookingSystem->>+Facility: Update session availability
    Facility-->>-OnlineBookingSystem: Returns updated session availability
    OnlineBookingSystem->>+Customer: Confirm booking
    OnlineBookingSystem->>+EmailService: Send confirmation email
    EmailService-->>-OnlineBookingSystem: Confirms email sent
    OnlineBookingSystem-->>-Customer: Booking confirmed
```

### Class diagram

```mermaid

classDiagram
class User {
    <<entity>>
    - username: string
    - password: string
    + login(): void
}

class SportsBookingSystem {
    <<system>>
    - availableSessions: Session[]
    - bookedSessions: Session[]
    + searchSessions(filter: Filter): Session[]
    + getAvailableSessions(): Session[]
    + addBookedSession(session: Session): void
}

class Session {
    <<entity>>
    - classType: string
    - date: Date
    - time: Time
    - location: string
    - available: boolean
    + getClassType(): string
    + getDate(): Date
    + getTime(): Time
    + getLocation(): string
    + isAvailable(): boolean
}

class Booking {
    <<entity>>
    - session: Session
    - customer: User
    - quantity: int
    - cost: double
    + getSession(): Session
    + getCustomer(): User
    + getQuantity(): int
    + getCost(): double
}

class Filter {
    <<entity>>
    - startDate: Date
    - endDate: Date
    + getStartDate(): Date
    + getEndDate(): Date
}

User "1..*" --> "1" SportsBookingSystem
SportsBookingSystem "1" --> "1..*" Session
SportsBookingSystem "1" --> "1..*" Booking
SportsBookingSystem "1" --> "1..*" Filter
Session "1" --> "1..*" Booking
Booking "1" --> "1" User
```

### ERD:

```mermaid

erDiagram

    CUSTOMER ||--|{ BOOKING : books
    EMPLOYEE ||--|{ CUSTOMER : supports
    EMPLOYEE ||--|{ BOOKING : checks
    BOOKING }|--|{ ACTIVTY : has
    SESSION ||--|{ BOOKING : has
    SESSION ||--|{ ACTIVTY : has
    ACTIVTY }|--|| FACILITY : is_in
    DISCOUNT ||--|| SESSION : has
```

Here are our fields for the ERD diagram:

<html>
<body>
<!--StartFragment-->

Table Name | Field Name | Data Type
-- | -- | --
Customer | id | int
  | first_name | string
  | last_name| string
  | email | string
  | phone_number | string
  | date_of_birth | string
  | gender | string
  | membership | bool
Employee | id | int 
  | |first_name | string|
  | last_name| string
  | email | string
  | phone_number | string
  | date_of_birth | string
  | password | string |
Booking | id | int
  | customer_id (FK) | int
  | employee_id (FK) | int
  | session_id (FK) | int
  | activity_id (FK) | int
  | number_of_people | int
Activity | id | int
  | name | string 
  | booking_type | string
  || price | float
  || duration | in
  || times | string |
  | facility_id (FK) | int |
Session | id | int |
  | date | string |
  ||start_time | int
  ||number_of_people | int 
  |activity_id (FK) | int |
Facility | id | int |
  | |name | string
  | capacity | int 
  | |activity_id (FK) | int 
Discount | id | int |
  || discount | int 

<!--EndFragment-->
</body>
</html>