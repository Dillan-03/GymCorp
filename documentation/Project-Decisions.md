## Justification

As a group, we decided to choose Project 1, the ‘Sports centre management system’. Our reasons are as follows, we are all dedicated gym goers and have gained our own personal user experience, by utilising the gyms personal websites to book individual fitness classes. We feel this experience will be invaluable to us, as we go on to develop our own software booking system. We aim to create a versatile system, which will improve efficiency by allowing users to book from anywhere, at any given time providing them with a convenient booking experience. 

## Monolithic vs Microservices

We decided to pursue a monolithic approach rather than using several microservices. A monolithic backend is much simpler to develop and maintain which allows us to realistically develop a higher quality product within the timeframe. As the functionality is all contained within a single repository/codebase, it is easier to manage in a development environment especially when working in a team. Additionally, it is much easier to ensure there is data integrity and consistency which is especially important in a situation where we are managing customer data. The database can be hosted with the monolithic backend and this means there is efficient communication between them. Some drawbacks can occur if the application grows in size or complexity, but as this is unlikely to occur for such situation for the provided backlog, we decided it should not pose much of a threat.

## Python and Flask

It is known the python is one of the most popular languages and also one of the easiest to start with. Any developers can contribute with little knowledge and the team we are working in already has members like Dillan and Ashir who have used not only python before, but even Flask during their work on COMP2011.

Flask is a lightweight framework for Python which is also known for simplicity. It is highly customizable with a variety of modules to achieve functionality. It integrates will with pytest for our testing and it also has a modular design which can be added upon and customized as needed. It also has a large community online which can help with any questions or to share any knowledge.

## Bootstrap

Bootstrap allows us to build responsive web application which prioritize mobile-first design and provides pre-designed UI components which can be customized to fit the application's needs. Bootstrap is designed to be easy to use and is optimized for smaller screens such as phones and tablets, and can scale up to any screen size. It is a very popular library which keeps evolving and has a large community behind it.

## Pylint

To ensure we keep a consistent and codestyle that brings upon high quality work, the team will all implement PyLint using Google's styleguide. This allows us to enforce a strict coding style that will adhere to the industry's best standards. It is integrated into out Github Actions pipeline so is therefore required that it scores at least 9/10. Other than improving maintainability through codestyle, it also allows us to catch our errors much earlier and by having it integrated within our IDE, we receive continuous feedback as we code.
