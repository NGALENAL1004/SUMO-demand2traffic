#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 Alix NGARI LENDOYE
# EIGSI La Rochelle
# La Rochelle Université — L3i
# SPDX-License-Identifier: GPL-3.0-only
"""
Event-driven TraCI controller — Strategy B: direct fallback taxi to activity.

Purpose
-------
This research controller detects public-transport passengers who are still
waiting at a bus stop although no suitable bus can serve the remaining trip.
It avoids reacting to a single missing timetable entry by requiring the
absence to persist for a configurable confirmation period.

High-level workflow
-------------------
1. Load the precomputed public-transport boarding index and the original SUMO
   population plans.
2. Observe passengers waiting at indexed bus stops.
3. Match each waiting passenger to the expected PT ride in the original plan.
4. Check the static timetable for a future vehicle serving the exact
   origin-stop, destination-stop, and line combination.
5. When the static index has no candidate, inspect active SUMO vehicles to
   detect a delayed bus that is still able to serve the passenger.
6. Mark the passenger as ``suspected_no_future_bus`` on the first failed check.
7. Confirm ``confirmed_stranded`` only when the failure persists for at least
   ``--stranded-confirmation-time`` seconds.
8. Apply Strategy B only after confirmation: replace the obsolete PT chain by
   a dedicated taxi ride directly to the next activity, while preserving the
   same SUMO person and the remainder of the original daily plan.
9. Monitor activity placeholders and release them at their original absolute
   end times so that subsequent stages continue in the correct order.
10. Write detailed runtime, plan, correction, and failure diagnostics.

Strategy B correction sequence
------------------------------
For a confirmed stranded passenger, the controller:
1. snapshots the remaining TraCI stages before any mutation;
2. identifies the destination activity following the blocked PT chain;
3. maps that pedestrian activity location to a passenger-accessible edge;
4. validates the final walking connection to the activity;
5. computes and validates the taxi route before changing the person plan;
6. creates a dedicated triggered taxi vehicle and route;
7. removes the obsolete remaining stages only after all read-only validation
   has succeeded;
8. appends the taxi stage, the final walking stage, the destination activity,
   and all later stages;
9. keeps the original ``person_id`` throughout the correction;
10. removes the person only when a post-mutation failure leaves the plan in an
    unsafe partial state, or when an explicit crash-guard rule requires it.

Operational notes
-----------------
- The fallback taxi has its own vehicle ID, while the SUMO person keeps the
  original ID.
- ``personNumber=1`` is not used to create an anonymous passenger.
- SUMO-GUI remains open at the end unless ``--nogui`` or
  ``--close-gui-on-end`` is used.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import pickle
import re
import sys
import time as pytime
import traceback
import xml.etree.ElementTree as ET
from bisect import bisect_left
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


# ============================================================
# Generic helpers
# ============================================================

def ln(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def first_line(lines_attr: str) -> str:
    if not lines_attr:
        return ""
    return str(lines_attr).split()[0]


def format_hms(seconds) -> str:
    if seconds in ("", None):
        return ""
    s = int(round(float(seconds)))
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"


def lane_to_edge(lane_id: str) -> str:
    return lane_id.rsplit("_", 1)[0] if "_" in lane_id else lane_id


def safe_float(x, default=0.1) -> float:
    try:
        if x in (None, ""):
            return float(default)
        return float(x)
    except Exception:
        return float(default)


def _fmt_elapsed(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    if seconds < 60:
        return f"{seconds:.1f}s"
    m = int(seconds // 60)
    s = seconds - 60 * m
    return f"{m}min{s:04.1f}s"


def progress(msg: str, t0: Optional[float] = None) -> float:
    """Print a clear timestamped progress message and return current wall time."""
    now = pytime.time()
    if t0 is None:
        print(f"[LOAD {pytime.strftime('%H:%M:%S')}] {msg}", flush=True)
    else:
        print(f"[OK   {pytime.strftime('%H:%M:%S')}] {msg} ({_fmt_elapsed(now - t0)})", flush=True)
    return now


def load_pickle(path: Path):
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path.resolve()}\n"
            "Run 01_build_pt_future_index.py first to generate pt_index_out/."
        )
    with path.open("rb") as f:
        return pickle.load(f)


def read_csv_auto(path: Path) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path.resolve()}")
    first = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    if ";" in first and "," not in first:
        dialect = csv.excel
        delimiter = ";"
    else:
        dialect = csv.excel
        delimiter = ","
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, dialect=dialect, delimiter=delimiter)
        return [dict(r) for r in reader]


def setup_sumo_tools():
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        raise RuntimeError(
            "SUMO_HOME is not defined. Check the SUMO_HOME environment variable."
        )
    tools_path = Path(sumo_home) / "tools"
    if str(tools_path) not in sys.path:
        sys.path.append(str(tools_path))
    from sumolib import checkBinary
    return checkBinary


def build_sumo_cmd(args):
    checkBinary = setup_sumo_tools()
    binary = args.sumo_binary or ("sumo" if args.nogui else "sumo-gui")
    cmd = [checkBinary(binary), "-c", str(args.sumocfg), "--no-step-log", "true"]

    # Production runs can generate tens of thousands of repetitive warnings
    # (notably deprecated walk departPos attributes). Suppressing warnings does
    # not suppress SUMO errors, which are written separately below.
    if getattr(args, "suppress_sumo_warnings", False):
        cmd += ["--no-warnings", "true"]
    sumo_error_log = getattr(args, "sumo_error_log", None)
    sumo_full_log = args.output_dir / "sumo_full.log"
    cmd += [
        "--log", str(sumo_full_log),
        "--log.timestamps", "true",
    ]
    if sumo_error_log:
        cmd += ["--error-log", str(sumo_error_log)]

    if not args.nogui:
        # Keep the GUI open by default by omitting --quit-on-end.
        cmd += ["--start"]
        if args.close_gui_on_end:
            cmd += ["--quit-on-end"]

    if args.begin is not None:
        cmd += ["--begin", str(args.begin)]
    if args.end is not None:
        cmd += ["--end", str(args.end)]

    # Use a fixed seed when requested so GUI/non-GUI and diagnostic runs remain
    # directly comparable. Without it, SUMO derives a seed from the system
    # clock and each execution becomes a different stochastic realization.
    if getattr(args, "seed", None) is not None:
        cmd += ["--seed", str(args.seed)]

    # A value of -1 disables teleportation. This is useful when testing whether
    # instability is caused by interactions between teleportation and dynamically
    # inserted fallback vehicles.
    if getattr(args, "time_to_teleport", None) is not None:
        cmd += ["--time-to-teleport", str(args.time_to_teleport)]

    return cmd


def resolve_path_maybe_relative(base_file: Path, candidate: str) -> Path:
    p = Path(candidate)
    if p.is_absolute():
        return p
    return (base_file.parent / p).resolve()


def extract_net_file_from_sumocfg(sumocfg: Path) -> Optional[Path]:
    """Best-effort extraction of <net-file value="..."> from SUMO config."""
    try:
        root = ET.parse(sumocfg).getroot()
    except Exception:
        return None
    for elem in root.iter():
        if ln(elem.tag) == "net-file":
            val = elem.get("value")
            if val:
                return resolve_path_maybe_relative(sumocfg, val)
    return None


# ============================================================
# PT index and population parsing
# ============================================================

class FuturePTIndex:
    def __init__(self, index_dir: Path):
        self.future_boardings = load_pickle(index_dir / "future_boardings.pkl")
        self.stop_info = load_pickle(index_dir / "stop_info.pkl")
        self.times = {
            key: [float(r["boarding_time"]) for r in rows]
            for key, rows in self.future_boardings.items()
        }

    def stop_name(self, stop_id: str) -> str:
        return self.stop_info.get(stop_id, {}).get("name", "")

    def watched_from_stops(self) -> set:
        return {key[0] for key in self.future_boardings.keys()}

    def next_boarding(self, from_stop: str, to_stop: str, line: str, current_time: float):
        key = (from_stop, to_stop, line)
        rows = self.future_boardings.get(key)
        if not rows:
            return None
        idx = bisect_left(self.times[key], float(current_time))
        if idx >= len(rows):
            return None
        return rows[idx]


def _stop_metadata(stop_elem: ET.Element) -> dict:
    lane = str(stop_elem.get("lane", "") or "")
    return {
        "ped_edge": lane_to_edge(lane),
        "ped_lane": lane,
        "ped_pos": safe_float(stop_elem.get("startPos"), safe_float(stop_elem.get("endPos"), 0.1)),
        "until": safe_float(stop_elem.get("until"), -1.0),
        "duration": safe_float(stop_elem.get("duration"), -1.0),
        "act_type": str(stop_elem.get("actType", "activity") or "activity"),
    }


def _target_activity_after_ride(children: List[ET.Element], ride_pos: int) -> Tuple[dict, List[dict]]:
    """Return the next activity and all activities from that point onward.

    The pedestrian destination is taken from the final walk of the PT chain when
    available, otherwise from the next stop lane itself.
    """
    last_to_edge = ""
    last_to_pos = 0.1
    target = None
    target_idx = None
    for j in range(ride_pos + 1, len(children)):
        ch = children[j]
        tag = ln(ch.tag)
        if tag == "walk" and ch.get("to"):
            last_to_edge = str(ch.get("to") or "")
            last_to_pos = safe_float(ch.get("arrivalPos"), 0.1)
        elif tag == "stop":
            target = _stop_metadata(ch)
            target_idx = j
            if last_to_edge:
                target["ped_edge"] = last_to_edge
                target["ped_pos"] = last_to_pos
            break
    if target is None or target_idx is None:
        return {}, []

    activities = []
    for ch in children[target_idx:]:
        if ln(ch.tag) == "stop":
            activities.append(_stop_metadata(ch))
    if activities:
        activities[0] = dict(target)
    return target, activities


def parse_population_rides(pop_path: Path):
    """Parse PT rides and the absolute schedule of subsequent activities."""
    if not pop_path.exists():
        raise FileNotFoundError(f"Population file not found: {pop_path.resolve()}")

    person_rides = defaultdict(list)
    for _event, person in ET.iterparse(pop_path, events=("end",)):
        if ln(person.tag) != "person":
            continue
        pid = person.get("id")
        children = list(person)
        if not pid:
            person.clear()
            continue

        for idx, elem in enumerate(children):
            if ln(elem.tag) != "ride":
                continue
            from_stop = elem.get("fromBusStop")
            to_stop = elem.get("busStop")
            line = first_line(elem.get("lines", ""))
            if from_stop and to_stop and line:
                target_activity, future_activities = _target_activity_after_ride(children, idx)
                person_rides[pid].append({
                    "ride_order": len(person_rides[pid]),
                    "from_stop": from_stop,
                    "to_stop": to_stop,
                    "line": line,
                    "fallback_dest_ped_edge": target_activity.get("ped_edge", ""),
                    "fallback_dest_ped_pos": target_activity.get("ped_pos", 0.1),
                    "target_activity_until": target_activity.get("until", -1.0),
                    "target_activity_type": target_activity.get("act_type", "activity"),
                    "future_activities": future_activities,
                })
        person.clear()
    return dict(person_rides)

def find_expected_ride(person_id, current_stop, person_rides, ride_pointer):
    rides = person_rides.get(person_id, [])
    start = ride_pointer.get(person_id, 0)

    for i in range(start, len(rides)):
        if rides[i]["from_stop"] == current_stop:
            return i, rides[i], "normal"

    for i, ride in enumerate(rides):
        if ride["from_stop"] == current_stop:
            return i, ride, "fallback_search"

    return None, None, "no_matching_ride"


# ============================================================
# SUMO network and facilities mapping
# ============================================================

class NetworkHelper:
    def __init__(self, net_path: Optional[Path]):
        setup_sumo_tools()
        import sumolib
        self.net_path = net_path
        self.net = None
        self._edge_cache = {}
        if net_path and net_path.exists():
            print("SUMO network         :", net_path.resolve())
            self.net = sumolib.net.readNet(str(net_path), withPedestrianConnections=True, withFoes=False, withPrograms=False)
        else:
            print("[WARN] No readable network file was found. Some network checks will be limited.")

    def edge(self, edge_id: str):
        if self.net is None:
            return None
        if edge_id in self._edge_cache:
            return self._edge_cache[edge_id]
        e = self.net.getEdge(edge_id)
        self._edge_cache[edge_id] = e
        return e

    def edge_allows(self, edge_id: str, vclass: str) -> bool:
        e = self.edge(edge_id)
        if e is None:
            return False
        try:
            return any(l.allows(vclass) for l in e.getLanes())
        except Exception:
            return False


class FacilitiesMapper:
    def __init__(self, path: Optional[Path]):
        self.path = path
        self.fac_modes: Dict[str, Dict[str, Tuple[str, str, float]]] = defaultdict(dict)
        self.ped_edge_index: Dict[str, List[dict]] = defaultdict(list)
        if path is None:
            print("[WARN] No facilities CSV file was provided.")
            return
        if not path.exists():
            print(f"[WARN] Facilities CSV file not found: {path.resolve()}")
            return
        rows = read_csv_auto(path)
        for r in rows:
            status = str(r.get("status", "mapped")).strip().lower()
            if status and status != "mapped":
                continue
            poi = str(r.get("poi_id", "")).strip()
            mode = str(r.get("mode", "")).strip()
            edge = str(r.get("edge_id", "")).strip()
            lane = str(r.get("lane_id", "")).strip()
            pos = safe_float(r.get("pos"), 0.1)
            if not poi or not mode or not edge or not lane:
                continue
            self.fac_modes[poi][mode] = (edge, lane, pos)

        for poi, modes in self.fac_modes.items():
            passenger = modes.get("passenger")
            pedestrian = modes.get("pedestrian")
            if not passenger or not pedestrian:
                continue
            ped_edge, ped_lane, ped_pos = pedestrian
            pass_edge, pass_lane, pass_pos = passenger
            self.ped_edge_index[ped_edge].append({
                "poi_id": poi,
                "ped_edge": ped_edge,
                "ped_lane": ped_lane,
                "ped_pos": ped_pos,
                "passenger_edge": pass_edge,
                "passenger_lane": pass_lane,
                "passenger_pos": pass_pos,
            })

        print("Facilities CSV       :", path.resolve())
        print("Mapped POIs          :", len(self.fac_modes))
        print("Ped-to-pass edge map :", len(self.ped_edge_index), "pedestrian edges")

    def passenger_for_ped_destination(self, ped_edge: str, ped_pos: float) -> Optional[dict]:
        cands = self.ped_edge_index.get(str(ped_edge), [])
        if not cands:
            return None
        ped_pos = safe_float(ped_pos, 0.1)
        best = min(cands, key=lambda x: abs(float(x["ped_pos"]) - ped_pos))
        return dict(best)


# ============================================================
# Live bus delayed detection
# ============================================================

def stop_id_from_next_stop(stop_data):
    """Extract the stop ID from a ``getNextStops`` tuple.

    TraCI normally returns ``(lane, endPos, stoppingPlaceID, stopFlags,
    duration, until)``. The stopping-place identifier is therefore item 2.
    """
    try:
        return stop_data[2]
    except Exception:
        return ""


def build_vehicle_ids_by_line(traci):
    out = defaultdict(list)
    for veh_id in traci.vehicle.getIDList():
        try:
            line = traci.vehicle.getLine(veh_id)
        except Exception:
            continue
        if line:
            out[line].append(veh_id)
    return dict(out)


def find_live_delayed_bus(traci, line, from_stop, to_stop, vehicle_ids_by_line):
    """Find an active delayed bus that can still serve the requested ride.

    A vehicle is accepted only when it uses the expected line, still has the
    boarding stop in its remaining stop sequence, and reaches the alighting
    stop later in that same sequence.
    """
    for veh_id in vehicle_ids_by_line.get(line, []):
        try:
            next_stops = traci.vehicle.getNextStops(veh_id)
        except Exception:
            continue

        stop_ids = [stop_id_from_next_stop(s) for s in next_stops]
        stop_ids = [s for s in stop_ids if s]
        if not stop_ids:
            continue

        try:
            i_from = stop_ids.index(from_stop)
        except ValueError:
            continue

        for j in range(i_from + 1, len(stop_ids)):
            if stop_ids[j] == to_stop:
                try:
                    speed = traci.vehicle.getSpeed(veh_id)
                except Exception:
                    speed = ""
                try:
                    waiting_time = traci.vehicle.getWaitingTime(veh_id)
                except Exception:
                    waiting_time = ""
                try:
                    road_id = traci.vehicle.getRoadID(veh_id)
                except Exception:
                    road_id = ""
                return {
                    "vehicle_id": veh_id,
                    "vehicle_speed": speed,
                    "vehicle_waiting_time": waiting_time,
                    "vehicle_road_id": road_id,
                    "from_index_live": i_from,
                    "to_index_live": j,
                    "live_next_stops_preview": " | ".join(
                        stop_ids[max(0, i_from - 2):min(len(stop_ids), i_from + 6)]
                    ),
                }
    return None


# ============================================================
# Car fallback correction
# ============================================================

def _parse_convert_road_result(res):
    """SUMO usually returns (edgeID, pos, laneIndex). Be tolerant."""
    if not res:
        return "", 0.1, 0
    if len(res) >= 3:
        return str(res[0]), safe_float(res[1], 0.1), int(res[2])
    if len(res) == 2:
        return str(res[0]), safe_float(res[1], 0.1), 0
    return str(res[0]), 0.1, 0


def passenger_edge_near_busstop(traci, net_helper: NetworkHelper, stop_id: str) -> Tuple[str, float, str, float, str]:
    """
    Returns (passenger_edge, passenger_pos, bus_lane, bus_pos, method).
    """
    lane = traci.busstop.getLaneID(stop_id)
    start = safe_float(traci.busstop.getStartPos(stop_id), 0.1)
    end = safe_float(traci.busstop.getEndPos(stop_id), start)
    pos = max(0.1, (start + end) / 2.0)
    edge = lane_to_edge(lane)

    if net_helper.edge_allows(edge, "passenger"):
        return edge, pos, lane, pos, "busstop_edge_allows_passenger"

    # Convert stop position to xy, then snap to nearest passenger edge.
    x, y = traci.simulation.convert2D(edge, pos, 0, False)
    road = traci.simulation.convertRoad(x, y, False, "passenger")
    near_edge, near_pos, _lane_idx = _parse_convert_road_result(road)
    if near_edge and net_helper.edge_allows(near_edge, "passenger"):
        return near_edge, near_pos, lane, pos, "nearest_passenger_from_busstop_xy"

    raise RuntimeError(f"no passenger edge near busStop={stop_id} lane={lane} edge={edge}")


def passenger_edge_for_destination(
    traci,
    net_helper: NetworkHelper,
    facilities: FacilitiesMapper,
    dest_ped_edge: str,
    dest_ped_pos: float,
) -> Tuple[str, float, str, str]:
    """
    Returns (dest_passenger_edge, dest_passenger_pos, poi_id_or_empty, method).
    """
    dest_ped_edge = str(dest_ped_edge or "")
    dest_ped_pos = safe_float(dest_ped_pos, 0.1)

    if dest_ped_edge:
        mapped = facilities.passenger_for_ped_destination(dest_ped_edge, dest_ped_pos)
        if mapped:
            p_edge = mapped["passenger_edge"]
            p_pos = safe_float(mapped["passenger_pos"], 0.1)
            if net_helper.edge_allows(p_edge, "passenger"):
                return p_edge, p_pos, mapped.get("poi_id", ""), "facilities_ped_to_passenger"

    if dest_ped_edge and net_helper.edge_allows(dest_ped_edge, "passenger"):
        return dest_ped_edge, dest_ped_pos, "", "destination_edge_already_passenger"

    if dest_ped_edge:
        x, y = traci.simulation.convert2D(dest_ped_edge, dest_ped_pos, 0, False)
        road = traci.simulation.convertRoad(x, y, False, "passenger")
        near_edge, near_pos, _lane_idx = _parse_convert_road_result(road)
        if near_edge and net_helper.edge_allows(near_edge, "passenger"):
            return near_edge, near_pos, "", "nearest_passenger_from_destination_xy"

    raise RuntimeError(f"no passenger destination found for ped_edge={dest_ped_edge} pos={dest_ped_pos}")


def unique_id(base: str, existing: set) -> str:
    if base not in existing:
        return base
    k = 1
    while f"{base}_{k}" in existing:
        k += 1
    return f"{base}_{k}"


def apply_basic_correction(traci, person_id, policy):
    if policy == "log_only":
        return {"action_result": "logged_only"}

    if policy == "remove_person":
        try:
            traci.person.remove(person_id)
            return {"action_result": "person_removed"}
        except Exception as e1:
            try:
                traci.person.removeStages(person_id)
                return {"action_result": "person_stages_removed"}
            except Exception as e2:
                return {"action_result": f"correction_failed: remove={e1}; removeStages={e2}"}

    return {"action_result": f"unknown_policy:{policy}"}


def stage_type(stage) -> int:
    try:
        return int(getattr(stage, "type"))
    except Exception:
        return -999


class PartialMutationError(RuntimeError):
    """A correction failed AFTER the person's TraCI state was already mutated.

    When this is raised, the person may be left with a partially rebuilt,
    incoherent plan inside SUMO. Such a person must be removed from the
    simulation regardless of --keep-person-on-correction-failure, because
    keeping a half-mutated person is exactly the kind of state that can make
    the native SUMO engine crash during a later simulationStep.
    """

    def __init__(self, message: str, original: Optional[BaseException] = None):
        super().__init__(message)
        self.original = original


def snapshot_person_stages(traci, person_id: str) -> List[Any]:
    """Copy remaining TraCI stages before touching the plan."""
    n = int(traci.person.getRemainingStages(person_id))
    out = []
    for i in range(n):
        out.append(traci.person.getStage(person_id, i))
    return out


def find_resume_stage_index_after_pt_chain(stages: List[Any]) -> int:
    """
    After the current blocked ride, skip the old PT chain until the next waiting
    stage, which corresponds to the destination activity. Re-append that waiting
    stage and everything after it.
    """
    for i in range(1, len(stages)):
        if stage_type(stages[i]) == 1:  # waiting/activity stop
            return i
    return len(stages)


def _stage_travel_time(stage, default=0.0) -> float:
    try:
        v = float(getattr(stage, "travelTime", default))
        if v < 0 or v > 10**8:
            return float(default)
        return v
    except Exception:
        return float(default)


def _stage_edges(stage) -> List[str]:
    try:
        return [str(e) for e in list(getattr(stage, "edges", []) or []) if str(e)]
    except Exception:
        return []


def _stage_arrival_pos(stage, default=0.1) -> float:
    try:
        v = float(getattr(stage, "arrivalPos", default))
        if v < -1e8:
            return float(default)
        return v
    except Exception:
        return float(default)


def _safe_stage_duration(stage=None, default=30.0) -> float:
    """SUMO 1.26 refuses negative walking-stage durations via TraCI.
    Use the routed travel time when available; otherwise a small positive fallback.
    """
    try:
        if stage is not None:
            tt = float(getattr(stage, "travelTime", default))
        else:
            tt = float(default)
        if tt < 0 or not math.isfinite(tt):
            return max(1.0, float(default))
        return max(1.0, tt)
    except Exception:
        return max(1.0, float(default))


def compute_walking_route_stages(traci, from_edge: str, to_edge: str, to_pos: float, t: float, args) -> Tuple[List[Any], float, str]:
    """Return walking stages and estimated walk time without modifying the person.

    Important safety rule for the controller: if SUMO cannot compute a pedestrian
    route, we DO NOT fall back to appending [from_edge, to_edge] manually. That
    direct fallback can create exactly the warnings we want to avoid:
    "No connection between edge ..." / "could not find sidewalk ...".
    Instead the correction is marked as failed before touching the person's plan.
    """
    if not from_edge or not to_edge or from_edge == to_edge:
        return [], 0.0, "same_edge_or_empty"

    last_error = ""
    try:
        stages = traci.simulation.findIntermodalRoute(
            from_edge,
            to_edge,
            modes="walk",
            depart=float(t),
            speed=float(args.fallback_walk_speed),
            arrivalPos=float(to_pos),
        )
        stages = [s for s in stages if stage_type(s) in (2, 4)]
        if stages:
            # Keep only safe stages with an actual edge list.
            stages = [s for s in stages if _stage_edges(s)]
            if stages:
                tt = sum(_safe_stage_duration(s, 30.0) for s in stages)
                return stages, tt, "findIntermodalRoute_walking"
            last_error = "intermodal route returned no usable walking edges"
        else:
            last_error = "findIntermodalRoute returned no walking stage"
    except Exception as e:
        last_error = str(e)

    return [], float("inf"), f"no_safe_walking_route:{last_error}"


def append_walking_solution(traci, person_id: str, from_edge: str, to_edge: str, to_pos: float, stages: List[Any], method: str, args):
    """Append precomputed walking stages to the person's plan.

    This function is intentionally strict. If no safe routed walking stage exists,
    it raises instead of inventing a direct walking stage that may be disconnected.
    """
    if not from_edge or not to_edge or from_edge == to_edge:
        return

    if not stages:
        raise RuntimeError(f"no safe walking route for correction {from_edge}->{to_edge} ({method})")

    for st in stages:
        edges = _stage_edges(st)
        if not edges:
            raise RuntimeError(f"walking stage without edges for correction {from_edge}->{to_edge}")
        # Ensure the final stage ends exactly where we want.
        arr = _stage_arrival_pos(st, to_pos)
        if edges[-1] == to_edge:
            arr = float(to_pos)
        traci.person.appendWalkingStage(
            person_id,
            edges,
            arr,
            _safe_stage_duration(st, 30.0),
            float(args.fallback_walk_speed),
            "",
        )


def append_resume_stage_safe(traci, person_id: str, stage, default_wait: float = 1.0):
    """Re-append a saved future stage, avoiding negative waiting durations.

    A blocked PT passenger may reach the activity after the original activity end
    time. SUMO then exposes the saved waiting/activity stage with a negative or
    invalid duration, and TraCI rejects appendStage with:
    "Duration for person ... must not be negative".

    For waiting stages, clamp the duration to a small positive value. For other
    stage types, keep the original stage.
    """
    if stage_type(stage) == 1:  # waiting/activity stop
        duration = _safe_stage_duration(stage, default_wait)
        description = str(getattr(stage, "description", "") or "")
        stop_id = str(getattr(stage, "destStop", "") or "")
        try:
            traci.person.appendWaitingStage(person_id, duration, description, stop_id)
        except TypeError:
            # Some SUMO versions expose a shorter signature.
            traci.person.appendWaitingStage(person_id, duration, description)
        return

    traci.person.appendStage(person_id, stage)


def _stage_signature_for_plan_preservation(stage) -> tuple:
    """Stable signature used to prove that future stages were not modified."""
    data = serialize_stage(stage)
    return (
        data.get("stage_type"),
        data.get("vType"),
        data.get("line"),
        data.get("intended"),
        data.get("destStop"),
        data.get("description"),
        data.get("edges"),
        data.get("arrivalPos"),
    )


def _finite_or(value, default):
    try:
        value = float(value)
        if math.isfinite(value) and value > -1e8:
            return value
    except Exception:
        pass
    return float(default)


ACTIVITY_PENDING_PREFIX = "fallback_activity_pending"
ACTIVITY_ACTIVE_PREFIX = "fallback_activity_active"


def ensure_fallback_taxi_type(traci, args) -> str:
    """Create a dedicated taxi vType dynamically when it is absent."""
    type_id = str(args.fallback_vtype)
    existing = set(map(str, traci.vehicletype.getIDList()))
    if type_id not in existing:
        base = "DEFAULT_VEHTYPE"
        if base not in existing:
            base = next(iter(existing))
        traci.vehicletype.copy(base, type_id)
    traci.vehicletype.setVehicleClass(type_id, "taxi")
    try:
        traci.vehicletype.setShapeClass(type_id, "taxi")
    except Exception:
        pass
    try:
        traci.vehicletype.setColor(type_id, tuple(args.fallback_color))
    except Exception:
        pass
    try:
        traci.vehicletype.setBoardingDuration(type_id, 1.0)
    except Exception:
        pass
    return type_id


def allow_taxi_on_pickup_lane(traci, lane_id: str) -> Tuple[List[str], bool]:
    """Ensure the taxi class can use the exact lane carrying the bus stop."""
    allowed = list(map(str, traci.lane.getAllowed(lane_id)))
    # Empty means every vehicle class is allowed already.
    if not allowed or "taxi" in allowed:
        return allowed, False
    new_allowed = list(dict.fromkeys(allowed + ["taxi"]))
    traci.lane.setAllowed(lane_id, new_allowed)
    return allowed, True


def lane_index_from_id(lane_id: str) -> int:
    try:
        return int(str(lane_id).rsplit("_", 1)[1])
    except Exception:
        return 0


def activity_marker(prefix: str, seq: int, activity: dict) -> str:
    return (
        f"{prefix}|seq={int(seq)}|act={activity.get('act_type', 'activity')}|"
        f"until={float(activity.get('until', -1.0))}|"
        f"duration={float(activity.get('duration', -1.0))}|"
        f"edge={activity.get('ped_edge', '')}|"
        f"pos={float(activity.get('ped_pos', 0.1))}"
    )


def parse_activity_marker(description: str) -> Optional[dict]:
    """Read an activity marker from the description returned by SUMO.

    ``appendWaitingStage`` stores the marker as the stage description, but
    ``person.getStage`` may expose it as ``waiting (<marker>)``.  The previous
    version expected the marker at character zero, so the pending activity was
    never converted to its real remaining duration.
    """
    desc = str(description or "").strip()

    # SUMO commonly wraps waiting-stage descriptions this way.  Strip all
    # wrapper levels to stay robust to descriptions such as
    # ``waiting (waiting (<marker>))``.
    while desc.startswith("waiting (") and desc.endswith(")"):
        desc = desc[len("waiting ("):-1].strip()

    # Defensive fallback: retain the marker even if SUMO adds another textual
    # prefix around it in a future version.
    marker_positions = [
        pos for pos in (
            desc.find(ACTIVITY_PENDING_PREFIX + "|"),
            desc.find(ACTIVITY_ACTIVE_PREFIX + "|"),
        ) if pos >= 0
    ]
    if not marker_positions:
        return None
    desc = desc[min(marker_positions):]
    parts = desc.split("|")
    out = {"prefix": parts[0]}
    for token in parts[1:]:
        if "=" in token:
            k, v = token.split("=", 1)
            out[k] = v
    try:
        out["seq"] = int(out.get("seq", 0))
        out["until"] = float(out.get("until", -1.0))
        out["duration"] = float(out.get("duration", -1.0))
        out["pos"] = float(out.get("pos", 0.1))
    except Exception:
        return None
    return out


def append_activity_placeholder(traci, person_id: str, seq: int, activity: dict, args):
    traci.person.appendWaitingStage(
        person_id,
        float(args.activity_placeholder_duration),
        activity_marker(ACTIVITY_PENDING_PREFIX, seq, activity),
        "",
    )


def validate_future_plan_alignment(future_stages: List[Any], future_activities: List[dict]):
    """Validate stage/activity coherence WITHOUT any TraCI call.

    Must be called BEFORE any state mutation. The historical version of this
    check ran *after* stages had already been appended via TraCI, which could
    leave the person with a half-rebuilt, incoherent plan inside SUMO when the
    mismatch was detected (a prime suspect for deferred native crashes during
    later simulationStep calls).
    """
    waiting_count = sum(1 for stage in future_stages if stage_type(stage) == 1)
    if waiting_count != len(future_activities):
        raise RuntimeError(
            f"activity alignment mismatch (pre-validated): "
            f"future_waiting_stages={waiting_count}, expected_activities={len(future_activities)}"
        )


def rebuild_future_plan_with_absolute_activities(
    traci,
    person_id: str,
    future_stages: List[Any],
    future_activities: List[dict],
    args,
):
    """Append saved movement stages and replace future waits by timed placeholders.

    Alignment MUST have been validated beforehand via
    ``validate_future_plan_alignment`` (no TraCI mutation happens here until
    coherence is guaranteed). The defensive re-check below should therefore
    never fire; it is kept as a last-resort invariant.
    """
    validate_future_plan_alignment(future_stages, future_activities)
    activity_cursor = 0
    for stage in future_stages:
        if stage_type(stage) == 1:
            append_activity_placeholder(
                traci, person_id, activity_cursor + 1, future_activities[activity_cursor], args
            )
            activity_cursor += 1
        else:
            traci.person.appendStage(person_id, stage)


def manage_current_activity_placeholder(
    traci,
    person_id: str,
    t: float,
    activity_runtime_state: dict,
) -> Optional[dict]:
    """Keep the activity placeholder on its correct edge and release it at its original end.

    The placeholder is NEVER replaced.  Replacing the current waiting stage can
    relocate the person to an edge belonging to another saved stage.  Instead:

    * when the placeholder first becomes current, record its real arrival time;
    * if the original activity end is already passed, remove it immediately;
    * otherwise leave it untouched on its pedestrian edge and remove it exactly
      when the original ``until`` is reached;
    * for duration-only activities, release at ``real_arrival + duration``.

    Removing stage 0 advances the same SUMO person to the next preserved stage.
    Every removal is returned as a structured event for the dedicated CSV log.
    """
    try:
        before_count = int(traci.person.getRemainingStages(person_id))
        if before_count < 1:
            return None
        stage = traci.person.getStage(person_id, 0)
    except Exception:
        return None

    if stage_type(stage) != 1:
        return None

    description = str(getattr(stage, "description", "") or "")
    meta = parse_activity_marker(description)
    if not meta or meta.get("prefix") != ACTIVITY_PENDING_PREFIX:
        return None

    seq = int(meta.get("seq", 0))
    key = (str(person_id), seq)
    state = activity_runtime_state.get(key)
    if state is None:
        state = {
            "first_active_time": float(t),
            "first_active_road": str(traci.person.getRoadID(person_id) or ""),
            "first_stage_description": description,
        }
        activity_runtime_state[key] = state

    first_active = float(state["first_active_time"])
    original_until = float(meta.get("until", -1.0))
    original_duration = float(meta.get("duration", -1.0))

    if original_until >= 0:
        release_time = original_until
        late_on_arrival = first_active >= original_until
    elif original_duration >= 0:
        release_time = first_active + original_duration
        late_on_arrival = False
    else:
        # No temporal information exists in the original XML.  Do not leave an
        # unbounded 48-hour placeholder in the simulation.
        release_time = first_active
        late_on_arrival = True

    if float(t) + 1e-9 < release_time:
        return None

    try:
        current_road = str(traci.person.getRoadID(person_id) or "")
    except Exception:
        current_road = ""
    try:
        current_pos = float(traci.person.getLanePosition(person_id))
    except Exception:
        current_pos = ""

    reason = (
        "late_arrival_after_original_until"
        if late_on_arrival
        else "original_activity_end_reached"
    )
    if original_until < 0 and original_duration < 0:
        reason = "activity_without_until_or_duration_removed_immediately"

    traci.person.removeStage(person_id, 0)
    try:
        after_count = int(traci.person.getRemainingStages(person_id))
    except Exception:
        after_count = ""

    activity_runtime_state.pop(key, None)
    return {
        "event": "activity_removed",
        "person_id": str(person_id),
        "activity_seq": seq,
        "activity_type": meta.get("act", "activity"),
        "activity_edge_expected": str(meta.get("edge", "") or ""),
        "activity_pos_expected": float(meta.get("pos", 0.1)),
        "activity_edge_actual_before_removal": current_road,
        "activity_pos_actual_before_removal": current_pos,
        "original_until": original_until,
        "original_duration": original_duration,
        "first_active_time": first_active,
        "removal_time": float(t),
        "time_spent_in_activity": max(0.0, float(t) - first_active),
        "arrival_lateness": (
            max(0.0, first_active - original_until)
            if original_until >= 0 else 0.0
        ),
        "removal_reason": reason,
        "activity_skipped": bool(late_on_arrival),
        "remaining_stages_before": before_count,
        "remaining_stages_after": after_count,
        "stage_description_before": description,
        "first_active_road": state.get("first_active_road", ""),
    }


def current_placeholder_release_time(
    traci,
    person_id: str,
    t: float,
    activity_runtime_state: dict,
) -> Optional[float]:
    """Return the next absolute release time for the current fallback activity.

    This helper is read-only with respect to the SUMO plan.  It lets the main
    loop schedule the next TraCI synchronization directly at the activity end
    rather than polling the person once per simulated second.
    """
    try:
        if int(traci.person.getRemainingStages(person_id)) < 1:
            return None
        stage = traci.person.getStage(person_id, 0)
    except Exception:
        return None

    if stage_type(stage) != 1:
        return None

    description = str(getattr(stage, "description", "") or "")
    meta = parse_activity_marker(description)
    if not meta or meta.get("prefix") != ACTIVITY_PENDING_PREFIX:
        return None

    seq = int(meta.get("seq", 0))
    key = (str(person_id), seq)
    state = activity_runtime_state.get(key)
    if state is None:
        try:
            road = str(traci.person.getRoadID(person_id) or "")
        except Exception:
            road = ""
        state = {
            "first_active_time": float(t),
            "first_active_road": road,
            "first_stage_description": description,
        }
        activity_runtime_state[key] = state

    original_until = float(meta.get("until", -1.0))
    original_duration = float(meta.get("duration", -1.0))
    if original_until >= 0:
        return float(original_until)
    if original_duration >= 0:
        return float(state["first_active_time"]) + original_duration
    return float(t)


def clamp_arrival_pos_on_edge(net_helper: NetworkHelper, edge_id: str, pos: float) -> Tuple[float, bool, float]:
    """Clamp an arrival position to a safe range on the destination edge."""
    original = safe_float(pos, 0.1)
    edge = net_helper.edge(str(edge_id))
    if edge is None:
        return max(0.1, original), False, -1.0
    lengths = []
    try:
        for lane in edge.getLanes():
            try:
                if lane.allows("taxi") or lane.allows("passenger"):
                    lengths.append(float(lane.getLength()))
            except Exception:
                continue
    except Exception:
        lengths = []
    if not lengths:
        return max(0.1, original), False, -1.0
    edge_limit = max(0.1, min(lengths) - 0.1)
    clamped = min(max(0.1, original), edge_limit)
    return clamped, abs(clamped - original) > 1e-9, edge_limit


def apply_car_fallback_keep_person(
    traci,
    person_id: str,
    ride: dict,
    current_stop: str,
    t: float,
    args,
    net_helper: NetworkHelper,
    facilities: FacilitiesMapper,
) -> dict:
    """Replace one blocked PT chain with a direct taxi to the next activity.

    The function is deliberately divided into two phases.

    Read-only validation phase
    --------------------------
    1. Snapshot every remaining stage of the person.
    2. Confirm that stage 0 is the blocked PT driving stage.
    3. Locate the next waiting stage, which represents the destination activity.
    4. Read the destination pedestrian edge and all later activity metadata from
       the original population plan.
    5. Map the pedestrian activity location to a taxi-accessible destination edge.
    6. Compute the final pedestrian route from the taxi drop-off edge to the
       activity edge.
    7. Identify the exact bus-stop lane and the passenger's current position.
    8. Compute the taxi route and reject empty or pathological routes.
    9. Verify that saved waiting stages align with the future activities that
       will replace them.

    Mutating phase
    --------------
    10. Create a unique SUMO route and a triggered one-seat fallback taxi.
    11. Remove the person's obsolete stages.
    12. Append the direct taxi stage and the validated final walking stages.
    13. Append a timed placeholder for the destination activity.
    14. Re-append all later movement stages and replace later activity waits by
        placeholders carrying their original timing metadata.

    Safety guarantees
    -----------------
    No person-plan mutation occurs before every route and alignment check has
    succeeded. If an exception occurs after ``removeStages``, the function raises
    ``PartialMutationError`` so the caller removes the unsafe partially rebuilt
    person rather than leaving inconsistent native SUMO state.
    """
    before = snapshot_person_stages(traci, person_id)
    if not before or stage_type(before[0]) != 3:
        raise RuntimeError("current person stage is not the blocked PT driving stage")

    target_idx = find_resume_stage_index_after_pt_chain(before)
    if target_idx >= len(before) or stage_type(before[target_idx]) != 1:
        raise RuntimeError("could not identify the target activity after the blocked PT chain")

    future_after_target = before[target_idx + 1:]
    activities = list(ride.get("future_activities", []) or [])
    if not activities:
        raise RuntimeError("original XML contains no target activity after this ride")
    target_activity = dict(activities[0])
    future_activities = [dict(x) for x in activities[1:]]

    dest_ped_edge = str(target_activity.get("ped_edge", "") or "")
    dest_ped_pos = safe_float(target_activity.get("ped_pos"), 0.1)
    if not dest_ped_edge:
        raise RuntimeError("target activity has no pedestrian edge")

    dest_edge, dest_pos, dest_poi, dest_method = passenger_edge_for_destination(
        traci, net_helper, facilities, dest_ped_edge, dest_ped_pos
    )
    dest_pos_original = float(dest_pos)
    dest_pos, dest_pos_clamped, dest_edge_limit = clamp_arrival_pos_on_edge(
        net_helper, dest_edge, dest_pos
    )
    if dest_pos_clamped:
        dest_method = f"{dest_method}|arrival_pos_clamped"

    walk_stages, walk_time, walk_method = compute_walking_route_stages(
        traci, dest_edge, dest_ped_edge, dest_ped_pos, t, args
    )
    if dest_edge != dest_ped_edge and not walk_stages:
        raise RuntimeError(
            f"no safe final walk from passenger edge to activity: {dest_edge}->{dest_ped_edge} ({walk_method})"
        )

    bus_lane = str(traci.busstop.getLaneID(current_stop))
    bus_edge = lane_to_edge(bus_lane)
    person_pos = safe_float(traci.person.getLanePosition(person_id), 0.1)
    try:
        lane_len = float(traci.lane.getLength(bus_lane))
        person_pos = min(max(0.1, person_pos), max(0.1, lane_len - 0.1))
    except Exception:
        person_pos = max(0.1, person_pos)

    taxi_type = ensure_fallback_taxi_type(traci, args)
    original_allowed, permission_changed = allow_taxi_on_pickup_lane(traci, bus_lane)

    try:
        route_stage = traci.simulation.findRoute(
            bus_edge,
            dest_edge,
            taxi_type,
            float(t),
            0,
            float(person_pos),
            float(dest_pos),
        )
    except TypeError:
        # Compatibility with older SUMO/TraCI versions whose findRoute does
        # not yet expose departPos and arrivalPos.
        route_stage = traci.simulation.findRoute(
            bus_edge, dest_edge, taxi_type, float(t)
        )
    route_edges = list(getattr(route_stage, "edges", []) or [])
    if not route_edges:
        raise RuntimeError(f"no taxi route from bus stop edge {bus_edge} to {dest_edge}")

    # Guard against pathological routes (massive detours across the whole
    # network). Besides being unrealistic for a taxi, such routes have been
    # correlated with vehicle teleportation and instability in this project.
    max_route_edges = int(getattr(args, "max_taxi_route_edges", 0) or 0)
    if max_route_edges > 0 and len(route_edges) > max_route_edges:
        raise RuntimeError(
            f"taxi route rejected as pathological: {len(route_edges)} edges "
            f"(limit={max_route_edges}) from {bus_edge} to {dest_edge}"
        )

    route_tt = _finite_or(getattr(route_stage, "travelTime", -1), 1.0)
    route_cost = _finite_or(getattr(route_stage, "cost", route_tt), route_tt)
    route_length = _finite_or(getattr(route_stage, "length", 0.0), 0.0)

    # === END OF READ-ONLY VALIDATION PHASE ===
    # Everything above this point is safe to fail: no TraCI mutation has
    # happened yet, so the person's state inside SUMO is untouched.
    # Validate the ENTIRE correction plan (including the future plan rebuild
    # coherence) before the first mutating call below.
    validate_future_plan_alignment(future_after_target, future_activities)

    existing_routes = set(map(str, traci.route.getIDList()))
    try:
        existing_vehicles = set(map(str, traci.vehicle.getLoadedIDList()))
    except Exception:
        existing_vehicles = set(map(str, traci.vehicle.getIDList()))
    stamp = int(round(float(t)))
    clean_pid = re.sub(r"[^A-Za-z0-9_.:-]", "_", str(person_id))
    route_id = unique_id(f"fallback_route_{clean_pid}_{stamp}", existing_routes)
    veh_id = unique_id(f"fallback_taxi_{clean_pid}_{stamp}", existing_vehicles)
    line_id = f"fallback_taxi_line_{clean_pid}_{stamp}"

    traci.route.add(route_id, route_edges)
    vehicle_added = False
    person_mutation_started = False
    try:
        traci.vehicle.add(
            vehID=veh_id,
            routeID=route_id,
            typeID=taxi_type,
            depart="triggered",
            departLane=str(lane_index_from_id(bus_lane)),
            departPos=str(person_pos),
            departSpeed="0",
            arrivalPos=str(max(0.1, float(dest_pos))),
            line=line_id,
            personCapacity=1,
            personNumber=0,
        )
        vehicle_added = True
        try:
            traci.vehicle.setColor(veh_id, tuple(args.fallback_color))
        except Exception:
            pass

        # === START OF PERSON MUTATION PHASE ===
        # From removeStages onward, any failure leaves the person in a
        # partially rebuilt state. Such failures are wrapped in
        # PartialMutationError so the caller knows the person MUST be removed.
        person_mutation_started = True
        traci.person.removeStages(person_id)

        stage_cls = type(before[0])
        taxi_stage = stage_cls(
            type=3,
            vType=taxi_type,
            line=f"{veh_id} {line_id}",
            destStop="",
            edges=[bus_edge, dest_edge],
            travelTime=route_tt,
            cost=route_cost,
            length=route_length,
            intended=veh_id,
            depart=float(t),
            departPos=float(person_pos),
            arrivalPos=float(dest_pos),
            description=(
                f"fallback taxi direct to activity {target_activity.get('act_type', 'activity')} "
                f"on passenger edge {dest_edge}"
            ),
        )
        traci.person.appendStage(person_id, taxi_stage)
        append_walking_solution(
            traci,
            person_id,
            dest_edge,
            dest_ped_edge,
            dest_ped_pos,
            walk_stages,
            walk_method,
            args,
        )
        append_activity_placeholder(traci, person_id, 0, target_activity, args)
        rebuild_future_plan_with_absolute_activities(
            traci,
            person_id,
            future_after_target,
            future_activities,
            args,
        )

    except Exception as exc:
        if vehicle_added:
            try:
                traci.vehicle.remove(veh_id)
            except Exception:
                pass
        if person_mutation_started and not isinstance(exc, PartialMutationError):
            # The person's plan was already (partially) destroyed/rebuilt.
            # Escalate so the caller removes the person unconditionally
            # instead of leaving a half-mutated person inside SUMO.
            raise PartialMutationError(
                f"correction failed after person state mutation started: {exc}",
                original=exc,
            ) from exc
        raise

    return {
        "fallback_person_id": str(person_id),
        "fallback_vehicle_id": veh_id,
        "fallback_route_id": route_id,
        "fallback_line": line_id,
        "fallback_depart_edge": bus_edge,
        "fallback_depart_pos": person_pos,
        "fallback_depart_lane": bus_lane,
        "fallback_depart_method": "exact_current_busstop_lane_triggered",
        "fallback_dest_ped_edge": dest_ped_edge,
        "fallback_dest_ped_pos": dest_ped_pos,
        "fallback_dest_passenger_edge": dest_edge,
        "fallback_dest_passenger_pos": dest_pos,
        "fallback_dest_passenger_pos_original": dest_pos_original,
        "fallback_dest_position_clamped": dest_pos_clamped,
        "fallback_dest_edge_safe_limit": dest_edge_limit,
        "fallback_dest_poi_id": dest_poi,
        "fallback_dest_method": dest_method,
        "fallback_route_edges_count": len(route_edges),
        "fallback_route_travel_time": route_tt,
        "fallback_walk_to_car_time": 0.0,
        "fallback_walk_to_activity_time": walk_time,
        "fallback_resume_stage_index": target_idx,
        "fallback_reappended_stage_count": len(future_after_target),
        "fallback_preserved_future_stage_count": len(future_after_target),
        "fallback_future_plan_verified_unchanged": False,
        "fallback_departure_mode": "triggered_by_exact_person_boarding_at_busstop",
        "pickup_lane_original_allowed": " ".join(original_allowed),
        "pickup_lane_permission_changed": permission_changed,
        "target_activity_type": target_activity.get("act_type", "activity"),
        "target_activity_until": target_activity.get("until", -1.0),
        "action_result": "strategy_b_direct_activity_placeholder_release_plan_rebuilt",
    }


# ============================================================
# Runtime monitoring, diagnostics, and event-driven controller loop
# ============================================================

STAGE_TYPE_NAMES = {
    1: "waiting_or_activity",
    2: "walking",
    3: "driving",
    4: "access",
    5: "personTrip",
}


def stage_attr(stage, name, default=""):
    try:
        value = getattr(stage, name, default)
        if value is None:
            return default
        return value
    except Exception:
        return default


def serialize_stage(stage) -> dict:
    stype = stage_type(stage)
    edges = _stage_edges(stage)
    return {
        "stage_type": stype,
        "stage_type_name": STAGE_TYPE_NAMES.get(stype, f"unknown_{stype}"),
        "vType": str(stage_attr(stage, "vType", "") or ""),
        "line": str(stage_attr(stage, "line", "") or ""),
        "intended": str(stage_attr(stage, "intended", "") or ""),
        "destStop": str(stage_attr(stage, "destStop", "") or ""),
        "description": str(stage_attr(stage, "description", "") or ""),
        "edges": " | ".join(edges),
        "edge_count": len(edges),
        "travelTime": stage_attr(stage, "travelTime", ""),
        "cost": stage_attr(stage, "cost", ""),
        "length": stage_attr(stage, "length", ""),
        "depart": stage_attr(stage, "depart", ""),
        "departPos": stage_attr(stage, "departPos", ""),
        "arrivalPos": stage_attr(stage, "arrivalPos", ""),
    }


def extract_original_person_plans(population_path: Path, focus_ids: set, output_path: Path):
    root = ET.Element("routes")
    found = set()
    for _event, elem in ET.iterparse(population_path, events=("end",)):
        if ln(elem.tag) != "person":
            continue
        pid = str(elem.get("id", ""))
        if pid in focus_ids:
            root.append(ET.fromstring(ET.tostring(elem, encoding="unicode")))
            found.add(pid)
        elem.clear()
        if found == focus_ids:
            break
    ET.ElementTree(root).write(output_path, encoding="utf-8", xml_declaration=True)
    missing = sorted(focus_ids - found)
    if missing:
        print("[WARN] Original plans not found for:", ", ".join(missing), flush=True)


def safe_person_ids(traci) -> set:
    try:
        return set(map(str, traci.person.getIDList()))
    except Exception:
        return set()


def safe_vehicle_person_ids(traci, vehicle_id: str) -> str:
    """Return persons currently inside a vehicle without querying a removed vehicle.

    SUMO removes a vehicle from TraCI as soon as it reaches the end of its
    route. Querying getPersonIDList() afterward produces the noisy message
    "Vehicle ... is not known", even when the exception is caught in Python.
    """
    if not vehicle_id:
        return ""
    try:
        active_vehicle_ids = set(map(str, traci.vehicle.getIDList()))
        if str(vehicle_id) not in active_vehicle_ids:
            return ""
        return " | ".join(map(str, traci.vehicle.getPersonIDList(vehicle_id)))
    except Exception:
        return ""


def safe_position(traci, pid: str):
    try:
        pos = traci.person.getPosition(pid)
        return pos[0], pos[1]
    except Exception:
        return "", ""


def runtime_state(traci, pid: str, expected_fallback_vehicle: str = "") -> dict:
    ids = safe_person_ids(traci)
    if pid not in ids:
        return {
            "present": False,
            "current_road": "",
            "current_vehicle": "",
            "remaining_stages": 0,
            "stage_type": "",
            "stage_type_name": "",
            "stage_line": "",
            "stage_edges": "",
            "stage_dest_stop": "",
            "stage_description": "",
            "stage_travel_time": "",
            "stage_arrival_pos": "",
            "position_x": "",
            "position_y": "",
            "speed": "",
            "inside_expected_fallback": False,
            "fallback_vehicle_person_ids": safe_vehicle_person_ids(traci, expected_fallback_vehicle),
        }

    try:
        road = str(traci.person.getRoadID(pid) or "")
    except Exception:
        road = ""
    try:
        veh = str(traci.person.getVehicle(pid) or "")
    except Exception:
        veh = ""
    try:
        speed = traci.person.getSpeed(pid)
    except Exception:
        speed = ""
    try:
        n = int(traci.person.getRemainingStages(pid))
    except Exception:
        n = 0

    stage_data = {
        "stage_type": "",
        "stage_type_name": "",
        "line": "",
        "edges": "",
        "destStop": "",
        "description": "",
        "travelTime": "",
        "arrivalPos": "",
    }
    if n > 0:
        try:
            stage_data = serialize_stage(traci.person.getStage(pid, 0))
        except Exception:
            pass

    x, y = safe_position(traci, pid)
    fallback_people = safe_vehicle_person_ids(traci, expected_fallback_vehicle)
    fallback_people_set = {x.strip() for x in fallback_people.split("|") if x.strip()}
    return {
        "present": True,
        "current_road": road,
        "current_vehicle": veh,
        "remaining_stages": n,
        "stage_type": stage_data.get("stage_type", ""),
        "stage_type_name": stage_data.get("stage_type_name", ""),
        "stage_line": stage_data.get("line", ""),
        "stage_edges": stage_data.get("edges", ""),
        "stage_dest_stop": stage_data.get("destStop", ""),
        "stage_description": stage_data.get("description", ""),
        "stage_travel_time": stage_data.get("travelTime", ""),
        "stage_arrival_pos": stage_data.get("arrivalPos", ""),
        "position_x": x,
        "position_y": y,
        "speed": speed,
        "inside_expected_fallback": bool(
            expected_fallback_vehicle
            and (veh == expected_fallback_vehicle or pid in fallback_people_set)
        ),
        "fallback_vehicle_person_ids": fallback_people,
    }


def write_plan_snapshot(traci, pid: str, event: str, t: float, stage_writer, text_file, note: str = ""):
    ids = safe_person_ids(traci)
    text_file.write(f"\n{'=' * 88}\n")
    text_file.write(f"{event} | person={pid} | t={t:.1f} ({format_hms(t)})\n")
    if note:
        text_file.write(f"NOTE: {note}\n")

    if pid not in ids:
        text_file.write("PERSON NOT PRESENT IN THE SIMULATION\n")
        text_file.flush()
        stage_writer.writerow({
            "snapshot_event": event,
            "sim_time": t,
            "sim_time_hms": format_hms(t),
            "person_id": pid,
            "person_present": False,
            "stage_index": "",
            "is_current_stage": "",
            "note": note,
        })
        return

    try:
        n = int(traci.person.getRemainingStages(pid))
    except Exception:
        n = 0
    text_file.write(f"remaining_stages={n}\n")

    if n == 0:
        stage_writer.writerow({
            "snapshot_event": event,
            "sim_time": t,
            "sim_time_hms": format_hms(t),
            "person_id": pid,
            "person_present": True,
            "stage_index": "",
            "is_current_stage": "",
            "note": note,
        })
        text_file.write("NO REMAINING STAGES\n")
        text_file.flush()
        return

    for index in range(n):
        try:
            data = serialize_stage(traci.person.getStage(pid, index))
        except Exception as exc:
            data = {
                "stage_type": "",
                "stage_type_name": "read_error",
                "description": str(exc),
            }
        row = {
            "snapshot_event": event,
            "sim_time": t,
            "sim_time_hms": format_hms(t),
            "person_id": pid,
            "person_present": True,
            "stage_index": index,
            "is_current_stage": index == 0,
            "note": note,
        }
        row.update(data)
        stage_writer.writerow(row)
        text_file.write(
            f"[{index}] type={data.get('stage_type')} ({data.get('stage_type_name')}) "
            f"line={data.get('line', '')!r} intended={data.get('intended', '')!r} "
            f"destStop={data.get('destStop', '')!r}\n"
        )
        text_file.write(
            f"    edges={data.get('edges', '')}\n"
            f"    description={data.get('description', '')!r} "
            f"travelTime={data.get('travelTime', '')} "
            f"depart={data.get('depart', '')} "
            f"arrivalPos={data.get('arrivalPos', '')}\n"
        )
    text_file.flush()


def run(args):
    """Run the event-driven controller and write all diagnostic outputs.

    The function prepares inputs and output files, starts SUMO through TraCI,
    schedules detection and lifecycle events, applies corrections, and always
    writes a final summary before closing the connection when possible.
    """
    t_global = pytime.time()
    setup_sumo_tools()
    import traci
    from traci.exceptions import TraCIException

    args.sumocfg = Path(args.sumocfg)
    args.population = Path(args.population)
    args.index_dir = Path(args.index_dir)
    args.output_dir = Path(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.focus_person_ids = [str(x) for x in (args.focus_person_ids or [])]
    args.skip_fallback_person_ids = {
        str(x) for x in (getattr(args, "skip_fallback_person_ids", None) or [])
    }
    if args.skip_fallback_person_ids:
        print(
            "[CRASH-GUARD] Fallback disabled for: "
            + ", ".join(sorted(args.skip_fallback_person_ids)),
            flush=True,
        )
    if args.sumo_error_log is None:
        args.sumo_error_log = args.output_dir / "sumo_errors.log"
    else:
        args.sumo_error_log = Path(args.sumo_error_log)
    controller_exception_path = args.output_dir / "controller_exception.log"
    controller_failed = False

    if args.net_file is None:
        args.net_file = extract_net_file_from_sumocfg(args.sumocfg)
    else:
        args.net_file = Path(args.net_file)
    if args.facilities_csv is not None:
        args.facilities_csv = Path(args.facilities_csv)

    pt_index = FuturePTIndex(args.index_dir)
    watched_stops = sorted(pt_index.watched_from_stops())
    all_person_rides = parse_population_rides(args.population)

    if args.all_persons:
        scope_ids = None
        person_rides = all_person_rides
        initial_trace_ids = set()
        print("\n=== GENERIC CONTROLLER — FULL POPULATION ===", flush=True)
        print(f"Indexed PT plans: {len(person_rides)} persons", flush=True)
    else:
        scope_ids = set(args.focus_person_ids)
        if not scope_ids:
            raise ValueError("Provide --focus-person-ids ... or use --all-persons")
        person_rides = {pid: all_person_rides.get(pid, []) for pid in scope_ids}
        initial_trace_ids = set(scope_ids)
        print("\n=== FOCUSED CONTROLLER — GENERIC LOGIC TEST ===", flush=True)
        print("Focused persons:", ", ".join(args.focus_person_ids), flush=True)
        for pid in args.focus_person_ids:
            print(f"{pid}: {len(person_rides.get(pid, []))} PT ride(s) in the plan", flush=True)

    net_helper = NetworkHelper(args.net_file)
    facilities = FacilitiesMapper(args.facilities_csv)

    original_plans_path = args.output_dir / "focused_original_plans.xml"
    runtime_path = args.output_dir / "focused_runtime_trace.csv"
    stages_path = args.output_dir / "focused_plan_snapshots.csv"
    readable_path = args.output_dir / "focused_plan_trace.txt"
    summary_path = args.output_dir / "focused_final_summary.csv"
    removed_activities_path = args.output_dir / "removed_activities_log.csv"
    if not args.all_persons:
        extract_original_person_plans(args.population, scope_ids, original_plans_path)

    runtime_fields = [
        "sim_time", "sim_time_hms", "event", "person_id", "present",
        "current_road", "current_vehicle", "expected_fallback_vehicle",
        "inside_expected_fallback", "fallback_vehicle_person_ids",
        "remaining_stages", "stage_type", "stage_type_name", "stage_line",
        "stage_edges", "stage_dest_stop", "stage_description",
        "stage_travel_time", "stage_arrival_pos", "position_x", "position_y",
        "speed", "decision", "action_result", "note",
    ]
    stage_fields = [
        "snapshot_event", "sim_time", "sim_time_hms", "person_id",
        "person_present", "stage_index", "is_current_stage", "stage_type",
        "stage_type_name", "vType", "line", "intended", "destStop",
        "description", "edges", "edge_count", "travelTime", "cost", "length",
        "depart", "departPos", "arrivalPos", "note",
    ]
    removed_activity_fields = [
        "event", "person_id", "activity_seq", "activity_type",
        "activity_edge_expected", "activity_pos_expected",
        "activity_edge_actual_before_removal", "activity_pos_actual_before_removal",
        "original_until", "original_until_hms", "original_duration",
        "first_active_time", "first_active_time_hms",
        "removal_time", "removal_time_hms",
        "time_spent_in_activity", "arrival_lateness",
        "removal_reason", "activity_skipped",
        "remaining_stages_before", "remaining_stages_after",
        "first_active_road", "stage_description_before",
    ]

    summary_fields = [
        "person_id", "correction_attempted", "correction_succeeded",
        "fallback_vehicle_id", "ever_boarded_expected_fallback",
        "disappeared_from_simulation", "disappearance_time",
        "final_present", "final_current_road", "final_current_vehicle",
        "final_remaining_stages", "final_stage_type", "final_stage_type_name",
        "final_stage_line", "final_stage_edges", "final_note",
    ]

    ride_pointer = defaultdict(int)
    waiting_state = {}
    no_future_state = {}
    corrected_info = {}
    correction_attempted = set()
    correction_succeeded = set()
    ever_present = set()
    disappeared = {}
    ever_boarded = set()
    last_runtime_signature = {}
    last_periodic_log = defaultdict(lambda: -10**12)
    last_decision = defaultdict(str)
    last_action = defaultdict(str)
    tracked_person_ids = set(initial_trace_ids)
    activity_runtime_state = {}

    sumo_cmd = build_sumo_cmd(args)
    print("SUMO command:", " ".join(map(str, sumo_cmd)), flush=True)

    traci.start(
    sumo_cmd,
    traceFile=str(args.output_dir / "traci_commands.py"),
    traceGetters=False)
    
    def write_runtime(writer, pid: str, t: float, event: str, decision="", action_result="", note="", force=False):
        expected_veh = corrected_info.get(pid, {}).get("fallback_vehicle_id", "")
        state = runtime_state(traci, pid, expected_veh)
        if state["present"]:
            ever_present.add(pid)
        if state.get("inside_expected_fallback"):
            ever_boarded.add(pid)

        signature = (
            state.get("present"), state.get("current_road"), state.get("current_vehicle"),
            state.get("remaining_stages"), state.get("stage_type"),
            state.get("stage_line"), state.get("stage_edges"),
            state.get("inside_expected_fallback"),
        )
        changed = signature != last_runtime_signature.get(pid)
        periodic = t - last_periodic_log[pid] >= args.trace_every
        if not (force or changed or periodic):
            return state

        row = {
            "sim_time": t,
            "sim_time_hms": format_hms(t),
            "event": event if event else ("state_changed" if changed else "periodic_state"),
            "person_id": pid,
            "expected_fallback_vehicle": expected_veh,
            "decision": decision or last_decision.get(pid, ""),
            "action_result": action_result or last_action.get(pid, ""),
            "note": note,
        }
        row.update(state)
        writer.writerow({k: row.get(k, "") for k in runtime_fields})
        last_runtime_signature[pid] = signature
        last_periodic_log[pid] = t
        return state

    try:
        with runtime_path.open("w", encoding="utf-8", newline="") as rf, \
             stages_path.open("w", encoding="utf-8", newline="") as sf, \
             removed_activities_path.open("w", encoding="utf-8", newline="") as af, \
             readable_path.open("w", encoding="utf-8") as tf:
            runtime_writer = csv.DictWriter(rf, fieldnames=runtime_fields)
            stage_writer = csv.DictWriter(sf, fieldnames=stage_fields)
            removed_activity_writer = csv.DictWriter(af, fieldnames=removed_activity_fields)
            runtime_writer.writeheader()
            stage_writer.writeheader()
            removed_activity_writer.writeheader()
            tf.write("STRATEGY B TRACE — PLACEHOLDERS RELEASED AT ORIGINAL ACTIVITY END TIMES\n")
            tf.write("Mode: " + ("full population" if args.all_persons else "focused") + "\n")
            if not args.all_persons:
                tf.write("Focused persons: " + ", ".join(args.focus_person_ids) + "\n")

            print("[OUTPUT]", original_plans_path.resolve(), flush=True)
            print("[OUTPUT]", runtime_path.resolve(), flush=True)
            print("[OUTPUT]", stages_path.resolve(), flush=True)
            print("[OUTPUT]", readable_path.resolve(), flush=True)
            print("[OUTPUT]", removed_activities_path.resolve(), flush=True)

            # ------------------------------------------------------------
            # Event-driven TraCI loop
            # ------------------------------------------------------------
            # The validated controller used to call simulationStep() and query
            # person state once per simulated second.  On a 27 h simulation this
            # means about 97,200 socket synchronizations.  Here Python wakes up
            # only for a detection scan, a lightweight lifecycle monitor, or an
            # exact known activity-release time.
            light_production_logging = bool(args.all_persons and not args.full_diagnostics)
            check_interval = max(1.0, float(args.check_every))
            monitor_interval = max(1.0, float(args.monitor_every))
            eps = 1e-7

            initial_sim_time = float(traci.simulation.getTime())
            next_scan = initial_sim_time + check_interval
            next_monitor = initial_sim_time + monitor_interval
            activity_release_schedule = {}
            scan_count = 0
            wall_loop_start = pytime.time()

            # Bus-stop subscriptions turn hundreds of socket requests per scan
            # into local reads of results delivered with simulationStep().
            busstop_subscriptions_enabled = False
            busstop_waiting_var = None
            if not args.disable_busstop_subscriptions:
                try:
                    from traci import constants as tc
                    busstop_waiting_var = tc.VAR_BUS_STOP_WAITING_IDS
                    subscribed = 0
                    for stop_id in watched_stops:
                        try:
                            traci.busstop.subscribe(stop_id, [busstop_waiting_var])
                            subscribed += 1
                        except Exception:
                            continue
                    busstop_subscriptions_enabled = subscribed > 0
                    print(
                        f"[FAST] Active bus-stop subscriptions: {subscribed}/{len(watched_stops)} stops.",
                        flush=True,
                    )
                except Exception as exc:
                    print(f"[WARN] Bus-stop subscriptions are unavailable; using direct queries: {exc}", flush=True)

            while True:
                current_t = float(traci.simulation.getTime())

                # When --end is provided, it is the primary stopping condition.
                # getMinExpectedNumber() may reach zero as soon as demand is exhausted
                # (often at 24:00), even when the requested run continues to 27:00.
                if args.end is not None:
                    if current_t >= float(args.end) - eps:
                        break
                elif traci.simulation.getMinExpectedNumber() <= 0:
                    break

                # Step 1: choose the next event time. The controller wakes only
                # for a detection scan, a lifecycle monitor, a known activity
                # release, or the configured simulation end.
                candidates = [next_scan, next_monitor]
                candidates.extend(
                    release_t for release_t in activity_release_schedule.values()
                    if float(release_t) > current_t + eps
                )
                if args.end is not None:
                    candidates.append(float(args.end))
                future_candidates = [float(x) for x in candidates if float(x) > current_t + eps]
                if not future_candidates:
                    target_t = current_t + max(1.0, monitor_interval)
                else:
                    target_t = min(future_candidates)

                traci.simulationStep(target_t)
                t = float(traci.simulation.getTime())

                due_release = any(float(x) <= t + eps for x in activity_release_schedule.values())
                due_monitor = t + eps >= next_monitor or due_release

                # Step 2: maintain already tracked or corrected persons. This
                # releases activity placeholders at the correct time and records
                # persons that have completed or left the simulation.
                if due_monitor:
                    current_ids = safe_person_ids(traci)
                    monitor_ids = sorted(tracked_person_ids | set(corrected_info.keys()))
                    for pid in monitor_ids:
                        if pid in current_ids:
                            activity_event = manage_current_activity_placeholder(
                                traci, pid, t, activity_runtime_state
                            )
                            if activity_event:
                                activity_release_schedule.pop(pid, None)
                                row = dict(activity_event)
                                row["original_until_hms"] = (
                                    format_hms(row.get("original_until"))
                                    if float(row.get("original_until", -1)) >= 0 else ""
                                )
                                row["first_active_time_hms"] = format_hms(row.get("first_active_time"))
                                row["removal_time_hms"] = format_hms(row.get("removal_time"))
                                removed_activity_writer.writerow(
                                    {k: row.get(k, "") for k in removed_activity_fields}
                                )
                                note = (
                                    f"activity={row.get('activity_type', '')}; "
                                    f"edge={row.get('activity_edge_actual_before_removal', '')}; "
                                    f"until={row.get('original_until', '')}; "
                                    f"reason={row.get('removal_reason', '')}; "
                                    f"stages={row.get('remaining_stages_before', '')}->"
                                    f"{row.get('remaining_stages_after', '')}"
                                )
                                if not light_production_logging:
                                    write_plan_snapshot(
                                        traci, pid, "ACTIVITY_REMOVED", t, stage_writer, tf, note
                                    )
                                write_runtime(
                                    runtime_writer, pid, t, "activity_removed",
                                    note=note, force=True
                                )

                            release_t = current_placeholder_release_time(
                                traci, pid, t, activity_runtime_state
                            )
                            if release_t is not None and float(release_t) > t + eps:
                                activity_release_schedule[pid] = float(release_t)
                            else:
                                activity_release_schedule.pop(pid, None)

                            ever_present.add(pid)
                            if not light_production_logging:
                                write_runtime(runtime_writer, pid, t, "")
                        elif pid in ever_present and pid not in disappeared:
                            activity_release_schedule.pop(pid, None)
                            disappeared[pid] = t
                            write_runtime(
                                runtime_writer, pid, t,
                                "person_disappeared_from_simulation",
                                note="The person is no longer in traci.person.getIDList(): the plan ended or SUMO removed the person.",
                                force=True,
                            )
                            if not light_production_logging:
                                write_plan_snapshot(
                                    traci, pid, "PERSON_DISAPPEARED", t, stage_writer, tf,
                                    "The person left the simulation.",
                                )

                    while next_monitor <= t + eps:
                        next_monitor += monitor_interval

                if (not args.all_persons and args.stop_when_focus_complete
                        and all(pid in disappeared for pid in args.focus_person_ids)):
                    print(
                        f"[STOP] All {len(args.focus_person_ids)} focused persons left the simulation at {format_hms(t)}.",
                        flush=True,
                    )
                    break

                if t + eps < next_scan:
                    continue

                # Step 3: run the heavier stranded-passenger detection scan.
                # Active vehicles are grouped by line once per scan so delayed-bus
                # checks do not repeatedly traverse the complete vehicle list.
                scan_count += 1
                vehicle_ids_by_line = {}
                if not args.disable_live_bus_check:
                    vehicle_ids_by_line = build_vehicle_ids_by_line(traci)

                # Step 4: collect passengers currently waiting at watched stops.
                # In production scope every indexed passenger is considered; in
                # focused mode the set is restricted to the requested person IDs.
                persons_at_stop = {}
                for stop_id in watched_stops:
                    try:
                        if busstop_subscriptions_enabled:
                            result = traci.busstop.getSubscriptionResults(stop_id) or {}
                            pids_raw = result.get(busstop_waiting_var, ())
                        else:
                            pids_raw = traci.busstop.getPersonIDs(stop_id)
                        pids = set(map(str, pids_raw or ()))
                    except TraCIException:
                        continue
                    except Exception:
                        continue
                    selected = pids if scope_ids is None else scope_ids.intersection(pids)
                    for pid in selected:
                        if pid in person_rides:
                            persons_at_stop[pid] = stop_id

                # Step 5: analyse each waiting passenger exactly once per scan.
                # Corrected persons are handled by the lightweight monitor and are
                # therefore excluded from repeated stranded detection.
                for pid in sorted(persons_at_stop):
                    if pid in corrected_info:
                        continue
                    current_stop = persons_at_stop[pid]
                    ride_idx, ride, match_reason = find_expected_ride(
                        pid, current_stop, person_rides, ride_pointer
                    )
                    if ride is None:
                        last_decision[pid] = "unknown_expected_ride"
                        if not light_production_logging:
                            write_runtime(
                                runtime_writer, pid, t, "waiting_analysis",
                                decision="unknown_expected_ride",
                                note=f"No expected ride matches stop {current_stop}; match={match_reason}",
                                force=True,
                            )
                        continue

                    key = (current_stop, ride_idx, ride["from_stop"], ride["to_stop"], ride["line"])
                    if pid not in waiting_state or waiting_state[pid].get("key") != key:
                        waiting_state[pid] = {"first_seen_time": t, "key": key}
                        no_future_state.pop(pid, None)

                    # Step 6: first consult the static future-boarding index for
                    # the exact from-stop, to-stop, and line combination.
                    static_candidate = pt_index.next_boarding(
                        ride["from_stop"], ride["to_stop"], ride["line"], t
                    )
                    # Step 7: when the timetable has no future candidate, inspect
                    # active buses. This prevents a delayed but still usable bus from
                    # being mistaken for a permanently missing service.
                    live_candidate = None
                    if static_candidate is None and not args.disable_live_bus_check:
                        live_candidate = find_live_delayed_bus(
                            traci, ride["line"], ride["from_stop"], ride["to_stop"], vehicle_ids_by_line
                        )

                    if static_candidate is not None:
                        no_future_state.pop(pid, None)
                        next_boarding_time = float(static_candidate.get("boarding_time", 0))
                        time_until_next_bus = next_boarding_time - t
                        if time_until_next_bus > args.max_acceptable_wait:
                            decision = "future_bus_too_late"
                            note = (
                                "A future bus exists in the static index, but it arrives in "
                                f"{time_until_next_bus:.0f}s, beyond the accepted threshold. "
                                "No correction is applied."
                            )
                        else:
                            decision = "keep_waiting"
                            note = f"A future bus is available in {time_until_next_bus:.0f}s."
                    elif live_candidate is not None:
                        no_future_state.pop(pid, None)
                        decision = "wait_for_delayed_bus"
                        note = f"Active delayed bus detected: {live_candidate.get('vehicle_id', '')}"
                    else:
                        # Step 8: no static or live bus can serve the ride. Start or
                        # continue the confirmation timer; never correct on the first
                        # negative observation.
                        st = no_future_state.get(pid)
                        if st is None or st.get("key") != key:
                            no_future_state[pid] = {"first_no_future_time": t, "key": key}
                            st = no_future_state[pid]
                        elapsed = t - float(st["first_no_future_time"])
                        if elapsed < args.stranded_confirmation_time:
                            decision = "suspected_no_future_bus"
                            note = f"No future bus has been available for {elapsed:.0f}s; awaiting confirmation."
                        else:
                            decision = "confirmed_stranded"
                            note = f"No future bus has been available for {elapsed:.0f}s; correction triggered."
                            correction_attempted.add(pid)
                            tracked_person_ids.add(pid)
                            last_decision[pid] = decision
                            write_runtime(
                                runtime_writer, pid, t, "confirmed_stranded",
                                decision=decision, note=note, force=True,
                            )

                            # Step 9: apply an explicit crash guard when this person
                            # is known to make dynamic fallback unsafe.
                            if pid in args.skip_fallback_person_ids:
                                removed = False
                                removal_note = (
                                    "Fallback skipped by --skip-fallback-person-ids; "
                                    "the person is removed to protect the full run."
                                )
                                try:
                                    traci.person.remove(pid)
                                    removed = True
                                except Exception as remove_exc:
                                    removal_note += f" remove_failed={remove_exc}"
                                last_action[pid] = (
                                    "crash_guard_person_removed" if removed
                                    else "crash_guard_removal_failed"
                                )
                                write_runtime(
                                    runtime_writer, pid, t,
                                    "crash_guard_person_removed" if removed else "crash_guard_removal_failed",
                                    decision=decision,
                                    action_result=last_action[pid],
                                    note=removal_note, force=True,
                                )
                                print(
                                    f"[CRASH-GUARD] {pid} at {format_hms(t)} -> "
                                    + ("person removed" if removed else "removal failed"),
                                    flush=True,
                                )
                                continue

                            if not light_production_logging:
                                write_plan_snapshot(
                                    traci, pid, "BEFORE_CORRECTION", t, stage_writer, tf,
                                    f"Stop={current_stop}; ride={ride_idx}; line={ride['line']}; Strategy B direct to activity",
                                )
                            # Step 10: build and apply the validated Strategy B plan.
                            # Failures before mutation may leave the person untouched;
                            # failures after mutation are escalated and removed.
                            try:
                                info = apply_car_fallback_keep_person(
                                    traci, pid, ride, current_stop, t, args, net_helper, facilities
                                )
                                corrected_info[pid] = info
                                correction_succeeded.add(pid)
                                last_action[pid] = info.get("action_result", "")
                                if not light_production_logging:
                                    write_plan_snapshot(
                                        traci, pid, "AFTER_CORRECTION", t, stage_writer, tf,
                                        f"fallback_vehicle={info.get('fallback_vehicle_id', '')}; "
                                        f"fallback_line={info.get('fallback_line', '')}",
                                    )
                                write_runtime(
                                    runtime_writer, pid, t, "correction_applied",
                                    decision=decision,
                                    action_result=info.get("action_result", ""),
                                    note="Obsolete PT chain removed; direct taxi to the activity; final walk appended; later activities preserved at their original times.",
                                    force=True,
                                )
                                print(
                                    f"[CORRECTION] {pid} at {format_hms(t)} -> "
                                    f"{info.get('fallback_vehicle_id', '')}",
                                    flush=True,
                                )
                            except Exception as exc:
                                failure_note = str(exc)
                                partial_mutation = isinstance(exc, PartialMutationError)
                                if partial_mutation:
                                    failure_note = (
                                        f"PARTIAL_MUTATION (person state unsafe, forced removal): {failure_note}"
                                    )
                                if not light_production_logging:
                                    write_plan_snapshot(
                                        traci, pid, "CORRECTION_FAILED_CURRENT_PLAN", t, stage_writer, tf,
                                        failure_note,
                                    )
                                removed_after_failure = False
                                # A partially mutated person is never safe to keep,
                                # regardless of --keep-person-on-correction-failure:
                                # their plan inside SUMO is incoherent and can crash
                                # the native engine on a later simulationStep.
                                if args.remove_on_correction_failure or partial_mutation:
                                    try:
                                        traci.person.remove(pid)
                                        removed_after_failure = True
                                    except Exception as remove_exc:
                                        failure_note += f"; person_remove_failed={remove_exc}"
                                last_action[pid] = (
                                    f"car_fallback_keep_person_failed_person_removed:{failure_note}"
                                    if removed_after_failure
                                    else f"car_fallback_keep_person_failed:{failure_note}"
                                )
                                write_runtime(
                                    runtime_writer, pid, t,
                                    "correction_failed_person_removed" if removed_after_failure else "correction_failed",
                                    decision=decision,
                                    action_result=last_action[pid],
                                    note=failure_note, force=True,
                                )
                                print(
                                    f"[FAILURE] {pid}: {failure_note}"
                                    + (" -> person removed" if removed_after_failure else ""),
                                    flush=True,
                                )
                            continue

                    last_decision[pid] = decision
                    if not light_production_logging:
                        write_runtime(
                            runtime_writer, pid, t, "waiting_analysis",
                            decision=decision, note=note,
                        )

                while next_scan <= t + eps:
                    next_scan += check_interval

                if scan_count % max(1, int(args.print_every_scan)) == 0:
                    wall_elapsed = max(1e-9, pytime.time() - wall_loop_start)
                    sim_elapsed = max(0.0, t - initial_sim_time)
                    speed = sim_elapsed / wall_elapsed
                    if args.end is not None and speed > 0:
                        eta = max(0.0, float(args.end) - t) / speed
                        eta_text = _fmt_elapsed(eta)
                    else:
                        eta_text = "?"
                    print(
                        f"[SCAN {scan_count}] sim={format_hms(t)} | waiting={len(persons_at_stop)} | "
                        f"corrected={len(correction_succeeded)} | speed={speed:.1f}x | ETA~{eta_text}",
                        flush=True,
                    )

                if args.flush_every_scan:
                    rf.flush(); sf.flush(); af.flush(); tf.flush()

            final_t = float(traci.simulation.getTime())
            final_report_ids = sorted(
                tracked_person_ids | set(corrected_info.keys()) | correction_attempted
            )
            for pid in final_report_ids:
                write_runtime(
                    runtime_writer, pid, final_t, "FINAL_STATE",
                    note="State observed when the controller stops.", force=True,
                )
                write_plan_snapshot(
                    traci, pid, "FINAL_PLAN_SNAPSHOT", final_t, stage_writer, tf,
                    "Remaining plan at controller shutdown.",
                )

    except BaseException as exc:
        controller_failed = True
        tb = traceback.format_exc()
        try:
            controller_exception_path.write_text(tb, encoding="utf-8")
        except Exception:
            pass
        print("\n[CONTROLLER ERROR] A Python exception interrupted TraCI control.", flush=True)
        print(f"[CONTROLLER ERROR] Traceback written to: {controller_exception_path.resolve()}", flush=True)
        print(tb, flush=True)
        raise

    finally:
        if controller_failed:
            print("\n[INFO] The controller failed; closing TraCI after saving diagnostics.", flush=True)
        elif not args.nogui and not args.close_gui_on_end:
            print("\n[INFO] SUMO-GUI remains open. Close the window, then press Enter.")
            try:
                input()
            except Exception:
                pass
        try:
            final_t = float(traci.simulation.getTime())
        except Exception:
            final_t = ""

        # Build final summary before closing whenever possible.
        rows = []
        try:
            summary_ids = sorted(
                tracked_person_ids | set(corrected_info.keys()) | correction_attempted
            )
            for pid in summary_ids:
                expected_veh = corrected_info.get(pid, {}).get("fallback_vehicle_id", "")
                state = runtime_state(traci, pid, expected_veh)
                rows.append({
                    "person_id": pid,
                    "correction_attempted": pid in correction_attempted,
                    "correction_succeeded": pid in correction_succeeded,
                    "fallback_vehicle_id": expected_veh,
                    "ever_boarded_expected_fallback": pid in ever_boarded,
                    "disappeared_from_simulation": pid in disappeared,
                    "disappearance_time": disappeared.get(pid, ""),
                    "final_present": state.get("present", False),
                    "final_current_road": state.get("current_road", ""),
                    "final_current_vehicle": state.get("current_vehicle", ""),
                    "final_remaining_stages": state.get("remaining_stages", ""),
                    "final_stage_type": state.get("stage_type", ""),
                    "final_stage_type_name": state.get("stage_type_name", ""),
                    "final_stage_line": state.get("stage_line", ""),
                    "final_stage_edges": state.get("stage_edges", ""),
                    "final_note": "",
                })
        except Exception as exc:
            rows.append({"person_id": "", "final_note": f"summary_error:{exc}"})

        with summary_path.open("w", encoding="utf-8", newline="") as smf:
            sw = csv.DictWriter(smf, fieldnames=summary_fields)
            sw.writeheader()
            for row in rows:
                sw.writerow({k: row.get(k, "") for k in summary_fields})

        try:
            traci.close()
        except Exception as close_exc:
            # Do not crash on close, but never swallow silently: a failed
            # close usually means SUMO already died, which is diagnostic gold.
            print(f"[WARN] traci.close() failed (SUMO probably already stopped): {close_exc}", flush=True)

    print("\n=== TRACE COMPLETE ===")
    print("Original plans   :", original_plans_path.resolve())
    print("Runtime states   :", runtime_path.resolve())
    print("Plan snapshots   :", stages_path.resolve())
    print("Readable trace   :", readable_path.resolve())
    print("Final summary    :", summary_path.resolve())
    print("Released activities:", removed_activities_path.resolve())
    print("Total elapsed time:", _fmt_elapsed(pytime.time() - t_global))


def parse_args():
    """Define command-line options for focused diagnostics and production runs."""
    p = argparse.ArgumentParser(
        "Generic TraCI Strategy B controller: direct taxi, preserved placeholders, and logged activity releases"
    )
    p.add_argument("--sumocfg", required=True)
    p.add_argument("--population", required=True)
    p.add_argument("--index-dir", default="pt_index_out")
    p.add_argument("--output-dir", default="traci_focus_outputs")
    p.add_argument(
        "--focus-person-ids", nargs="*", default=["283361", "594501"],
        help="Focused test mode: only these persons are detected, corrected, and traced.",
    )
    p.add_argument(
        "--all-persons", action="store_true",
        help="Production mode: apply the same generic logic to every person in the population file.",
    )
    p.add_argument("--nogui", action="store_true")
    p.add_argument("--sumo-binary", default=None)
    p.add_argument("--begin", type=float, default=None)
    p.add_argument("--end", type=float, default=None)
    p.add_argument(
        "--seed", type=int, default=None,
        help="Fixed SUMO seed for reproducible GUI/non-GUI and teleportation tests.",
    )
    p.add_argument(
        "--time-to-teleport", type=float, default=None,
        help="Pass --time-to-teleport to SUMO. Use -1 to disable teleportation "
             "when diagnosing crashes involving fallback vehicles.",
    )
    p.add_argument("--check-every", type=int, default=30)
    p.add_argument("--stranded-confirmation-time", type=float, default=600)
    p.add_argument("--max-acceptable-wait", type=float, default=1800)
    p.add_argument("--log-repeat-every", type=float, default=600)
    p.add_argument("--trace-every", type=float, default=60,
                   help="Maximum interval between runtime-state records; changes are always logged immediately.")
    p.add_argument("--disable-live-bus-check", action="store_true")
    p.add_argument("--flush-every-scan", action="store_true")
    p.add_argument("--print-every-scan", type=int, default=10)
    p.add_argument("--facilities-csv", default=r"../2-POI's/facilities2sumo_multimode.csv")
    p.add_argument("--net-file", default=None)
    p.add_argument("--fallback-vtype", default="fallback_taxi")
    p.add_argument("--fallback-walk-speed", type=float, default=1.3)
    p.add_argument("--fallback-depart-buffer", type=float, default=20.0)
    p.add_argument(
        "--max-taxi-route-edges", type=int, default=250,
        help="Reject a correction when the taxi route exceeds this number of edges "
             "to prevent pathological network-wide detours. Use 0 to disable the limit.",
    )
    p.add_argument("--activity-placeholder-duration", type=float, default=172800.0,
                   help="Safety duration for an activity placeholder. It stays on the correct edge and is released at the original until time.")
    p.add_argument("--fallback-color", nargs=4, type=int, default=[255, 128, 0, 255])
    p.add_argument(
        "--remove-on-correction-failure", dest="remove_on_correction_failure",
        action="store_true", default=True,
        help="Remove the person when the fallback cannot be constructed. This is the default behavior.",
    )
    p.add_argument(
        "--keep-person-on-correction-failure", dest="remove_on_correction_failure",
        action="store_false",
        help="Diagnostic mode: keep the person when a correction fails before plan mutation.",
    )
    p.add_argument(
        "--monitor-every", type=float, default=60.0,
        help="Simulated-time interval between lightweight checks of already corrected persons."
    )
    p.add_argument(
        "--full-diagnostics", action="store_true",
        help="With --all-persons, keep detailed periodic snapshots and traces. This is slower."
    )
    p.add_argument(
        "--disable-busstop-subscriptions", action="store_true",
        help="Disable TraCI bus-stop subscriptions and query getPersonIDs separately for every stop."
    )
    p.add_argument(
        "--skip-fallback-person-ids", nargs="*", default=[],
        help=(
            "Person IDs for which dynamic fallback is disabled. "
            "A confirmed stranded person is removed to avoid a known deterministic SUMO crash."
        ),
    )
    p.add_argument(
        "--suppress-sumo-warnings", action="store_true", default=False,
        help="Suppress repetitive SUMO warnings during the run. Errors remain available in sumo_errors.log.",
    )
    p.add_argument(
        "--sumo-error-log", default=None,
        help="Path to the SUMO error log. Default: <output-dir>/sumo_errors.log.",
    )
    p.add_argument("--close-gui-on-end", action="store_true")
    p.add_argument("--stop-when-focus-complete", action="store_true",
                   help="Stop the controller as soon as all focused persons have left the simulation.")
    p.set_defaults(correction_policy="car_fallback_keep_person")
    return p.parse_args()


if __name__ == "__main__":
    run(parse_args())
