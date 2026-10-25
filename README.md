# Hammerspoon — personal fork

[![Personal arm64 build](https://github.com/psedik/hammerspoon/actions/workflows/personal-build.yml/badge.svg)](https://github.com/psedik/hammerspoon/actions/workflows/personal-build.yml)

This is [psedik's personal fork](https://github.com/psedik/hammerspoon) of [Hammerspoon](https://github.com/Hammerspoon/hammerspoon), a macOS automation application that exposes system APIs to Lua scripts. It retains the upstream application name and bundle identifier. It is not an official Hammerspoon release or a security-certified distribution.

## Changes in this fork

- Removed Sparkle from the personal build's dependencies. The packaged app contains no Sparkle updater or XPC bundles, and updates must be installed manually.
- Upgraded the embedded Lua runtime from 5.4.7 to **5.5.1**, retaining Hammerspoon's module search paths and Objective-C exception bridge. Updated the application module to use the standard C `INT_MAX` constant instead of an internal Lua macro.
- Added a manually triggered GitHub Actions workflow for an **Apple Silicon / arm64 Release build**, using Hardened Runtime and `-Os` optimization.
- Disabled Xcode's automatic base-entitlement injection and made packaging fail if the main app has `com.apple.security.get-task-allow` enabled.
- Removed the main app's `allow-jit`, `allow-unsigned-executable-memory`, and `disable-executable-page-protection` entitlements. Library-validation relaxation remains enabled for the ad-hoc-signed native modules; it also permits loading unsigned native modules from user-controlled Lua search paths.
- Added a Lua runtime smoke test covering Lua errors, the Objective-C exception bridge, coroutines, garbage collection, and syntax loading of the bundled Lua scripts.

The workflow has read-only repository permissions, pins its checkout and artifact-upload actions to commit hashes, and does not persist checkout credentials. It verifies the main executable's architecture, code signatures, updater absence, and the debugger entitlement before packaging. These checks reduce specific risks; they do not prove that every dependency or build machine is uncompromised.

## Build and install

With repository write access, run **Personal arm64 build** from the repository's [Actions page](https://github.com/psedik/hammerspoon/actions/workflows/personal-build.yml). Other users can fork this repository and run the workflow in their own fork. The workflow uses a GitHub-hosted `macos-15` runner with Xcode; a local build of the full application also requires full Xcode, not just Command Line Tools.

A successful run produces a `Hammerspoon-arm64-<run number>` artifact containing:

- `Hammerspoon-arm64.zip` and its `SHA256SUMS` file;
- the source revision, Xcode version, resolved Podfile lock, and app entitlements;
- the complete Xcode build log.

Artifacts expire after 14 days. Download the artifact, extract the outer archive, and compute the inner app archive's checksum from the extracted directory:

```sh
shasum -a 256 Hammerspoon-arm64.zip
cat SHA256SUMS
```

Compare the 64-character hash on both lines; it must match. The recorded filename includes the workflow's `artifacts/` directory prefix, so `shasum -c SHA256SUMS` does not work directly from the extracted directory. The checksum detects archive corruption; because it is produced by the same workflow, it is not independent proof of a trustworthy build. Check the run's source revision as well.

Extract `Hammerspoon-arm64.zip`, quit any running Hammerspoon instance, and install `Hammerspoon.app` in `~/Applications`. Keep a backup of the previous working version. This fork shares the upstream bundle identifier, so avoid running the upstream and forked apps simultaneously.

The build is **ad-hoc signed and not notarized**. macOS may require explicit approval before opening it. A new build may also invalidate its Accessibility approval: if shortcuts or text insertion stop working, remove the old entry in **System Settings → Privacy & Security → Accessibility**, add the newly installed app, enable it, and restart Hammerspoon. Stable release signing has not been set up.

`brew install --cask hammerspoon` installs the upstream distribution, not this fork. This repository does not provide a custom Homebrew cask or automatic update service. Review upstream changes and dependencies before creating later builds.

## Configuration and security boundaries

Sentry remains a linked dependency. The personal workflow supplies no Sentry API URL, and build 4 reports `Sentry API URL unavailable`; the application's Sentry startup code is conditional on that build-time setting. Removing Sparkle does not make Hammerspoon an offline application.

Hammerspoon still loads user configuration from `~/.hammerspoon/init.lua`. Lua code runs with the capabilities available to Hammerspoon and the user's account; it is **not sandboxed**. Only run configuration and extensions you trust.

This fork does not make user configuration immutable. A process that can modify the configuration or a helper program it invokes can change what a shortcut does. Configuration edits take effect on the next load or reload; helper edits take effect on the next invocation. Ad-hoc signing does not protect external Lua or Python files, and the app in `~/Applications` is also writable by its owner. Root-owned deployment, protected configuration, and a stable signing identity remain future work.

The `hs.ipc` and AppleScript execution features have not been removed from the application. Whether they are enabled depends on local settings and configuration. In the maintainer's local setup, the general Lua IPC command port and Lua execution through AppleScript are disabled. Local dictation fixes add destination checks, private recording files, and failure handling, but **those personal Lua scripts and their Python helper are not included in this repository**. Installing this fork alone does not install those controls.

Destination checks in an automation script are not a security boundary against a hostile local process, every focus race, or a CLI coding agent's internal approval and command modes. Accessibility permission remains powerful even with the updater removed and the release entitlements reduced.

## Verification performed

[Build 4](https://github.com/psedik/hammerspoon/actions/runs/40208079811), from revision `fbd58cac`, successfully built and packaged application build `6942` with Lua 5.5.1. The runtime test and syntax checks passed on the runner. Local validation checked both archive hashes, the app signature, arm64 architecture, updater absence, and the reduced entitlements.

An isolated startup test loaded 17 commonly used native modules, including application/window control, event taps, tasks, pasteboard, Accessibility, and webview support. This was a targeted build and runtime check, not a complete audit or a test of every Hammerspoon module. Documentation and About-panel updates after that revision do not change these recorded results; they appear in subsequent builds.

To run the vendored Lua smoke test locally with Apple Command Line Tools:

```sh
python3 scripts/test_lua_runtime.py
```

## Upstream project and credits

Hammerspoon grew out of [Mjolnir](https://github.com/mjolnirapp/mjolnir). The original authors, contributors, application icon credits, and third-party license notices are retained in the source and About panel. The updated Lua sources retain their upstream license.

- [Getting Started](https://www.hammerspoon.org/go/)
- [API documentation](https://www.hammerspoon.org/docs/)
- [FAQ](https://www.hammerspoon.org/faq/)
- [Upstream releases](https://github.com/Hammerspoon/hammerspoon/releases)
- [Upstream contribution guide](https://github.com/Hammerspoon/hammerspoon/blob/master/CONTRIBUTING.md)
