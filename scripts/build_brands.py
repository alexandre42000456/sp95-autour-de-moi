#!/usr/bin/env python3
"""Génère brands.json : identifiant de station (flux « Prix des carburants ») -> enseigne.

Le flux officiel ne contient pas l'enseigne. OpenStreetMap relie la plupart de ses
stations-service au même identifiant via l'étiquette `ref:FR:prix-carburants` et
renseigne leur marque (`brand`). Ce script interroge l'API Overpass et écrit un
fichier JSON compact servi avec le site.

Usage : python3 scripts/build_brands.py [chemin_sortie]   (défaut : brands.json)
Données © contributeurs OpenStreetMap, licence ODbL.
"""
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

ENDPOINTS = [
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]
QUERY = '[out:json][timeout:300];nwr["amenity"="fuel"]["ref:FR:prix-carburants"];out tags;'
USER_AGENT = "carburants-autour-de-moi/1.0 (brands.json builder)"
GENERIC = re.compile(r"^(station[- ]?service|station|carburants?|fuel|gas station)$", re.I)


def fetch():
    body = urllib.parse.urlencode({"data": QUERY}).encode()
    last = None
    for url in ENDPOINTS:
        for attempt in range(2):
            try:
                req = urllib.request.Request(url, data=body, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=400) as r:
                    return json.load(r)
            except Exception as e:  # réseau, 429, 504…
                last = e
                print(f"{url} (essai {attempt + 1}) : {e}", file=sys.stderr)
                time.sleep(20)
    raise SystemExit(f"Overpass indisponible : {last}")


# Regroupement des variantes d'une même enseigne sous le nom du groupe
# (comparaison sans accents ni casse ; premier motif qui correspond).
GROUPS = [
    (r"\btotal", "TotalEnergies"),
    (r"\bleclerc\b", "E.Leclerc"),
    (r"\bcarrefour\b", "Carrefour"),
    (r"intermarche|mousquetaires", "Intermarché"),
    (r"^(la )?station u$|^(super|hyper) u$|^u( express)?$|systeme u|^utile$", "Système U"),
    (r"\besso\b", "Esso"),
    (r"\bavia\b", "Avia"),
    (r"\bauchan\b", "Auchan"),
    (r"^elan$", "Elan"),
    (r"\beni\b|\bagip\b", "Eni"),
    (r"^bp\b", "BP"),
    (r"^shell\b", "Shell"),
    (r"^q8\b", "Q8"),
    (r"\bcora\b", "Cora"),
    (r"\bmatch\b", "Match"),
    (r"^as ?24$", "AS 24"),
    (r"^aire[- ]c$", "Aire C"),
    (r"^dyneff\b", "Dyneff"),
    (r"^independent$|^independant$", "Indépendant"),
]
GROUPS = [(re.compile(p), n) for p, n in GROUPS]


def fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def label(tags):
    for k in ("brand", "name", "operator"):
        v = (tags.get(k) or "").strip()
        if v and not GENERIC.match(v):
            f = fold(v)
            for rx, group in GROUPS:
                if rx.search(f):
                    return group
            return v
    return ""


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "brands.json"
    data = fetch()
    brands = {}
    for e in data.get("elements", []):
        tags = e.get("tags", {})
        name = label(tags)
        if not name:
            continue
        for ref in tags.get("ref:FR:prix-carburants", "").split(";"):
            ref = ref.strip()
            if ref.isdigit():
                brands[ref] = name
    if len(brands) < 5000:  # garde-fou : ne pas écraser un bon fichier par une réponse tronquée
        raise SystemExit(f"Résultat suspect ({len(brands)} stations), fichier non modifié.")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(brands.items())), f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(brands)} enseignes écrites dans {out}")


if __name__ == "__main__":
    main()
