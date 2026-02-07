# Architecture 

The main components of this application include:
- IMAP index
- Prefect for data pipeline
- Flask for web application
  - DaisyUI design system

C4 components diagram:
```mermaid
C4Context
    title Town Digest - Context Diagram

    Person(user, "User", "A local resident who wants to stay informed about local events and news.")
    System(townDigest, "Town Digest", "A web application that collects and publishes local news and events.")

    user -> townDigest: Uses
```


# Concepts

The application will have multiple "Editions" each edition can cover multiple neighbooring towns as needed. 

Each edition will have a main email address where newsletters are sent. 

On a regular cadence email are processed as follows:
- Associate email to an edition 
- Process email to extract:
  - Events
  - General news and announcements
- Deduplicate and add news to the edition 
- Archieve email

The web frontend will display the events and news servered per edition. A subdomain indicataes the edition, an edition can have multiple subdomains.  


# Data model

The following models are used in the application:
- Edition
  - An edition represents a specific geographic area (e.g., a town or group of towns) and serves as the main organizational unit for the application. Each edition has a unique name and can have multiple associated subdomains, email aliases, events, and announcements.
- Subdomain
  - A subdomain is associated with an edition and serves as the URL for that edition's web frontend. An edition can have multiple subdomains, but each subdomain is associated with only one edition.
- EmailAlias
  - An email alias is an email address associated with an edition. Emails sent to this address are processed and associated with the edition.
- Email
  - An email received and processed by the system. Emails are associated with an edition through the email alias they were sent to.
- Event
  - An event is a structured piece of information extracted from an email, containing details such as date, time, location, and description. Events are associated with an edition.
- Announcement
  - An announcement is a general news item extracted from an email, containing unstructured information. Announcements are associated with an edition.
- Photo
  - A photo is an image associated with an event or announcement, providing visual context. Photos are associated with either an event or an announcement, but not both.
