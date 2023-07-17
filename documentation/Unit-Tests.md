Testing Plan of the Product

* Workflows
* Automated
* Test driven approach


Login Page:

Scenario: Inputting login details

1) User doesn't exist -> output "account doesn't exist"
2) Username is wrong -> output "account doesn't exist"
3) Password is wrong -> output "incorrect login details" 
4) Successful login -> output "successful login"

Scenario: Sign Up

1) Validate fName,sName
2) Validate email
3) Validate age 
4) Validate password (security wise)

Scenario: Booking 

1) Selecting a fully booked out session -> greyed out
2) Input too many people, over the capacity -> output "Limit exceeded"
3) Successful Booking -> output "Booking successful"
4) Booking multiple activities 

Scenario: Membership purchase

1) Purchase membership -> successful membership 
2) Purchase membership whilst a member -> invalid membership
3) Purchase membership without any payment details -> invalid payment

Scenario: Payment Service

1) Purchase without any payment details -> invalid payment
2) Purchase with membership -> 15% discounted price
3) Purchase without membership -> normal price
4) Purchase 3rd booking in a week -> 15% discounted price

