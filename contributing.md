# Contributing

The pythonkc.org website is a volunteer project maintained by the pythonkc community. This project uses a standard open source model where a designated volunteer maintainer will review and approve any changes.

Please follow the guidelines in this document to ensure the limited volunteer resources are utilized efficiently.


## Reporting Bugs

If you notice a bug when using the website, please open an issue on github with steps to reproduce.
Please be as detailed and descriptive as possible. Including screenshots if it is a UI or data bug would be very helpful as well.

## Requesting Features

Feature discussions should happen on the pythonkc discord server, not in the github issues or discussion boards. Once the group has agreed to implement a feature, an issue should be opened on github to track the work on that feature.

Discussion in the feature issue should be related to active work or to document decisions made in discord discussions. Questions about the work or informal design discussion can happen through discord.

## PR Workflow

When contributing a bug fix or new feature, create a new branch with the issue number for the corresponding bug or feature as part of the branch name following a [conventional commit pattern](https://www.conventionalcommits.org/en/v1.0.0/)

All PRs must use a rebase workflow to maintain the linear history on main. Never merge main into the topic branch.
Bug fixes should generally be squashed or amended to ensure only one commit per bug fix is merged into the commit history on main. Complex features can have multiple commits, but they should be organized into sections of work. Fixup commits should be squashed before merging into main.

If you are new to git or you have not used a rebase workflow before or if you simply need help with something related to the PR workflow, please reach out on the discord server with any questions.

### Commit messages

Conventional commits should be used for the first line of the commit message followed by a description of the changes.

An example of a conventional commit branch and commit message for a bug fix for a hypothetical timezone conversion issue with issue number 12 :
Branch name:

```
fix/12/use-utc-timezone-in-event-schedule
```

Commit message:

```
fix(events): 12 use utc for event schedule datetime calculations

The `schedule_next_event` function was attempting to coerce datetimes into US central time.
This makes sense for an application like pykc.org since this is a local user group, but timezone calculations get complicated fast, and this was causing problems when serializing date values to send to the FE.

To simplify datetime computations and keep everything consistent, this patch refactors all of the datetime handling code throughout the BE to use UTC everywhere. I updated the JS code in the FE to do the local time conversion and formatting. The interchange format between the FE and BE for dates and datetimes will always be an ISO 8601 date or datetime string after this change.

With these changes, we can safely rely on the fact that any and all dates and datetimes in BE code will always be in UTC, and any dates or datetimes parsed from a websocket message or http response on the FE can also be safely converted to local time because of the guaranteed ISO 8601 format.
```

You don't need to document everything in the commit message, but an extended description is helpful for other devs who may need to look through the git history to find context about why something was changed or written the way that it was.

As a rule of thumb, use the commit message to explain *why* you are making the changes you are making, and not *what* those changes are. The code diff already shows what is being changed. The commit message is an opportunity to provide additional context around the change while the details are still fresh in your mind.

In particular, edge cases and other gotchas that you encountered and are likely to trip up other devs that work on the same code later on are good to include in the extended commit message.

Another advantage of adding extended commit messages is that github will autopopulate the PR description from the commit message, so you don't have to type out everything again in the github UI when creating the PR if you add it to the commit message.

## Setting up the local dev environment

This project currently uses hatch for managing its automation. This can change if the community decides to switch to a different project management tool. In which case, this document will need to be updated with the new instructions.

Npm is needed for building the frontend.

Hatch will build the virtual environment it needs to run any automation script on first run. To reset the venvs managed by hatch use `hatch env prune`.


To get started run the following commands to clone and setup the local automation environment. Make sure `npm` and `hatch` are both installed. This will create a `env` directory in the project root which will hold all of the ephemeral env-specific files like .env files, ssl certs, and server config files.

```
git clone https://github.com/GrammAcc/pythonkc.org pykc
cd pykc
npm install
hatch run dev:setup
```

The application will not run with only this setup. You will also need to setup local HTTPS and the discord client id and secret for discord oauth.

### Obtaining discord oauth credentials

You can access the discord application id and secret for oauth through the discord developer portal. An admin will need to add you to the dev team for the pykc oauth application. You can request access in the pythonkc discord server.

Once you have the discord client id and secret, store them in a `.env` file in the project root under the env vars `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET` respectively.

TODO: Add some kind of secrets management to automate this process.

### Local HTTPS

The project uses HTTPS in production and for local development.
Local HTTPS can be set up with the [mkcert](https://github.com/FiloSottile/mkcert) tool.

Create a `env/certs` directory in the project root and follow the installation instructions
for your platform in the mkcert READme, and then you can enable local HTTPS with the
following commands:

```bash
mkcert -install
mkcert -key-file path/to/project/root/env/certs/localhost-key.pem -cert-file path/to/project/root/env/certs/localhost.pem localhost 127.0.0.1 ::1
```

This should install a local certificate authority to your system and browser's CA store and
create a signed SSL certificate for localhost in the `env/certs` directory you just created.

Make sure you store the certificates in the `env/certs` directory so that the server configs generated by the `dev:setup` script will find the certificates when serving the application on localhost.

The fullchain certificate is needed for mobile browsers to validate the certs, and the server config generated by `dev:setup` expects the fullchain cert to be present, so it needs to be added to the `env/certs` directory.
To find the fullchain cert run `mkcert -CAROOT`. Copy the `rootCA.pem` file from this
directory into the `env/certs` directory alongside the other cert files.

**Important!!** Do **NOT** copy the `rootCA-key.pem` file. That is the private key, and it must **NOT** be shared.

Now, when running `hatch run dev:serve`, the site should be available over tls at `https://localhost:8000`.

### Seeding your test user

Seed the database with `hatch run dev:seed`.
Run the application with `hatch run dev:serve`, then navigate to `https://localhost:8000/members/login` and login with discord.
This will create a new user account associated with your discord login.
Back in the shell run `hatch run dev:mkorganizer MyUserName` where `MyUserName` is the "moniker" that was created for your profile/account page.
Now you should have full organizer permissions on the local website, and will be able to test all flows such as event management and member role assignment.

TODO: Automate member account creation and permissions updates without needing to use discord login.

### Hatch Scripts

The following hatch scripts are available for various development tasks:

- Environment setup and automation scripts:
    - `hatch run dev:setup` - setup dev env vars.
    - `hatch run dev:seed` - seed dev database (deletes local user account).
    - `hatch run dev:seed.events` - seed only the events database without deleting the local users.
    - `hatch run dev:seed.members` - seed only the members database without modifying the events database.
    - `hatch run dev:mkorganizer {username}` - set `username` from the members database to have organizer permissions for local testing.
    - `hatch run dev:serve` - Run the application with hypercorn in the dev environment.
    - `hatch run dev:stop` - Kill the dev server if running in the background. E.g. with `hatch run dev:serve &`.
    - `hatch run test:setup` - same as dev:setup but for the test env instead of the dev env.
    - `hatch run test:seed` - same as dev:seed but for the test env instead of the dev env.
    - `hatch run test:seed.events` - same as dev:seed.events but for the test env instead of the dev env.
    - `hatch run test:seed.members` - same as dev:seed.members but for the test env instead of the dev env.
    - `hatch run test:serve` - same as dev:serve but for the test env instead of the dev env.
    - `hatch run test:stop` - Kill the test server if running in the background. E.g. with `hatch run test:serve &`.
    - `hatch run prod:setup` - same as dev:setup but for the prod env instead of the dev env.
    - `hatch run prod:seed` - same as dev:seed but for the prod env instead of the dev env.
    - `hatch run prod:seed.events` - same as dev:seed.events but for the prod env instead of the dev env.
    - `hatch run prod:seed.members` - same as dev:seed.members but for the prod env instead of the dev env.
    - `hatch run prod:serve` - same as dev:serve but for the prod env instead of the dev env.
    - `hatch run prod:stop` - Kill the prod server if running in the background. E.g. with `hatch run prod:serve &`.
    - `hatch run frontend:build` - Build the tailwind CSS and run any other transpilation or build steps for the javascript frontend.
- Documentation automation:
    - `hatch run docs.build` - Generate the static api docs website from source code docstrings.
    - `hatch run docs.serve` - Serve the static api docs website on http://localhost:8000
    - `hatch run docs.test` - Run doctests from the source code doctrings.
- Test Suite:
    - `hatch run test.unit` - service and data tests.
    - `hatch run test.integration` - api tests.
    - `hatch run test.events` - Run all tests related to event management whether they are api or service/data tests.
    - `hatch run test.members` - Run all tests related to member accounts whether they are api or service/data tests.
    - `hatch run test.cov` - run test coverage.
    - `hatch run test.all` - run test env setup and seeding as well as unit, integration, and doc tests.
- Code style:
  - `hatch run format` - Run the python autoformatter.
  - `hatch run lint` - Run the linter.
  - `hatch run frontend:format` - Run the javascript autoformatter.
- Typechecking:
  - `hatch run typecheck` - Run the mypy static typechecker.
- Automation Groups:
  - `hatch run ci` - Run all parts of the automation suite that need to be run in hosted GH CI runners.
  - `hatch run all` - Run the full automation suite including both FE and BE formatters, all test suites, typechecker, and linter.
