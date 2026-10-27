# Python Modules and Packages
from ipaddress import IPv4Address
import socket
from uuid import UUID

import psutil

from .helpers import ToolError, confirm, logged_action, read_number, run_menu
from .windows import is_admin, powershell, powershell_json, request_admin, require_admin


# Python Data Structures - Dictionary
# Python Data Structures - List
DNS_PROVIDERS = {
    "1": {"name": "Cloudflare", "servers": ["1.1.1.1", "1.0.0.1"],
          "description": "Standard resolver with no content filtering."},
    "2": {"name": "Google Public DNS", "servers": ["8.8.8.8", "8.8.4.4"],
          "description": "General-purpose public DNS resolver."},
    "3": {"name": "Quad9", "servers": ["9.9.9.9", "149.112.112.112"],
          "description": "Recommended service with malicious-domain blocking."},
    "4": {"name": "OpenDNS", "servers": ["208.67.222.222", "208.67.220.220"],
          "description": "Cisco's standard public resolvers; filtering depends on service settings."},
}

READ_ADAPTERS = r"""
$items = @(foreach ($adapter in @(Get-NetAdapter | Sort-Object InterfaceIndex)) {
    $dns = Get-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -AddressFamily IPv4
    if ($null -eq $dns) { continue }
    $guid = ([guid]$adapter.InterfaceGuid).ToString('B')
    $key = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\' + $guid
    $properties = Get-ItemProperty -LiteralPath $key
    $manual = [string]$properties.NameServer
    $ips = @(Get-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty IPAddress)
    $gateways = @(Get-NetRoute -InterfaceIndex $adapter.InterfaceIndex -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty NextHop -Unique)
    [pscustomobject]@{
        index = [int]$adapter.InterfaceIndex
        guid = ([guid]$adapter.InterfaceGuid).ToString()
        name = [string]$adapter.Name
        status = [string]$adapter.Status
        ips = $ips
        gateways = $gateways
        mode = $(if ([string]::IsNullOrWhiteSpace($manual)) { 'automatic' } else { 'static' })
        servers = @($dns.ServerAddresses)
    }
})
ConvertTo-Json -InputObject $items -Depth 5 -Compress
"""

REFRESH_DNS_CACHE = r"""
try {
    Clear-DnsClientCache -ErrorAction Stop
    [pscustomobject]@{ success = $true } | ConvertTo-Json -Compress
} catch {
    [pscustomobject]@{ success = $false; reason = [string]$_.Exception.Message } |
        ConvertTo-Json -Compress
}
"""

WRITE_DNS = r"""
$adapter = Get-NetAdapter -InterfaceIndex ([int]$data.index)
if (([guid]$adapter.InterfaceGuid).ToString() -ne [string]$data.guid) {
    throw 'The adapter identity changed. Refresh the adapter list.'
}
$dns = Get-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -AddressFamily IPv4
if ($null -eq $dns) { throw 'IPv4 DNS is unavailable on this adapter.' }
if ($data.mode -eq 'automatic') {
    Set-DnsClientServerAddress -InputObject $dns -ResetServerAddresses
} else {
    Set-DnsClientServerAddress -InputObject $dns -ServerAddresses ([string[]]$data.servers)
}
"""


