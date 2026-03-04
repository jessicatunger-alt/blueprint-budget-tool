import json

from . import constraints

# load rules once
with open("data/rules.json") as f:
    RULES = json.load(f)


def _find_tier(total_budget):
    """Return the tier key for the given total budget."""
    for tier, data in RULES["tiers"].items():
        if data["min"] <= total_budget < data["max"]:
            return tier
    # fallback to highest tier
    return max(RULES["tiers"].keys(), key=lambda t: RULES["tiers"][t]["min"])


def _normalize(weights):
    """Normalize a dict of weights so they sum to 1."""
    total = sum(weights.values())
    if total <= 0:
        # default to equal split
        n = len(weights)
        return {k: 1 / n for k in weights}
    return {k: v / total for k, v in weights.items()}


def _apply_adjustments(weights, increases, decreases, delta=0.05):
    """Increase and decrease specified channels by a fixed delta, then renormalize."""
    for ch in increases:
        if ch in weights:
            weights[ch] = weights.get(ch, 0) + delta
    for ch in decreases:
        if ch in weights:
            weights[ch] = max(0, weights.get(ch, 0) - delta)
    return _normalize(weights)


def _apply_business_modifier(weights, business_type, monthly_budget):
    mods = RULES["business_modifiers"].get(business_type, {})
    weights = weights.copy()
    for ch in mods.get("increase", []):
        if ch in weights:
            weights[ch] += 0.05
    # conditional OOH for local service if budget allows
    if business_type == "Local Service" and monthly_budget >= 5000:
        weights["OOH"] = weights.get("OOH", 0) + 0.05
    return _normalize(weights)


def _apply_risk(weights, risk_tolerance):
    config = RULES["risk_tolerance"].get(risk_tolerance, {})
    max_channels = config.get("channels", len(weights))
    # if we already have fewer, nothing to do
    # otherwise remove smallest until we meet limit
    w = weights.copy()
    while len(w) > max_channels:
        # remove channel with smallest weight
        ch = min(w, key=w.get)
        val = w.pop(ch)
        # redistribute val to remaining proportionally
        for k in w:
            w[k] += w[k] / sum(w.values()) * val
    return _normalize(w)


def allocate(total_budget, campaign_duration, objective, business_type, risk_tolerance):
    """Main entry point. Returns allocation dict and monthly budgets."""
    monthly_budget = total_budget / max(campaign_duration, 1)
    tier = _find_tier(total_budget)
    base = RULES["tiers"][tier]["base"].copy()

    # apply objective adjustments
    obj = RULES["objective_adjustments"].get(objective, {})
    weights = _apply_adjustments(base, obj.get("increase", []), obj.get("decrease", []))

    # apply business type modifiers
    weights = _apply_business_modifier(weights, business_type, monthly_budget)

    # apply risk tolerance channel count
    weights = _apply_risk(weights, risk_tolerance)

    # convert to budget allocations and enforce constraints
    allocations = {}
    for ch, pct in weights.items():
        allocations[ch] = {
            "pct": pct,
            "total": pct * total_budget,
            "monthly": pct * monthly_budget,
        }

    allocations = constraints.enforce(allocations, total_budget, monthly_budget, campaign_duration)

    # after constraints we should re-normalize percentages
    total_pct = sum(v["pct"] for v in allocations.values())
    if total_pct > 0:
        for v in allocations.values():
            v["pct"] /= total_pct
    return allocations, monthly_budget
