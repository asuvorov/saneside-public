Change Log
==========
v.X.Y.Z (YYYY-MM-DD)
--------------------
### New

>

### Fixes

>

### Changes

>

v.2.0.3 (2018-03-09)
--------------------
### New

> Accounts: Users can archive received/sent Invitations.

> Challenges: Added Categories List Page.

### Fixes

> Accounts: Views: Moved some Logic from Views to Mixins.

### Changes

> Accounts: Foreign Profile: Details Page: Re-design.

> Accounts: My Profile: Details, edit, delete Pages: Re-design.

> Challenges: Details, create, edit Pages: Re-design.

> Organizations: Details, create, edit Pages: Re-design.

v.2.0.2 (2018-01-17)
--------------------
### New

> Accounts, Blog, Challenges, Forum, Organizations: actively show uploading Status on creating/editing Instances.

> Accounts: Foreign Profile: Invite to Organization Group, or Staff.

> Accounts: My Profile Page: Allow Participant to submit their Experience Report and rate the Challenge from the Table of the completed Challenges.

> Accounts: Simplifying the Challenge Organizer's Actions on the Challenges, which require the Action.

> Challenges: Details: Added Notification, if there are Participants, waiting for Confirmation and/or Acknowledgment.

> Challenges: Organizer can add reporting Materials after Challenge is completed.

> Challenges: Organizer can mark the Challenge as complete, even if it hasn't taken Place.

> Challenges: Organizer can clone (reschedule) the Challenge, if it hasn't taken Place.

> FAQ: Added `Section` Model.

> FAQ: Added edit/delete Functionality.

> Organizations: Change the Order of the Staff Members, edit Staff Members, remove Staff Members.

> Organizations: Details: Added "Create Challenge" Functionality.

> Organizations: Details: Groups Tab: Added "Add Group" Button and Functionality.

> Organizations: Details: Groups Tab: Added "Remove Group" Button and Functionality.

> Organizations: Details: Groups Tab: Added "Remove Group Member" Button and Functionality.

> Search: Results: Render HTML Version.

### Fixes

> Accounts: My Profile: List of the created and related Organizations.

> Challenges: Create: List of the Organizations in the Dropdown.

> Organizations: Details: List of the User's related Organizations.

### Changes

> Accounts: Changed the User Flow on signing up.

> Accounts, Comments, Complaints, Organizations, Ratings: Reworked AJAX Calls with REST API.

> Implemented `django-ckeditor` instead of `django-wysiwyg`.

v.2.0.1 (2017-07-07)
--------------------
### New

> Accounts, Challenges, Organizations: Added Complaints Functionality...

> Forum: Added custom Template Tag for rendering MPTT Instances.

> Forum: Added 'readmore.js'.

### Fixes

> Accounts, Blog, Challenges, Forum, Organizations: Fixed Metadata on Instance create/update.

> Accounts, Blog, Challenges, Organizations: Fixed the Path for uploading the Avatar Images of the newly created Instances.

> Accounts: Properly show the Member's Name with Privacy.

> Buttons' Colors.

### Changes

> Accounts: Moved querying User's Participations from View to Mixin.

> Forum: Topic Posts styling.

> Moved inline Javascript for uploading Files to an Inject.

> Removed overwhelming Headers.

> Reworked NavBar.

> Unified and extended Styles with LessCSS.

> Upgraded Django to Version 1.11.x.

v.2.0.0 (2017-07-03)
--------------------
### New

> Accounts: Customized the Path, where all the uploaded Media Files go.

> Accounts: My Profile. Add/view social Links.

> Accounts: Foreign Profile: View social Links.

> Admin: Added Django-Grappelli Interface.

> Admin: Show Images Thumbnails in the Django Admin.

> SEO: Added ALT Text on Images, where it makes Sense.

> SEO: Added URL Path Metadata Fixtures.

> SEO: Accounts, Challenges, Organizations: Populate Model Instance Metadata on Save.

> SEO: Created relevant Title Tag(s).

> Added Javascript for handling Browser/Browser Tab Events, like closing, reloading, refreshing...

### Fixes

> Organization Twitter Feed (if applied).

### Changes

> Accounts, Challenges, Organizations: Changed Navigation Arrows' Layout on the sign-up/create/edit Pages.

> Updated the Logo.

> Side Bar: Contact Person Phone Numbers.

v.1.12.14 (2017-06-04)
--------------------
### New

> Accounts: Privacy Settings: Updated to the latest.

> Challenges: Roles: Show the List of the Roles on the Challenge Preview.

### Fixes

> Challenges: Roles & Social Links Formsets: Failed to create/delete Formset Entry.

> Challenges, Organizations: Addressless Checkbox always checked (True).

> Invites: If related Content Object (Challenge, Organization, etc.) does not exist (deleted from the Database), rendering such Invite(s) breaks the entire Template.

> NavBar: Avatar.

> Organizations: Social Links Formset: Failed to delete Formset Entry.

### Changes

> Accounts: Simplified sign up Process.

> Accounts: Prompting User to provided an Email Address, if not set yet.

> Challenges: Roles Breakdown: Style.

> Updated 'humans.txt' File.

