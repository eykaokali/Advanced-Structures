from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Dict, List, Tuple
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

T1, T2 = 0, 1
W1, W2, W3, W4 = 2, 3, 4, 5
STORES = list(range(6, 20)) 

NODE_NAMES = {
    T1: "Термінал 1",
    T2: "Термінал 2",
    W1: "Склад 1",
    W2: "Склад 2",
    W3: "Склад 3",
    W4: "Склад 4",
}
for i, idx in enumerate(STORES, start=1):
    NODE_NAMES[idx] = f"Магазин {i}"

BASE_EDGES: List[Tuple[int, int, int]] = [
    # Термінал → Склад
    (T1, W1, 25),
    (T1, W2, 20),
    (T1, W3, 15),
    (T2, W3, 15),
    (T2, W4, 30),
    (T2, W2, 10),
    # Склад 1 → Магазини 1..3
    (W1, STORES[0], 15),
    (W1, STORES[1], 10),
    (W1, STORES[2], 20),
    # Склад 2 → Магазини 4..6
    (W2, STORES[3], 15),
    (W2, STORES[4], 10),
    (W2, STORES[5], 25),
    # Склад 3 → Магазини 7..9
    (W3, STORES[6], 20),
    (W3, STORES[7], 15),
    (W3, STORES[8], 10),
    # Склад 4 → Магазини 10..14
    (W4, STORES[9], 20),
    (W4, STORES[10], 10),
    (W4, STORES[11], 15),
    (W4, STORES[12], 5),
    (W4, STORES[13], 10),
]

INF = 10**9

def bfs(
    capacity_matrix: List[List[int]],
    flow_matrix: List[List[int]],
    source: int,
    sink: int,
    parent: List[int],
) -> bool:
    """Пошук збільшуючого шляху (BFS) у залишковій мережі."""
    n = len(capacity_matrix)
    visited = [False] * n
    queue = deque([source])
    visited[source] = True
    parent[:] = [-1] * n

    while queue:
        u = queue.popleft()
        for v in range(n):
            residual = capacity_matrix[u][v] - flow_matrix[u][v]
            if not visited[v] and residual > 0:
                parent[v] = u
                visited[v] = True
                if v == sink:
                    return True
                queue.append(v)
    return False

def edmonds_karp(
    capacity_matrix: List[List[int]],
    source: int,
    sink: int,
) -> Tuple[int, List[List[int]]]:

    n = len(capacity_matrix)
    flow_matrix = [[0] * n for _ in range(n)]
    parent = [-1] * n
    max_flow = 0

    while bfs(capacity_matrix, flow_matrix, source, sink, parent):
        path_flow = INF
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, capacity_matrix[u][v] - flow_matrix[u][v])
            v = u

        v = sink
        while v != source:
            u = parent[v]
            flow_matrix[u][v] += path_flow
            flow_matrix[v][u] -= path_flow
            v = u

        max_flow += path_flow

    return max_flow, flow_matrix

def empty_matrix(n: int) -> List[List[int]]:
    return [[0] * n for _ in range(n)]

def build_base_network() -> Tuple[List[List[int]], int, int, Dict[str, int]]:

    n_log = 20
    source = n_log      # 20
    sink = n_log + 1    # 21
    n = n_log + 2
    cap = empty_matrix(n)

    for u, v, c in BASE_EDGES:
        cap[u][v] = c

    # SUPER_SOURCE → термінали (ємність = сума вихідних ребер термінала)
    cap[source][T1] = sum(c for u, v, c in BASE_EDGES if u == T1)
    cap[source][T2] = sum(c for u, v, c in BASE_EDGES if u == T2)

    # магазини → SUPER_SINK
    for s in STORES:
        # ємність = сума вхідних ребер магазину
        cap[s][sink] = sum(c for u, v, c in BASE_EDGES if v == s)

    meta = {"n_log": n_log, "W1": W1, "split": False}
    return cap, source, sink, meta

def build_variant6_network() -> Tuple[List[List[int]], int, int, Dict[str, int]]:

    W1_IN = 2
    W1_OUT = 20
    n_log_ext = 21
    source = 21
    sink = 22
    n = 23
    cap = empty_matrix(n)

    WAREHOUSE_OUT = {W1: W1_OUT, W2: W2, W3: W3, W4: W4}
    WAREHOUSE_IN = {W1: W1_IN, W2: W2, W3: W3, W4: W4}

    for u, v, c in BASE_EDGES:
        if u in (T1, T2) and v in (W1, W2, W3, W4):
            # термінал → вхід складу
            cap[u][WAREHOUSE_IN[v]] = c
        elif u in (W1, W2, W3, W4) and v in STORES:
            # вихід складу → магазин
            cap[WAREHOUSE_OUT[u]][v] = c
        else:
            cap[u][v] = c

    cap[W1_IN][W1_OUT] = 20

    cap[source][T1] = sum(c for u, v, c in BASE_EDGES if u == T1)
    cap[source][T2] = sum(c for u, v, c in BASE_EDGES if u == T2)
    for s in STORES:
        cap[s][sink] = sum(c for u, v, c in BASE_EDGES if v == s)

    meta = {
        "n_log": n_log_ext,
        "W1_IN": W1_IN,
        "W1_OUT": W1_OUT,
        "split": True,
        "WAREHOUSE_IN": WAREHOUSE_IN,
        "WAREHOUSE_OUT": WAREHOUSE_OUT,
    }
    return cap, source, sink, meta

def store_inflows(flow: List[List[int]], meta: Dict) -> Dict[int, int]:
    """Фактичний потік у кожен магазин."""
    result = {}
    if meta.get("split"):
        w_out = meta["WAREHOUSE_OUT"]
        for s in STORES:
            total = 0
            for w in (W1, W2, W3, W4):
                total += max(0, flow[w_out[w]][s])
            result[s] = total
    else:
        for s in STORES:
            total = 0
            for w in (W1, W2, W3, W4):
                total += max(0, flow[w][s])
            result[s] = total
    return result


