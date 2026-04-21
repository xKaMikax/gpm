from __future__ import annotations

from core import PackageManager


def run_gpm(args: list[str]) -> str:
    manager = PackageManager()
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

    if sub in {"install", "i"}:
        if len(args) < 2:
            return "Использование: gpm install <package>"
        package_name = args[1]
        ok, message = manager.install(package_name)
        return message

    if sub in {"reinstall", "ri"}:
        if len(args) < 2:
            return "Использование: gpm reinstall <package>"
        package_name = args[1]
        ok, message = manager.install(package_name, force=True)
        return message

    if sub in {"remove", "uninstall", "rm"}:
        if len(args) < 2:
            return "Использование: gpm remove <package>"
        package_name = args[1]
        if package_name == "gpm":
            return "Для удаления/починки gpm используйте gpmi (install/reinstall/update)."
        ok, message = manager.remove(package_name)
        return message

    if sub in {"update", "up"}:
        if len(args) < 2 or args[1] == "all":
            installed = manager.list_installed()
            if not installed:
                return "Нет установленных пакетов."
            messages: list[str] = []
            for package_name in installed:
                _, msg = manager.update(package_name)
                messages.append(msg)
            return "\n".join(messages)
        ok, message = manager.update(args[1])
        return message

    if sub in {"upgrade", "full-upgrade"}:
        return run_gpm(["update", "all"])

    if sub == "list":
        installed = manager.list_installed()
        if not installed:
            return "Нет установленных пакетов."
        lines = ["Установленные пакеты:"]
        for package_name in sorted(installed.keys()):
            info = installed[package_name]
            lines.append(f"- {package_name} ({info.get('version', '?')})")
        return "\n".join(lines)

    if sub in {"search", "find"}:
        query = args[1] if len(args) > 1 else ""
        try:
            packages = (
                manager.search_store_packages(query) if query else manager.list_store_packages()
            )
        except Exception as exc:
            return f"Ошибка поиска в store: {exc}"
        if not packages:
            return "Ничего не найдено."
        prefix = f"Найдено пакетов ({len(packages)}):"
        return "\n".join([prefix, *[f"- {name}" for name in packages]])

    if sub == "info":
        if len(args) < 2:
            return "Использование: gpm info <package>"
        package_name = args[1]
        local = manager.get_installed_info(package_name)
        if local:
            return (
                f"{package_name}\n"
                f"name: {local.get('name', '')}\n"
                f"author: {local.get('author', '')}\n"
                f"version: {local.get('version', '')}\n"
                f"description: {local.get('description', '')}\n"
                f"command: {local.get('command', '')}"
            )
        try:
            remote = manager.fetch_info_from_store(package_name)
        except Exception:
            return f"Пакет '{package_name}' не установлен."
        return (
            f"{package_name} (store)\n"
            f"name: {remote.name}\n"
            f"author: {remote.author}\n"
            f"version: {remote.version}\n"
            f"description: {remote.description}\n"
            f"command: {remote.command}"
        )

    if sub == "outdated":
        outdated, errors = manager.outdated()
        lines: list[str] = []
        if outdated:
            lines.append("Доступны обновления:")
            lines.extend(f"- {entry}" for entry in outdated)
        else:
            lines.append("Все пакеты актуальны.")
        if errors:
            lines.append("Ошибки проверки:")
            lines.extend(f"- {entry}" for entry in errors)
        return "\n".join(lines)

    if sub == "doctor":
        return "\n".join(manager.doctor())

    return f"Неизвестная команда gpm: {sub}"
