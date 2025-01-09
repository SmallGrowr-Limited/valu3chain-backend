# valu3chain-backend
## For development
1. Clone the `valu3chain-backend` project
2. Clone the project and run `npm install` in the root folder on your terminal
3. After installation is done, run `npm start` to begin your local API for valu3chain

## Database
The latest and current database barebone structure is exported to a file called `db-structure.sql`. Our database version is MariaDB 10.5.21 so when you install a SQL docker for work, please take note.

# Create a pull request (PR)

Please follow the instructions below for a faster review process and to maintain organization.

1. **Branch Naming:** 

   Create branches according to the ticket type. For bug fixes, use `bugfix/[TICKET-ID]`, for features, `feature/[TICKET-ID]`, and for refactor tasks, `refactor/[TICKET-ID]`. Refer to this cheat sheet for guidance: https://danielkummer.github.io/git-flow-cheatsheet/

2. **Commit Messages:**

   Adhere to the conventional commits format. More information can be found here: https://www.conventionalcommits.org/en/v1.0.0/

3. **PR Naming:**

   Naming your PR following by ticket number and title, for example your ticket number is `VALU3CHAIN-18 [BE] Add staging basic authentication` then your PR should be `VALU3CHAIN-18 Add staging basic authentication`.
      > **NOTE:** Please keep in mind that your title should not include quote or double quote (`' or "`)

4. **Ticket Title Modification:**
   
   If the ticket title is too long and not good at describing the problem/future of the PR you working on, please modify it for a better one, for example: 
      > **Ticket is `*VALU3CHAIN-18 [BE] Make staging version protected from our clients and keep private access for in-house dev only`**

      In this case, you can make it better by re-writing it like `VALU3CHAIN-18 Add staging basic authentication`. You also can modify the title of the ticket if you feel it necessary.

5. **PR Descriptions:**

   Please add the description to your PR as well as the screenshot/video if necessary, usually we need some descriptions for a bugfix and screenshot/video for a new feature.

6. **PR Size:**

   Keep changes to `<= 200` line changes. The maximum is `500` line changes. PRs exceeding this will not be approved.

8. **Code Cleanliness:**

   Ensure no unnecessary comments, commented code blocks, or `console.log` statements are left in the final PR. Thoroughly clean up your code before marking the PR ready for review.

9. And lastly, happy coding.
