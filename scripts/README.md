# Helper Scripts

Small scripts added to assist in development or deployment in various scenarios. Please look at each script before using it.

## script: `clean-it-all-up.sh`

### Use this script with caution!

Stop:

- any running docker containers defined in docker-compose.yaml

Remove: 

- docker containers, networks, and volumes defined in docker-compose.yaml
- all migrations directories
- pg_data (PostgreSQL data volume mount)

Recreate:

- pg_data (PostgreSQL data volume mount)


### Usage:

```
$ ./clean-it-all-up.sh
### ALERT: stopping and removing docker containers
Stopping aerpaw-nginx ... done
Stopping aerpaw-db    ... done
Going to remove aerpaw-nginx, aerpaw-db
Removing aerpaw-nginx ... done
Removing aerpaw-db    ... done
### ALERT: removing associated docker networks
aerpaw-portal_default
### ALERT: removing migrations files
    - /Users/stealey/GitHub/aerpaw/aerpaw-portal/reservations/migrations
    - /Users/stealey/GitHub/aerpaw/aerpaw-portal/experiments/migrations
    - /Users/stealey/GitHub/aerpaw/aerpaw-portal/projects/migrations
    - /Users/stealey/GitHub/aerpaw/aerpaw-portal/resources/migrations
    - /Users/stealey/GitHub/aerpaw/aerpaw-portal/accounts/migrations
### ALERT: removing volume mounts
### ALERT: replacing volume mounts
```