# Python OOP - Classes
class NetworkTool:
    # Python Functions, Arguments and Return Values
    def __init__(self, store):
        self.store = store

    def run(self):
        if not is_admin():
            print("Windows will ask for administrator approval when a protected action is selected.")
        # Python Data Structures - Tuple
        run_menu("NETWORK OPTIMIZATION", {
            "1": ("Auto optimize (inspect connection and refresh DNS cache)", self.auto_optimize),
            "2": ("DNS changer (administrator)", self.change_dns),
            "3": ("Restore saved IPv4 DNS configuration (administrator)", self.restore_dns),
            "4": ("Use automatic IPv4 DNS (DHCP; administrator)", self.automatic_dns),
        })

    def adapters(self):
        result = powershell_json(READ_ADAPTERS)
        # Python Flow Control - Conditionals
        if not isinstance(result, list):
            raise ToolError("Windows did not return an adapter list.")
        return result

    def display_adapter(self, adapter):
        # Python String Operations
        print(f"{adapter['name']} (index {adapter['index']}), {adapter['status']}")
        print(f"  IPv4: {', '.join(adapter['ips']) or 'none'}")
        print(f"  Default gateways: {', '.join(adapter['gateways']) or 'none'}")
        print(f"  IPv4 DNS ({adapter['mode']}): {', '.join(adapter['servers']) or 'none'}")

    def choose_adapter(self):
        adapters = self.adapters()
        if not adapters:
            raise ToolError("No supported network adapters were found.")
        # Python Flow Control - Loops
        for number, adapter in enumerate(adapters, start=1):
            print(f"\n{number}.", end=" ")
            self.display_adapter(adapter)
        choice = read_number("Adapter number (0 to cancel): ", 0, len(adapters))
        # Python Arithmetic Operations
        return adapters[choice - 1] if choice else None

    def fresh_adapter(self, guid):
        guid = str(UUID(str(guid)))
        for adapter in self.adapters():
            if str(UUID(adapter["guid"])) == guid:
                return adapter
        raise ToolError("The saved adapter is missing. Reconnect it before restoring.")

    def validate_config(self, config):
        if not isinstance(config, dict) or config.get("mode") not in ("automatic", "static"):
            raise ValueError("Invalid DNS restoration data; preserve settings.json for inspection.")
        guid = str(UUID(str(config.get("guid"))))
        servers = config.get("servers")
        if not isinstance(servers, list):
            raise ValueError("DNS server addresses must be a list.")
        servers = [str(IPv4Address(address)) for address in servers]
        if config["mode"] == "static" and not servers:
            raise ValueError("Cannot restore static DNS without saved addresses.")
        return {"guid": guid, "mode": config["mode"], "servers": servers}

    def apply_config(self, adapter, config):
        config = self.validate_config(config)
        require_admin()
        powershell(WRITE_DNS, {**config, "index": int(adapter["index"])})
        current = self.fresh_adapter(config["guid"])
        if current["mode"] != config["mode"] or (config["mode"] == "static"
                                                      and current["servers"] != config["servers"]):
            raise ToolError("Windows did not confirm the requested DNS setting. The backup is kept.")
        self.display_adapter(current)

    def inspect_connection(self):
        print("Inspecting local connections (this does not prove internet access):")
        try:
            adapters = self.adapters()
        except (ToolError, OSError):
            print("Detailed adapter information is unavailable; showing basic connection status.")
            try:
                addresses = psutil.net_if_addrs()
                statuses = psutil.net_if_stats()
                for name, status in statuses.items():
                    ipv4 = [address.address for address in addresses.get(name, [])
                            if address.family == socket.AF_INET]
                    print(f"{name}: {'Up' if status.isup else 'Down'}")
                    print(f"  IPv4: {', '.join(ipv4) or 'none'}")
                if not statuses:
                    print("No network interfaces were reported.")
            except (psutil.Error, OSError) as error:
                print(f"Connection details unavailable: {error}")
            return
        for adapter in adapters:
            self.display_adapter(adapter)
        if not adapters:
            print("No supported adapters found; cache maintenance is still available.")

    def restart_as_admin(self, action):
        print("Please approve the Windows administrator prompt to continue.")
        if not request_admin(action, self.store.folder):
            print("Administrator request cancelled. No settings were changed.")
            return "cancelled"
        self.store.log("administrator_access", "approved; continuing in administrator window")
        print("Continuing in the administrator window.")
        raise SystemExit(0)

    # Python Decorators
    @logged_action
    def auto_optimize(self):
        self.inspect_connection()
        print("DNS cache refresh removes cached name lookups, including stale results.")
        print("The next lookup may take longer. This does not guarantee faster internet.")
        print("Windows may ask for administrator approval.")
        if not confirm("Refresh the Windows DNS cache?"):
            return "cancelled"
        if not is_admin():
            return self.restart_as_admin("dns-cache")
        return self.refresh_dns_cache()

    @logged_action
    def refresh_dns_cache(self):
        try:
            result = powershell_json(REFRESH_DNS_CACHE)
        except (ToolError, OSError):
            print("DNS cache refresh skipped: this Windows session could not run cache maintenance.")
            return "cache refresh unavailable"
        if not isinstance(result, dict) or result.get("success") is not True:
            reason = result.get("reason") if isinstance(result, dict) else None
            print(f"DNS cache refresh skipped: {reason or 'Windows did not complete the operation.'}")
            return "cache refresh unavailable"
        print("DNS cache refresh: completed. IP addresses and adapter settings were not changed.")
        return "cache refreshed"

    def save_original(self, adapter):
        original = self.validate_config(adapter)
        self.store.remember(f"dns:{original['guid']}", {**original, "name": adapter["name"]})

    def explain_change(self):
        print("Administrator access is required. Only IPv4 DNS server settings are changed.")
        print("IPv6, VPN rules, and browser secure DNS may use other resolvers.")
        print("Public DNS may break private/work/VPN names. Use a network you manage.")
        print("No provider is universally fastest. These settings do not configure DNS encryption.")

    @logged_action
    def change_dns(self):
        if not is_admin():
            return self.restart_as_admin("dns-change")
        self.explain_change()
        adapter = self.choose_adapter()
        if adapter is None:
            return "cancelled"
        for key, provider in DNS_PROVIDERS.items():
            print(f"{key}. {provider['name']}: {', '.join(provider['servers'])}")
            print(f"   {provider['description']}")
        choice = str(read_number("Provider number (0 to cancel): ", 0, 4))
        if choice == "0":
            return "cancelled"
        provider = DNS_PROVIDERS[choice]
        if not confirm(f"Set {adapter['name']} IPv4 DNS to {provider['name']}?"):
            return "cancelled"
        require_admin()
        adapter = self.fresh_adapter(adapter["guid"])
        self.save_original(adapter)
        print(f"Original configuration saved in {self.store.path}")
        self.apply_config(adapter, {"guid": adapter["guid"], "mode": "static", "servers": provider["servers"]})
        print("DNS change: verified. Use 'Restore saved IPv4 DNS configuration' to undo it.")
        return "DNS changed and verified"

    @logged_action
    def automatic_dns(self):
        if not is_admin():
            return self.restart_as_admin("dns-automatic")
        self.explain_change()
        print("Automatic DNS asks the network's DHCP service for IPv4 DNS servers.")
        adapter = self.choose_adapter()
        if adapter is None:
            return "cancelled"
        if adapter["mode"] == "automatic":
            print("This adapter already uses automatic IPv4 DNS.")
            return "already automatic"
        if not confirm(f"Use automatic IPv4 DNS on {adapter['name']}?"):
            return "cancelled"
        require_admin()
        adapter = self.fresh_adapter(adapter["guid"])
        self.save_original(adapter)
        self.apply_config(adapter, {"guid": adapter["guid"], "mode": "automatic", "servers": []})
        print("Automatic DNS: verified. The original configuration is saved for restoration.")
        return "automatic DNS verified"

    @logged_action
    def restore_dns(self):
        if not is_admin():
            return self.restart_as_admin("dns-restore")
        backups = [(key, value) for key, value in self.store.data["backups"].items() if key.startswith("dns:")]
        if not backups:
            print("No DNS restoration data has been saved.")
            return "no backup"
        for number, (key, backup) in enumerate(backups, start=1):
            if not isinstance(backup, dict):
                raise ValueError("Invalid saved DNS data.")
            print(f"{number}. {backup.get('name', key)}: {backup.get('mode')}, {backup.get('servers')}")
        choice = read_number("Saved configuration (0 to cancel): ", 0, len(backups))
        if not choice:
            return "cancelled"
        key, backup = backups[choice - 1]
        config = self.validate_config(backup)
        adapter = self.fresh_adapter(config["guid"])
        if not confirm(f"Restore saved IPv4 DNS for {adapter['name']}? Administrator access required."):
            return "cancelled"
        self.apply_config(adapter, config)
        self.store.forget(key)
        print("Original IPv4 DNS configuration restored and verified.")
        return "DNS restored and verified"
