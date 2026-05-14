# envdiff

Compare environment variable sets across `.env` files and running processes to surface drift.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git && cd envdiff && pip install .
```

---

## Usage

Compare two `.env` files:

```bash
envdiff .env .env.production
```

Compare a `.env` file against the current running environment:

```bash
envdiff .env --process
```

Compare against a specific process by PID:

```bash
envdiff .env --pid 12345
```

Example output:

```
KEY              .env              production
─────────────────────────────────────────────
DATABASE_URL     postgres://local  postgres://prod-host
DEBUG            true              <missing>
NEW_RELIC_KEY    <missing>         abc123xyz
```

### Options

| Flag | Description |
|------|-------------|
| `--process` | Diff against the current shell environment |
| `--pid PID` | Diff against a running process by PID |
| `--only-missing` | Show only keys absent from one side |
| `--json` | Output results as JSON |

---

## Contributing

Bug reports and pull requests are welcome. Please open an issue first for major changes.

---

## License

[MIT](LICENSE)