> Updated 'robots.txt' File.

v.0.1.6 (2015-03-28)
--------------------
### New

> Added `Order` Field to `Team` & `TeamMember` Models.

> Added `Team` Model.

> Added Time Picker.

> Added Google Analytics Handler.

> Added `"Sign in"` Modal.

> Added List of related Organization on `"Member Profile"` Page.

> Added 'Automatically accept Participants after Challenge completed' Functionality.

> Added 'Allow re-entering to Challenge after withdrawing Application' Functionality.

### Fixes

> Fixed Design Responsiveness.

> Fixed Footer positioning.

> User Profile Flow Fixes.

> Design Fixes.

> Reviewed and updated User Agreement and Privacy Policy.

### Changes

> Improved `"Our Team"` Page.

> Updated `"About us"` Page.

v.0.1.5 (2015-02-15)
--------------------
### New

> Added "Affiliated with..." Challenges Tab.

> Added basic filtering of `Challenge List` by Category.

> Added Challenge Categories.

> Added `Team Members` Model and Functionality.

> Added GeoLocation Functionality.

> Added ForeignKey `Role` to Model `Participation`.

> Added "Roles" Functionality to `"Post Challange"`, and `"Edit Challenge"` Pages.

> Made `Challenge[Avatar]` Field mandatory.

> Added "Share on..." Functionality to `"Organization Details"` Page.

> Added "Delete Comment" Functionality to `"Organization Details"` Page.

> Added "Add Comment" Functionality to `"Organization Details"` Page.

> Added "Delete Comment" Functionality to `"Challenge Details"` Page.

> Added "Add Comment" Functionality to `"Challenge Details"` Page.

> Added Avatar Preview to `"Create a new Account"`, `"Edit Profile"`, `"Post a Challenge"`, `"Edit Challenge"`, `"Create an Organization"`, and `"Edit Orgazization"` Pages.

### Fixes

> Improved JS.

> Improved Design.

> Improved Emails Contents.

> Improved Styles of Forms' Input Fields.

### Changes

> Added Dropdowns to Tabs on "My Profile" Page.

> Refactored Email to be in HTML Format.

> Updated `"Challenge Participants"` Tab.

> Redesigned `"Edit Profile"` Page.

> Redesigned `"Create a new Account"` Page.

> Redesigned `"Create an Organization"` Page.

> Redesigned `"Post a Challenge"` Page.

v.0.1.4 (2015-01-30)
--------------------
### New

> Added "Contact us" Functiopnality.

> Added "Django Bower".

> Added "Invite Reject" Functionality.

> Added "Invite Accept" Functionality.

> Added "Invite" Functionality.

> Added showing short Name instead of full Name.

> Added Field "Nickname" to User Profile.

> Added initial Commit for Ratings.

### Fixes

> Fixed `"Members List"` Page.

> Fixed **NavBar**.

> Fixed "View on Map" Functionality.

### Changes

> Removed statement "Selfreflection" with "Experience Report" on Front-end. Back-end remains the same to keep everything in sync.

> Improved `"My Profile"` Page Appearance.

v.0.1.3 (2015-01-23)
--------------------
### New

> Added "Privacy Policy" and "User Agreement" pop-up Modals.

> Added "View on Map" for Challenge.

> Added Organizations Specs.

> Integrated AWS S3.

> Integrated AWS RDS.

### Fixes

> Fixed `"Create a new Account"` Page Appearence.

> Fixed Privacy on `"User Profile"` Page.

> Fixed upcoming Challenges List of Organization on `"Organizations List"` Page.

> Fixed Organization Appearence on `"Organizations List"` Page.

> Fixed "About", and "Contact" Links on **NavBar**.

### Changes

> Changed Countries List Order.

> Small Changes to `"Privacy Policy"` Page.

> Small Changes to `"Organization Details"` Page.

> Small Changes to `"Challenge Details"` Page.

v.0.1.2 (2015-01-21)
--------------------
### New

> Added Google Social Authorization.

> Added LinkedIn Social Authorization.

> Added Twitter Social Authorization.

> Added "Accept Experience Report" Functionality.

> Added "Reject Experience Report" Functionality.

> Added "Submit my Experience (in Challenge)" Functionality.

> Added "I did not participate (in Challenge)" Functionality.

> Sending Email Notifications to Challenge Admin(s), if Challenge was complete.

### Fixes

### Changes

> Code optimization.

v.0.1.1 (2015-01-19)
--------------------
### New

> Added sharing with Challenge in social Networks.

> Sending Email Notifications to Challenge Admin(s), if Challenge was closed (deleted).

> Sending Email Notifications to Challenge Admin(s), if Challenge was modified.

> Added mock-ups for Pages `"Our Team"`, `"Our Partners"`, `"About us"`, and `"Contact us"`.

### Fixes

> Fixed Links in **Footer**.

### Changes

> Changed Styles for Pages `"Privacy Policy"`, and `"User Agreement"`.

> Improved **NavBar** to highlight **"HOME"** Link, when Pages `"Privacy Policy"`, `"User Agreement"`, `"Our Team"`, or `"Our Partners"` is open.
