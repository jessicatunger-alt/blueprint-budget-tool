def enforce(allocations, total_budget, monthly_budget, campaign_duration):
    """Remove channels that violate minimum spend rules and redistribute budget.

    allocations: dict of channel -> {pct,total,monthly}
    total_budget: overall campaign budget
    monthly_budget: computed monthly spend
    campaign_duration: months
    """

    # remove channels one at a time to avoid eliminating entire set
    while True:
        # identify violators in priority order
        removal_candidate = None
        # check tv threshold first
        if "TV / BVOD" in allocations and monthly_budget < 300000:
            removal_candidate = "TV / BVOD"
        else:
            # find any channel under monthly 5k (and not the only one left)
            smalls = [ch for ch, v in allocations.items() if v["monthly"] < 5000]
            if smalls and len(allocations) > 1:
                # pick the smallest monthly channel
                removal_candidate = min(smalls, key=lambda c: allocations[c]["monthly"])
            # paid social special rule
            if (
                removal_candidate is None
                and "Paid Social" in allocations
                and allocations["Paid Social"]["monthly"] < 20000
                and len(allocations) > 1
            ):
                removal_candidate = "Paid Social"
        if not removal_candidate:
            break
        # remove it and redistribute
        allocations.pop(removal_candidate, None)
        if allocations:
            total = sum(v["pct"] for v in allocations.values())
            for v in allocations.values():
                v["pct"] /= total
                v["monthly"] = v["pct"] * monthly_budget
                v["total"] = v["pct"] * total_budget
    return allocations
