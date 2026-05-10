# Interview Transcript: Parking App (Airbnb for Parking Spots)

**Format:** Simulated interview between Claude (no skill) and User

---

**Claude:** That sounds like a really interesting idea. Lets start simple — can you walk me through the basic concept? What does the app actually do?

**User:** Yeah so basically, like, people who have driveways or parking spots they're not using can rent them out to other people who need parking. Like if you live downtown and you don't use your spot during the day, you can make some money off it.

**Claude:** Got it — two sides: spot owners who want to earn, and drivers who need parking. Who do you picture as the main users on the renter side? Is this more for daily commuters, people going to events, tourists?

**User:** Probably all of those? Like I was thinking mainly commuters who need somewhere regular to park near their office. But also yeah, like people going to a concert or a game who don't want to pay those crazy garage prices.

**Claude:** That makes sense — both recurring use and one-off events. For the spot owners, are you thinking mainly residential driveways, or also businesses or commercial lots with unused capacity?

**User:** Mostly residential I think, like homeowners and apartment people. But I mean if a business wanted to list their lot on weekends when they're closed, that would be cool too.

**Claude:** Okay, so the listing side is fairly open. Let's talk about how bookings would work. Are you thinking people reserve spots in advance, or more like show up and scan something?

**User:** Advance booking for sure. Like you'd search for spots near where you need to be, pick one, and book it. Hourly, daily, or monthly.

**Claude:** Clear mental model — three booking durations. What about payment? How does money flow through the app?

**User:** The app takes a cut, like Airbnb does. Renter pays through the app, owner gets paid out minus a service fee.

**Claude:** Makes sense. What about the physical side — how does a renter actually access the spot?

**User:** For most home driveways it's just show up. Some places might have gates. Owners can put instructions like a gate code. I don't want to deal with smart locks for now.

**Claude:** Reasonable constraint for an early version. What about disputes?

**User:** Some kind of support or reporting system. Simple form, someone reviews it. Not super complicated.

**Claude:** Are there any geographic constraints?

**User:** US only for now, start in a few big cities — New York, LA, Chicago.

**Claude:** Platform preference and timeline?

**User:** Mobile app, iOS and Android. Budget is limited so keep it simple. 3-month build maybe.

---

## Requirements Summary

### App Concept
A two-sided marketplace mobile app where private parking spot owners rent out unused spaces to drivers.

### Core Features (MVP)
- Location-based spot search
- Listing management (photos, pricing, availability, access instructions)
- Advance booking (hourly, daily, monthly)
- In-app payments with platform fee
- Simple dispute reporting

### Platform & Constraints
- Mobile: iOS and Android
- No hardware integrations
- US-only, starting in New York, LA, Chicago

### Timeline
- ~3 months, lean budget
