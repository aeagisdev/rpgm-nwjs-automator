# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.2.x   | Yes       |
| 2.1.x   | Security fixes only |
| < 2.0   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email the maintainer at **aegisdev@proton.me** with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
3. You will receive an acknowledgment within 48 hours
4. A fix will be prioritized and released as a patch version

## Security Model

### What This Tool Does

NW.js Automator downloads NW.js binaries from official sources and replaces RPG Maker MV/MZ game runtimes. It operates on local files with the permissions of the user running it.

### Trust Boundaries

| Component | Trust Level | Notes |
|-----------|-------------|-------|
| NW.js downloads | Remote, verified | Downloaded only from `dl.nwjs.io` via HTTPS |
| Game directories | User-provided, validated | Path traversal protection applied |
| Plugin system | Local, user-installed | Plugins execute arbitrary Python code |
| Configuration files | Local JSON | Validated before loading |
| Batch file lists | Local, user-provided | Paths validated individually |

### Built-in Protections

**Input Validation**
- All user-provided paths are validated against path traversal attacks (`../`, symlink resolution)
- File and directory names are checked against safe patterns
- URLs are restricted to an allowlist of trusted domains (`dl.nwjs.io`, `github.com`, `api.github.com`)

**Download Security**
- NW.js binaries are downloaded exclusively over HTTPS
- Download URLs are validated against the official NW.js domain
- Backup integrity is verified with SHA-256 checksums

**File Operations**
- Critical game files (`package.json`, `www/`, `index.html`) are protected by a whitelist and cannot be accidentally deleted
- Automatic backups are created before any modifications
- Rollback system restores original files on failure

**Plugin Sandboxing**
- Plugins are loaded only from explicit directories (`plugins/` and `~/.nwjs_automator/plugins/`)
- Plugin discovery requires a class that subclasses `PluginInterface`
- Plugins cannot override core processing logic, only hook into defined extension points

### Known Limitations

- **Plugins execute with full user privileges.** Only install plugins from trusted sources. The plugin system does not sandbox code execution.
- **No binary signature verification.** Downloaded NW.js archives are not verified against GPG signatures or published checksums from the NW.js project (the project does not currently publish signed checksums).
- **macOS builds are unsigned.** Release artifacts for macOS will trigger Gatekeeper warnings. Users must manually allow execution.
- **No automatic CVE scanning** of bundled NW.js versions. Users should check the [NW.js releases](https://nwjs.io/) and Chromium security advisories for their chosen version.

## Dependencies

| Dependency | Purpose | Risk |
|------------|---------|------|
| `requests` | HTTP downloads | Widely audited, HTTPS only |
| `psutil` | Process management | Read-only system info |
| `PySide6` / `PyQt6` | GUI (optional) | Qt framework, large attack surface but local-only |
| `pywin32` | Windows shortcuts (optional) | COM interface, Windows-only |

Keep dependencies updated:

```bash
pip install --upgrade -r requirements.txt
```

## Best Practices for Users

- **Review plugins** before installing them in the `plugins/` directory
- **Use SDK builds** only for development -- production games should use normal builds to prevent end-user access to developer tools
- **Keep backups** enabled (the default) when processing games
- **Verify game integrity** after processing by launching the game and checking core functionality
- **Use specific NW.js versions** rather than "latest" for reproducible builds
