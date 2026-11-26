"""Prepare reviewed Happ geo database updates without changing routing rules."""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

UPSTREAM = "https://raw.githubusercontent.com/hydraponique/roscomvpn-routing/main/HAPP/WHITELIST.JSON"
FIELDS = {"Geoipurl": "geoip", "Geositeurl": "geosite"}
PATHS = [Path("HAPP/WHITELIST.json"), Path("HAPP/DEFAULT.json")]
LIMIT = 100 * 1024 * 1024


def download(url, limit):
    request = urllib.request.Request(url, headers={"User-Agent": "kpopium-routing-update/1"})
    with urllib.request.urlopen(request, timeout=90) as response:
        if not response.geturl().startswith("https://"):
            raise ValueError("Non-HTTPS redirect")
        data = response.read(limit + 1)
    if not data or len(data) > limit:
        raise ValueError("Unexpected download size")
    return data


def version(url, kind):
    match = re.fullmatch(
        r"https://cdn\.jsdelivr\.net/gh/hydraponique/roscomvpn-"
        + kind + r"@(\d{12})/release/" + kind + r"\.dat", url
    )
    if not match:
        raise ValueError("Unexpected geo database URL: " + str(url))
    return match.group(1)


def varint(data, pos):
    value = 0
    for shift in range(0, 70, 7):
        if pos >= len(data):
            raise ValueError("Truncated protobuf")
        byte = data[pos]
        pos += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, pos
    raise ValueError("Invalid varint")


def fields(data):
    pos = 0
    while pos < len(data):
        tag, pos = varint(data, pos)
        number, wire = tag >> 3, tag & 7
        if number == 0:
            raise ValueError("Invalid protobuf field")
        if wire == 0:
            _, pos = varint(data, pos)
        elif wire == 2:
            size, pos = varint(data, pos)
            end = pos + size
            if end > len(data):
                raise ValueError("Truncated protobuf field")
            yield number, data[pos:end]
            pos = end
        elif wire in (1, 5):
            pos += 8 if wire == 1 else 4
            if pos > len(data):
                raise ValueError("Truncated fixed field")
        else:
            raise ValueError("Unsupported protobuf wire type")


def categories(data):
    # GeoIPList / GeoSiteList: repeated entry=1; entry code=1.
    result = set()
    for number, entry in fields(memoryview(data)):
        if number != 1:
            continue
        for n, value in fields(entry):
            if n == 1:
                result.add(bytes(value).decode("ascii").lower())
                break
    if not result:
        raise ValueError("No geo categories found")
    return result


def main():
    profiles = [json.loads(p.read_text(encoding="utf-8")) for p in PATHS]
    upstream = json.loads(download(UPSTREAM, 1024 * 1024))
    candidate = {}
    changed = False
    for field, kind in FIELDS.items():
        old = {p[field] for p in profiles}
        if len(old) != 1:
            raise ValueError("Happ profiles disagree about " + field)
        old_url = next(iter(old))
        old_tag = version(old_url, kind)
        new_url = upstream[field]
        new_tag = version(new_url, kind)
        if new_tag < old_tag:
            raise ValueError("Upstream version is older; refusing downgrade")
        candidate[field] = new_url
        changed |= new_url != old_url
        print(f"{kind}: {old_tag} -> {new_tag}")
    if not changed:
        print("No new versions.")
        return
    for field, kind in FIELDS.items():
        data = download(candidate[field], LIMIT)
        prefix = kind + ":"
        required = {
            rule[len(prefix):].split("@", 1)[0].lower()
            for profile in profiles
            for key in ("DirectSites", "DirectIp", "ProxySites", "ProxyIp", "BlockSites", "BlockIp")
            for rule in profile[key]
            if rule.startswith(prefix)
        }
        missing = required - categories(data)
        if missing:
            raise ValueError(f"Missing {kind} categories: {sorted(missing)}")
        print(f"{kind}: {len(data)} bytes; SHA256 {hashlib.sha256(data).hexdigest()}; categories OK")
    revision = str(max(int(time.time()), *(int(p["LastUpdated"]) + 1 for p in profiles)))
    for path, profile in zip(PATHS, profiles):
        profile.update(candidate)
        profile["LastUpdated"] = revision
        path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Prepared Happ profiles for review; INCY and all routing rules unchanged.")


if __name__ == "__main__":
    main()
