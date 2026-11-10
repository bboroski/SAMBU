# Black Duck SCA in GitHub Actions

SAMBU's security workflow uses **Black Duck SCA only**. Polaris, Coverity and Software Risk Manager (SRM) are separate products with separate endpoints and credentials; merely supplying their optional input fields does not enable those scans.

## Required GitHub configuration

Open the repository's **Settings → Secrets and variables → Actions**.

Create the following repository-level values (organization-level values are also supported when they are made available to this repository):

| Name | GitHub type | Value |
|---|---|---|
| `BLACKDUCKSCA_URL` | Actions variable | HTTPS base URL of the actual Black Duck SCA server |
| `BLACKDUCKSCA_TOKEN` | Actions secret | Black Duck SCA API access token |

For Black Duck SCA SaaS, the official quickstart gives `https://sca.blackduck.com` as an example URL. Use the exact URL supplied by your organization's Black Duck administrator for an on-premises or regional deployment; do not guess the host.

Create the API token from the Black Duck SCA user profile / access-token area. The account must have a role that permits the required scan operations and token creation. Follow your organization's least-privilege policy. **Do not put the token in this file, a commit, an issue, a pull-request comment, or a chat message.** Store it only as the GitHub Actions secret.

## What the workflow does

File: `.github/workflows/black-duck-security-scan-ci.yml`

- Runs on pushes to `main`, pull requests targeting `main`, the weekly schedule, and manual `workflow_dispatch`.
- Validates that the URL and token are present before invoking the vendor action. The token is never echoed.
- Rejects non-HTTPS URLs and reports the exact missing setting instead of allowing the action to fail later with a generic “Requires at least one scan type” error.
- Uses the Black Duck SCA provider only; unconfigured Polaris, Coverity and SRM inputs are not passed.
- Uses a full/intelligent scan on branch, scheduled and manual runs; pull requests use the action's rapid/differential mode.
- Names the Black Duck project after the GitHub repository and uses the target branch as the PR version name.
- Fails the workflow when Black Duck reports CRITICAL or HIGH findings.
- Pins the official Black Duck Security Scan action to the immutable commit for release `v2.11.0`.
- Does not enable PR comments, automatic fix PRs, GitHub issue creation or SARIF upload. Those features require additional permissions and have intentionally not been enabled.
- Skips fork-originated `pull_request` runs because GitHub does not expose repository secrets to those runs. It does not use `pull_request_target` to bypass that protection.

## Verify the setup

1. Add the Actions variable `BLACKDUCKSCA_URL`.
2. Add the Actions secret `BLACKDUCKSCA_TOKEN`.
3. Open **Actions → CI Black Duck SCA → Run workflow** and start a run on `main`.
4. Confirm that the preflight step reports the configuration is present, then that the **Black Duck SCA scan** step starts and completes.
5. Open the Black Duck SCA project/version created for the repository and verify the scan timestamp and findings.

A workflow run that stops at preflight is intentionally not counted as a scan. If a scan starts but cannot reach the server, check that the GitHub-hosted runner can resolve and access the configured HTTPS endpoint and trust its TLS certificate. For a private network-only server, use an approved self-hosted runner with the appropriate network access and certificate trust.

## Common failures

| Symptom | Likely cause | Corrective action |
|---|---|---|
| `Missing Actions variable BLACKDUCKSCA_URL` | URL variable is absent or named differently | Add the exact variable name shown above |
| `Missing Actions secret BLACKDUCKSCA_TOKEN` | Token secret is absent or named differently | Add/rotate the token as an Actions secret |
| URL validation fails | The value is not an HTTPS base URL | Copy the endpoint from the Black Duck administrator |
| Authentication / authorization failure | Expired token, wrong server, or insufficient role | Rotate the token and verify account permissions |
| Connection or TLS failure | Runner cannot reach server or does not trust its certificate | Check networking, DNS, proxy and CA trust; use a suitable self-hosted runner if the server is private |
| Scan reports HIGH/CRITICAL findings | The configured security gate is working | Review the findings in Black Duck and resolve, suppress or accept them through the organization's review process |

## Upstream references

- [Black Duck Security Scan action](https://github.com/blackduck-inc/black-duck-security-scan)
- [Official Black Duck SCA quickstart](https://docs.blackduck.com/r/bridge/latest/bridge-cli-guide/quickstart-black-duck-security-scan-action-with-black-duck-sca.html)
- [Black Duck SCA action configuration](https://docs.blackduck.com/r/bridge/latest/bridge-cli-guide/using-the-black-duck-security-scan-action-with-black-duck-sca.html)

