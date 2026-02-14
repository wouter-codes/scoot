# Ideation and scoping

### Problem Statement

It's difficult getting anywhere in Cornwall without a car. Public transport is limited and taxis can be pricey. Many Cornish residents lack accessible transport to get to the shop, social or medical appointment.

### Purpose

Scoot connects local drivers with neighbours who need a lift. No more delayed buses or spenny taxi fares — just locals helping locals get where they need to go.

### Target Audience

Cornwall residents without reliable transport and community-minded drivers happy to offer a spare seat.

# Scoot - User Stories

> **MoSCoW Priority Key:**
> 🔴 Must Have (required to pass) | 🟡 Should Have (strengthens submission) | 🟢 Could Have (only if time allows)

---

## EPIC: User Authentication

| #   | User Story                                                                                                      | Priority | Acceptance Criteria                                                                                                      | LO    |
| --- | --------------------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------ | ----- |
| 1   | As a **site user**, I can **register for an account** so that **I can access ride features**.                   | 🔴       | User can register with username/email/password. Form validates input and shows errors. Redirects to homepage on success. | LO3.1 |
| 2   | As a **registered user**, I can **log in and log out** so that **I can securely access my account**.            | 🔴       | Login/logout works without errors. Session is created/destroyed correctly.                                               | LO3.1 |
| 3   | As a **site user**, I can **see my login status in the navbar** so that **I know whether I'm logged in**.       | 🔴       | Navbar shows username and logout link when logged in. Shows login/register links when logged out.                        | LO3.2 |
| 4   | As a **site user**, I cannot **access restricted pages when logged out** so that **the application is secure**. | 🔴       | Unauthenticated users are redirected to login page when trying to create/edit/delete rides.                              | LO3.3 |

---

## EPIC: Ride Management (CRUD)

| #   | User Story                                                                                                                                  | Priority | Acceptance Criteria                                                                                                                          | LO           |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 5   | As a **logged-in user**, I can **create a ride listing** so that **I can offer a lift to others**.                                          | 🔴       | Form with fields: origin, destination, date, time, available seats. Form validates all fields. Ride is saved to database and linked to user. | LO2.2, LO2.4 |
| 6   | As a **site user**, I can **view a list of available rides** so that **I can find a suitable lift**.                                        | 🔴       | All upcoming rides display in a list/card view. Each ride shows key details (origin, destination, date, driver).                             | LO2.2        |
| 7   | As a **site user**, I can **view the full details of a ride** so that **I can decide if it suits me**.                                      | 🔴       | Clicking a ride opens a detail page with all ride information.                                                                               | LO2.2        |
| 8   | As a **ride creator**, I can **edit my ride listing** so that **I can update details if plans change**.                                     | 🔴       | Edit form pre-populates with existing data. Only the ride creator can see/use the edit button. Changes save to database.                     | LO2.2, LO2.4 |
| 9   | As a **ride creator**, I can **delete my ride listing from the front end** so that **I can remove rides I no longer offer**.                | 🔴       | Delete button visible only to ride creator. Confirmation step before deletion. Record removed from database.                                 | LO2.2        |
| 10  | As a **user**, I can **see confirmation messages after creating, editing, or deleting a ride** so that **I know my action was successful**. | 🔴       | Django messages display success/error feedback for all CRUD actions. Messages auto-dismiss or can be closed.                                 | LO2.3        |

---

## EPIC: Ride Requests

| #   | User Story                                                                                                 | Priority | Acceptance Criteria                                                                                                                                            | LO           |
| --- | ---------------------------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 11  | As a **logged-in user**, I can **request to join a ride** so that **I can get a lift**.                    | 🟡       | Request button on ride detail page. A RideRequest record is created linking passenger to ride. Button disabled if user is the driver or has already requested. | LO2.2, LO7.1 |
| 12  | As a **ride creator**, I can **see pending requests on my rides** so that **I can manage my passengers**.  | 🟡       | Ride detail page shows list of requests with status. Only the driver can see this section.                                                                     | LO2.2        |
| 13  | As a **ride creator**, I can **approve or decline a ride request** so that **I can choose my passengers**. | 🟡       | Approve/decline buttons next to each request. Status updates in database. Confirmation message shown.                                                          | LO2.2, LO2.3 |

