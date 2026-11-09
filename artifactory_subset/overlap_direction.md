# Overlap direction summary

Overlap rows (both host string and artifactory): 2114

Group A count 334; Group B count 97.

## Pattern counts

| pattern | A | B | overlap |
|---|---|---|---|
| getent | 81 | 13 | 21 |
| /dev/tcp | 24 | 0 | 0 |
| DNS | 130 | 18 | 56 |
| artifactproperties | 5 | 0 | 0 |
| ui/api | 21 | 13 | 0 |
| api/system/ping | 0 | 4 | 48 |
| github-remote | 15 | 22 | 1960 |
| github-remote-cache | 11 | 20 | 991 |
| PROXY | 70 | 9 | 267 |
| SERVICE | 141 | 44 | 1101 |
| encoded | 115 | 53 | 423 |

## Operational differences

- Group A is host-only references: DNS probes/getent, /dev/tcp port checks, host enumeration; often no artifactory path.

- Group B is artifactory-only references: appears as encoded/proxy path strings or dependency cache paths; less DNS probing.

- Overlap dominates and contains full URLs with /artifactory/ paths such as github-remote/github-remote-cache.