def terminal_store_table(
    flow: List[List[int]],
    meta: Dict,
) -> List[Tuple[str, str, int]]:

    rows: List[Tuple[str, str, int]] = []

    if meta.get("split"):
        w_in = meta["WAREHOUSE_IN"]
        w_out = meta["WAREHOUSE_OUT"]
    else:
        w_in = {W1: W1, W2: W2, W3: W3, W4: W4}
        w_out = w_in

    # для кожного складу: вхід від T1/T2 і вихід у магазини
    for w, stores_of_w in [
        (W1, STORES[0:3]),
        (W2, STORES[3:6]),
        (W3, STORES[6:9]),
        (W4, STORES[9:14]),
    ]:
        wi = w_in[w]
        wo = w_out[w]
        in_t1 = max(0, flow[T1][wi])
        in_t2 = max(0, flow[T2][wi])
        in_total = in_t1 + in_t2

        for s in stores_of_w:
            f_store = max(0, flow[wo][s])
            if f_store == 0 or in_total == 0:
                f1 = 0
                f2 = 0
            else:
                # пропорційний розподіл (цілі одиниці з округленням залишку)
                f1 = int(round(f_store * in_t1 / in_total))
                f2 = f_store - f1
            rows.append((NODE_NAMES[T1], NODE_NAMES[s], f1))
            rows.append((NODE_NAMES[T2], NODE_NAMES[s], f2))

    return rows

def bottlenecks(capacity: List[List[int]], flow: List[List[int]], edges: List[Tuple[int, int, int]]) -> List[Tuple[str, str, int, int]]:
    """Ребра, завантажені на 100% (вузькі місця)."""
    result = []
    for u, v, c in edges:
        f = max(0, flow[u][v]) if u < len(flow) and v < len(flow[u]) else 0
        if c > 0 and f >= c:
            result.append((NODE_NAMES.get(u, str(u)), NODE_NAMES.get(v, str(v)), f, c))
    return result


def print_separator(title: str = "") -> None:
    print("=" * 70)
    if title:
        print(title)
        print("=" * 70)


def run_scenario(name: str, build_fn) -> Dict:
    cap, source, sink, meta = build_fn()
    max_flow, flow = edmonds_karp(cap, source, sink)
    stores = store_inflows(flow, meta)
    table = terminal_store_table(flow, meta)

    print_separator(name)
    print(f"Максимальний потік: {max_flow}")
    print()
    print(f"{'Термінал':<14} {'Магазин':<14} {'Фактичний потік':>16}")
    print("-" * 48)
    for term, shop, f in table:
        if f > 0:
            print(f"{term:<14} {shop:<14} {f:>16}")

    print()
    print("Потік у магазини:")
    for s in STORES:
        print(f"  {NODE_NAMES[s]}: {stores[s]}")

    # вузькі місця на базових ребрах (для варіанту 6 — з урахуванням розщеплення)
    print()
    if meta.get("split"):
        w_in = meta["WAREHOUSE_IN"]
        w_out = meta["WAREHOUSE_OUT"]
        check_edges = []
        for u, v, c in BASE_EDGES:
            if u in (T1, T2):
                check_edges.append((u, w_in[v], c))
            else:
                check_edges.append((w_out[u], v, c))
        # саме обмеження Складу 1
        check_edges.append((meta["W1_IN"], meta["W1_OUT"], 20))
        bn = []
        for u, v, c in check_edges:
            f = max(0, flow[u][v])
            if f >= c > 0:
                if u == meta["W1_IN"] and v == meta["W1_OUT"]:
                    nu, nv = "Склад 1 (in)", "Склад 1 (out)"
                else:
                    nu = NODE_NAMES.get(
                        u,
                        "Склад 1 (out)" if u == meta["W1_OUT"] else str(u),
                    )
                    nv = NODE_NAMES.get(
                        v,
                        "Склад 1 (out)" if v == meta["W1_OUT"] else str(v),
                    )
                bn.append((nu, nv, f, c))
    else:
        bn = bottlenecks(cap, flow, BASE_EDGES)

    print("Вузькі місця (потік = пропускна здатність):")
    if not bn:
        print("  (немає)")
    for a, b, f, c in bn:
        print(f"  {a} → {b}: {f}/{c}")

    return {
        "max_flow": max_flow,
        "flow": flow,
        "stores": stores,
        "table": table,
        "meta": meta,
        "bottlenecks": bn,
    }

def analyze_variant6(base: Dict, var6: Dict) -> None:
    print_separator("Порівняння: база vs варіант 6")
    print(f"Базовий макс. потік:     {base['max_flow']}")
    print(f"Варіант 6 макс. потік:   {var6['max_flow']}")
    print(f"Зменшення потоку:        {base['max_flow'] - var6['max_flow']}")
    print()
    print("Порівняння поставок у магазини (база → варіант 6):")
    for s in STORES:
        b = base["stores"][s]
        v = var6["stores"][s]
        print(f"  {NODE_NAMES[s]}: {b} → {v}")


def main() -> None:
    print_separator("| Завдання 1 | Max Flow | Варіант 6")
    base = run_scenario("БАЗОВА МЕРЕЖА (без обмеження Складу 1)", build_base_network)
    print()
    var6 = run_scenario(
        "ВАРІАНТ 6 (Склад 1: сумарний вихід ≤ 20)",
        build_variant6_network,
    )
    print()
    analyze_variant6(base, var6)
    print()
    print_separator("Готово")


if __name__ == "__main__":
    main()