---

## EPIC: Front-End Design & UX

| #   | User Story                                                                                                  | Priority | Acceptance Criteria                                                                                               | LO    |
| --- | ----------------------------------------------------------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------- | ----- |
| 14  | As a **site user**, I can **view the site on any device** so that **I can use it on my phone or computer**. | 🔴       | Responsive layout using Bootstrap. No horizontal scrolling or broken layouts on mobile, tablet, or desktop.       | LO1.1 |
| 15  | As a **site user**, I can **easily navigate the site** so that **I can find what I need quickly**.          | 🔴       | Consistent navbar on all pages. Clear links to key sections. Active page highlighted.                             | LO1.1 |
| 16  | As a **site user**, I can **use the site with a screen reader** so that **the site is accessible**.         | 🟡       | Semantic HTML elements used. Alt text on images. No WCAG errors flagged by WAVE tool. Sufficient colour contrast. | LO1.1 |

---

## EPIC: Admin Functionality

| #   | User Story                                                                                                  | Priority | Acceptance Criteria                                                                  | LO    |
| --- | ----------------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------ | ----- |
| 17  | As an **admin**, I can **manage all ride listings via the admin panel** so that **I can moderate content**. | 🟡       | Rides visible and editable in Django admin. Admin can delete inappropriate listings. | LO3.1 |
| 18  | As an **admin**, I can **manage user accounts** so that **I can handle problematic users**.                 | 🟢       | Admin can view, edit, and deactivate user accounts from the admin panel.             | LO3.1 |

---

## EPIC: Project Setup & Deployment

| #   | User Story                                                                                                        | Priority | Acceptance Criteria                                                                                                  | LO           |
| --- | ----------------------------------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------- | ------------ |
| 19  | As a **developer**, I can **deploy the application to Heroku** so that **it is publicly accessible**.             | 🔴       | App runs on Heroku without errors. DEBUG=False. SECRET_KEY in env vars. Static files served correctly.               | LO6.1, LO6.3 |
| 20  | As a **developer**, I can **track project progress using a kanban board** so that **I follow Agile methodology**. | 🔴       | GitHub Projects board with To Do, In Progress, Done columns. All user stories as issues. Labels for MoSCoW priority. | LO1.3        |

---

## EPIC: Testing & Documentation

| #   | User Story                                                                                                            | Priority | Acceptance Criteria                                                                                                 | LO                |
| --- | --------------------------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------- | ----------------- |
| 21  | As a **developer**, I can **test all features manually** so that **I can verify the app works correctly**.            | 🔴       | Manual test cases documented in README with steps, expected results, actual results, and pass/fail.                 | LO4.1, LO4.3      |
| 22  | As a **developer**, I can **document the full UX and deployment process** so that **the README is assessment-ready**. | 🔴       | README includes: wireframes, design rationale, features, deployment steps, testing results, AI reflection sections. | LO1.5, LO6.2, LO8 |

---

## How to Use These in GitHub Projects

1. Create a new **GitHub Projects** board (Board view) on your repo
2. Set up columns: **Backlog → To Do → In Progress → Done**
3. Add each user story as an **Issue** in your repo
4. Use **Labels** for priority: `must-have`, `should-have`, `could-have`
5. Move cards across columns as you work — this provides the Agile evidence for LO1.3
6. Take screenshots of your board at different stages for the README

### Suggested Sprint Breakdown

**Sprint 1 (Days 1–5):** Stories 1–10, 14, 15, 19, 20 (all 🔴 Must Haves)
**Sprint 2 (Days 6–10):** Stories 11–13, 16–17, 21–22 (🟡 Should Haves + remaining 🔴s)

> **Tip:** Focus exclusively on 🔴 Must Haves first. Only move to 🟡 Should Haves once all Must Haves are complete and working on the deployed site.
