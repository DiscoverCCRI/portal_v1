# USAGE Overview

## Admin rights
To provide the user with administrative rights a few manual changes can be made to Django admin.

You must have the first run of the portal and login into your account before doing following instructions.

After the first run, terminal the portal by pressing `Ctrl C` at the command line.

From the command line, type the command `python manage.py createsuperuser`, and enter following information (`Username`, `Email address`, and `Password`)

```console
$ python manage.py createsuperuser
Username: discover_admin
Email address: discover@gmail.com
Password: ******
Password (again): ******
Supersuser created successfully.
```

Then run the portal and navigate to [https://127.0.0.1:8443/admin](https://127.0.0.1:8443/admin)

![](docs/images/site_admin_login.PNG)

Use the information for `Username` and `Password` to login the admin page. Here is an example of admin page:

![](docs/images/site_admin_page.PNG)

Go to `Users` in the section `ACCOUNTS`, here is the example of `Users` page:

![](docs/images/users_admin_page.PNG)

At the section `Select user to change`, select account to change the admin rights (usually account has `OIDC CLAIM SUB` with CILogon link).

That direct to user selected page, at the `Groups` of the section `Permissions`, select `Choose all` to select all roles

![](docs/images/groups_admin.PNG)

Verify the change by scrolling down at the bottom of current page and select `SAVE`

![](docs/images/verify_changes_admin.PNG)

Finally, you successfully assigned your account to have admin rights and come back to [https://127.0.0.1:8443/](https://127.0.0.1:8443/) to login again.
