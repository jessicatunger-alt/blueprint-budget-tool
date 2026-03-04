"""Generate strategic rationale text for an allocation."""

def generate(objective, business_type, risk_tolerance, channels):
    """Return a list of bullet point strings based on inputs."""
    bullets = []

    # base principle statements
    bullets.append(
        "Brand and performance work together; the mix balances long-term fame with short-term ROI."
    )
    bullets.append(
        "Marketing builds both mental and physical availability, so we spread investment across media."
    )

    # channel-specific language
    if any("Video" in ch or ch == "YouTube" for ch in channels):
        bullets.append(
            "High-attention video media drive greater effectiveness and support emotional creative."
        )
    if "Search" in channels or "Paid Social" in channels:
        bullets.append(
            "Performance channels like search and social deliver measurable response while supporting brand goals."
        )
    if "OOH" in channels:
        bullets.append(
            "OOH adds reach and supports memory encoding in urban contexts."
        )

    # objective-driven language
    if objective == "Awareness":
        bullets.append(
            "Awareness objectives lean on broad-reach formats to ignite mental availability."
        )
    elif objective == "Performance":
        bullets.append(
            "Performance focus shifts spend to direct response channels without abandoning brand drivers."
        )
    else:  # Growth
        bullets.append(
            "Growth strategy keeps a balanced, always-on approach across channels."
        )

    # risk tolerance effect
    if risk_tolerance == "Low":
        bullets.append(
            "A lower-risk stack uses fewer channels for clarity and executional simplicity."
        )
    elif risk_tolerance == "High":
        bullets.append(
            "High-risk tolerance allows a broader, multi-channel portfolio to chase incremental returns."
        )

    # Grace Kite note
    bullets.append(
        "We follow Grace Kite’s “lots of little” idea: many small, well-targeted exposures beat a few big bursts."
    )

    # ensure 4-6 bullets
    # if more than 6, truncate; if fewer, pad with generic
    if len(bullets) > 6:
        bullets = bullets[:6]
    while len(bullets) < 4:
        bullets.append("The media stack is designed to be coherent and simple to activate.")

    return bullets
