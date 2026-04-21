from __future__ import annotations

from core import PackageManager


def run_gpm(args: list[str]) -> str:
    manager = PackageManager()
    
    commands_map = {
        "install": ["install", "i"],
        "reinstall": ["reinstall", "ri"],
        "remove": ["remove", "uninstall", "rm"],
        "update": ["update", "up"],
        "upgrade": ["upgrade", "full-upgrade"],
        "list": ["list"],
        "search": ["search", "find"],
        "info": ["info"],
        "outdated": ["outdated"],
        "doctor": ["doctor"],
    }

    if not args:
        return "\n".join(
            [
                "gpm commands:",
                "  install <package>",
                "  reinstall <package>",
                "  remove <package>",
                "  update <package|all>",
                "  upgrade (alias update all)",
                "  list",
                "  search [query]",
                "  info <package>",
                "  outdated",
                "  doctor",
            ]
        )

    sub = args[0]

    if sub in commands_map["install"]:
        if len(args) < 2:
            return "Usage: gpm install <package>"
        ok, message = manager.install(args[1])
        return message

    if sub in commands_map["reinstall"]:
        if len(args) < 2:
            return "Usage: gpm reinstall <package>"
        ok, message = manager.install(args[1], force=True)
        return message

    if sub in commands_map["remove"]:
        if len(args) < 2:
            return "Usage: gpm remove <package>"
        package_name = args[1]
        if package_name == "gpm":
            return "To remove/repair gpm, use gpmi (install/reinstall/update)."
        ok, message = manager.remove(package_name)
        return message

    if sub in commands_map["update"]:
        if len(args) < 2 or args[1] == "all":
            installed = manager.list_installed()
            if not installed:
                return "No packages installed."
            messages = []
            for name in installed:
                _, msg = manager.update(name)
                messages.append(msg)
            return "\n".join(messages)
        ok, message = manager.update(args[1])
        return message

    if sub in commands_map["upgrade"]:
        return run_gpm(["update", "all"])

    if sub in commands_map["list"]:
        installed = manager.list_installed()
        if not installed:
            return "No packages installed."
        lines = ["Installed packages:"]
        for name in sorted(installed.keys()):
            info = installed[name]
            lines.append(f"- {name} ({info.get('version', '?')})")
        return "\n".join(lines)

    if sub in commands_map["search"]:
        query = args[1] if len(args) > 1 else ""
        try:
            packages = (
                manager.search_store_packages(query) if query else manager.list_store_packages()
            )
        except Exception as exc:
            return f"Store search error: {exc}"
        if not packages:
            return "No results found."
        prefix = f"Found packages ({len(packages)}):"
        return "\n".join([prefix, *[f"- {name}" for name in packages]])

    if sub in commands_map["info"]:
        if len(args) < 2:
            return "Usage: gpm info <package>"
        package_name = args[1]
        local = manager.get_installed_info(package_name)
        
        data = local if local else None
        source_label = ""
        
        if not data:
            try:
                remote = manager.fetch_info_from_store(package_name)
                data = {
                    "name": remote.name,
                    "author": remote.author,
                    "version": remote.version,
                    "description": remote.description,
                    "command": remote.command,
                    "help_menu": getattr(remote, "help_menu_description", {})
                }
                source_label = " (store)"
            except Exception:
                return f"Package '{package_name}' not found."

        output = [
            f"{package_name}{source_label}",
            f"name: {data.get('name', '')}",
            f"author: {data.get('author', '')}",
            f"version: {data.get('version', '')}",
            f"description: {data.get('description', '')}",
            f"command: {data.get('command', '')}"
        ]
        
        help_menu = data.get("help_menu") or data.get("help_menu_description")
        if help_menu:
            output.append("\nflags:")
            for flag, desc in help_menu.items():
                output.append(f"  {flag.ljust(6)} {desc}")
                
        return "\n".join(output)

    if sub in commands_map["outdated"]:
        outdated, errors = manager.outdated()
        lines = []
        if outdated:
            lines.append("Updates available:")
            lines.extend(f"- {entry}" for entry in outdated)
        else:
            lines.append("All packages are up to date.")
        if errors:
            lines.append("Check errors:")
            lines.extend(f"- {entry}" for entry in errors)
        return "\n".join(lines)

    if sub in commands_map["doctor"]:
        return "\n".join(manager.doctor())

    return f"Unknown gpm command: {sub}"
