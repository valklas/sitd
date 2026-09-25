# SITD

SITD (**S**erve **I**t **T**o **D**evices) allows you to run a server on your local machine and upload files/folders and access them from another device on the same network that has a browser or [curl](https://github.com/curl/curl)/[wget](https://www.gnu.org/software/wget/).

## Development

This project includes a **flake.nix** so you can do:

```bash
nix develop
```

in the project root. This will install the required packages/dependencies and start `fish` as the shell.

## Running Server

Once you install the required packages/dependencies, you can run the server from project root using:

```bash
uvicorn sitd.server:app --host 0.0.0.0 --reload
```

Then you can visit the web page from any device using:

```plaintext
machineip:8000
```

Machine ip is the ip of the machine that the server is running on.

## Third-partie resources/assets

See [LICENSES](LICENSES/)

## LICENSE

This project is under [MIT](LICENSE).
