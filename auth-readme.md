# Authentication in Fooocus

This document explains how to set up and use the authentication system in Fooocus.

## Features

- Custom login page with a modern, responsive design
- Session-based authentication (cookies)
- Support for both light and dark themes
- Secure password handling with SHA-256 hashing

## Setup

1. Rename `auth-example.json` to `auth.json` or create a new `auth.json` file in the root directory.
2. Add user credentials in the following format:

```json
[
    {
        "user": "username1",
        "pass": "password1"
    },
    {
        "user": "username2",
        "pass": "password2"
    }
]
```

## Security Notes

- Passwords are stored as SHA-256 hashes in memory for security.
- The `auth.json` file is blocked from being accessed through the web interface.
- Authentication is automatically enabled when:
  - The `auth.json` file exists and contains valid credentials
  - AND either the `--share` or `--listen` arguments are used when starting Fooocus

## Command Line Options

To enable authentication when sharing your instance or making it accessible on the network:

```bash
python launch.py --share
```

or

```bash
python launch.py --listen 0.0.0.0
```

## Customization

You can modify the `auth.json` file to add, remove, or update user credentials. The changes will take effect the next time you restart Fooocus. 