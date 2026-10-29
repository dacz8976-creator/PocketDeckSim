#!/usr/bin/env python3
"""Plan-following bot (opts in to pdl_events only). Usage: plan_follower_bot.py --seed N [--log PATH]

A PlanSource proposes a whole sequence of actions; the PlanFollower plays it step by step and
re-asks the source when the plan is stale or when something happened since the last decide
(pdl_since_last counters)."""
import argparse
import json
import random
import sys

COUNTERS = (
    ("opponent_choice", "opponent_choices"),
    ("chance", "chance_events"),
    ("draw_mine", "cards_left_deck_mine"),
    ("draw_opponent", "cards_left_deck_opponent"),
)


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


class PlanSource:
    def propose(self, msg):
        """Return the planned sequence of `action` objects."""
        raise NotImplementedError


class DummyPlanSource(PlanSource):
    def __init__(self, seed):
        self.seed = seed

    def propose(self, msg):
        plan = [a["action"] for a in msg["actions"]]
        random.Random(self.seed * 7919 + msg["ply"]).shuffle(plan)
        return plan


class PlanFollower:
    def __init__(self, source):
        self.source = source
        self.plan = None

    def _matches(self, step, msg):
        key = canon(step)
        return [a["i"] for a in msg["actions"] if canon(a["action"]) == key]

    def decide(self, msg):
        since = msg.get("pdl_since_last") or {}
        reason = None
        if self.plan:
            for name, key in COUNTERS:
                if since.get(key, 0) > 0:
                    reason = name
                    break
            if reason is not None:
                self.plan = None
        fresh = False
        if not self.plan:
            self.plan = list(self.source.propose(msg))
            fresh = True
        matches = self._matches(self.plan[0], msg)
        if not matches:
            if reason is None:
                reason = "stale"
            self.plan = list(self.source.propose(msg))
            fresh = True
            matches = self._matches(self.plan[0], msg)
        i = min(matches)
        assert any(a["i"] == i for a in msg["actions"])
        self.plan.pop(0)
        record = {
            "ply": msg["ply"],
            "pdl_since_last": since,
            "reask_reason": reason,
            "played_from_saved_plan": not fresh,
            "i": i,
        }
        return i, record


def send(message):
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--log")
    args = parser.parse_args()
    follower = PlanFollower(DummyPlanSource(args.seed))
    log = open(args.log, "w") if args.log else None
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            kind = msg.get("type")
            if kind == "hello":
                send({"type": "hello", "name": "plan_follower_bot.py", "pdl_events": True})
            elif kind == "decide":
                i, record = follower.decide(msg)
                if log:
                    log.write(json.dumps(record) + "\n")
                    log.flush()
                send({"i": i})
    finally:
        if log:
            log.close()


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt, BrokenPipeError):
        pass
