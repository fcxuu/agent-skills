#!/usr/bin/env python3
"""Pure-stdlib static validator for JSON Canvas 1.0 (.canvas) files.

Checks JSON syntax, unique IDs across nodes and edges, required type-specific fields,
valid edge endpoints and sides, and bounding-box overlaps among non-group nodes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VALID_NODE_TYPES = {"text", "file", "link", "group"}
VALID_SIDES = {"top", "right", "bottom", "left"}
VALID_ENDS = {"none", "arrow"}


def _is_num(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_data(data: object) -> dict:
    issues: list[dict] = []

    def emit(severity: str, code: str, message: str) -> None:
        issues.append({"severity": severity, "code": code, "message": message})

    if not isinstance(data, dict):
        emit("error", "ROOT_NOT_OBJECT", "Top-level .canvas JSON must be an object")
        return _finalize(issues, 0, 0)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if not isinstance(nodes, list):
        emit("error", "NODES_NOT_LIST", "'nodes' must be a list")
        nodes = []
    if not isinstance(edges, list):
        emit("error", "EDGES_NOT_LIST", "'edges' must be a list")
        edges = []

    seen_ids: set[str] = set()
    node_ids: set[str] = set()
    boxes: list[tuple[str, float, float, float, float]] = []

    for idx, node in enumerate(nodes, 1):
        if not isinstance(node, dict):
            emit("error", "NODE_NOT_OBJECT", f"Node #{idx} must be an object")
            continue
        nid = node.get("id")
        if not isinstance(nid, str) or not nid.strip():
            emit("error", "NODE_MISSING_ID", f"Node #{idx} missing non-empty string 'id'")
        else:
            if nid in seen_ids:
                emit("error", "DUPLICATE_ID", f"Duplicate ID: {nid!r}")
            seen_ids.add(nid)
            node_ids.add(nid)

        ntype = node.get("type")
        if ntype not in VALID_NODE_TYPES:
            emit("error", "NODE_INVALID_TYPE", f"Node {nid or f'#{idx}'} has invalid type: {ntype!r}")
        else:
            if ntype == "text" and not isinstance(node.get("text"), str):
                emit("error", "TEXT_NODE_MISSING_TEXT", f"Text node {nid or f'#{idx}'} missing string 'text'")
            elif ntype == "file" and (not isinstance(node.get("file"), str) or not node["file"].strip()):
                emit("error", "FILE_NODE_MISSING_FILE", f"File node {nid or f'#{idx}'} missing non-empty string 'file'")
            elif ntype == "link" and (not isinstance(node.get("url"), str) or not node["url"].strip()):
                emit("error", "LINK_NODE_MISSING_URL", f"Link node {nid or f'#{idx}'} missing non-empty string 'url'")

        coords_ok = True
        for field in ("x", "y", "width", "height"):
            if not _is_num(node.get(field)):
                emit("error", "NODE_INVALID_COORD", f"Node {nid or f'#{idx}'} field '{field}' must be numeric")
                coords_ok = False
        if coords_ok:
            if node["width"] <= 0 or node["height"] <= 0:
                emit("error", "NODE_NONPOSITIVE_SIZE", f"Node {nid or f'#{idx}'} width and height must be > 0")
            elif ntype != "group" and isinstance(nid, str):
                x, y, w, h = float(node["x"]), float(node["y"]), float(node["width"]), float(node["height"])
                boxes.append((nid, x, y, x + w, y + h))

    # Pairwise overlap check for non-group nodes
    for i in range(len(boxes)):
        id_a, ax1, ay1, ax2, ay2 = boxes[i]
        for j in range(i + 1, len(boxes)):
            id_b, bx1, by1, bx2, by2 = boxes[j]
            ox = min(ax2, bx2) - max(ax1, bx1)
            oy = min(ay2, by2) - max(ay1, by1)
            if ox > 0 and oy > 0:
                emit(
                    "warning",
                    "NODE_OVERLAP",
                    f"Non-group nodes {id_a!r} and {id_b!r} overlap by {ox:.0f}x{oy:.0f} px",
                )

    for idx, edge in enumerate(edges, 1):
        if not isinstance(edge, dict):
            emit("error", "EDGE_NOT_OBJECT", f"Edge #{idx} must be an object")
            continue
        eid = edge.get("id")
        if not isinstance(eid, str) or not eid.strip():
            emit("error", "EDGE_MISSING_ID", f"Edge #{idx} missing non-empty string 'id'")
        else:
            if eid in seen_ids:
                emit("error", "DUPLICATE_ID", f"Duplicate ID: {eid!r}")
            seen_ids.add(eid)

        for ep in ("fromNode", "toNode"):
            target = edge.get(ep)
            if not isinstance(target, str) or target not in node_ids:
                emit("error", "EDGE_DANGLING_ENDPOINT", f"Edge {eid or f'#{idx}'} {ep}={target!r} does not match any node id")

        for side_field in ("fromSide", "toSide"):
            if side_field in edge and edge[side_field] not in VALID_SIDES:
                emit("error", "EDGE_INVALID_SIDE", f"Edge {eid or f'#{idx}'} has invalid {side_field}: {edge[side_field]!r}")

        for end_field in ("fromEnd", "toEnd"):
            if end_field in edge and edge[end_field] not in VALID_ENDS:
                emit("error", "EDGE_INVALID_END", f"Edge {eid or f'#{idx}'} has invalid {end_field}: {edge[end_field]!r}")

    return _finalize(issues, len(nodes), len(edges))


def _finalize(issues: list[dict], node_count: int, edge_count: int) -> dict:
    issues.sort(key=lambda x: (x["severity"], x["code"], x["message"]))
    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")
    return {
        "status": "PASS" if errors == 0 else "FAIL",
        "nodes": node_count,
        "edges": edge_count,
        "errors": errors,
        "warnings": warnings,
        "issues": issues,
        "not_checked": ["obsidian_live_rendering", "vault_file_existence"],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate an Obsidian JSON Canvas (.canvas) file.")
    ap.add_argument("path", help="Path to the .canvas file")
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    args = ap.parse_args(argv)

    p = Path(args.path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot parse {p} as UTF-8 JSON: {exc}", file=sys.stderr)
        return 2

    res = validate_data(data)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for item in res["issues"]:
            print(f"{item['severity'].upper()} {item['code']}: {item['message']}")
        print(f"{res['status']} (nodes={res['nodes']}, edges={res['edges']}, errors={res['errors']}, warnings={res['warnings']})")
    return 0 if res["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
