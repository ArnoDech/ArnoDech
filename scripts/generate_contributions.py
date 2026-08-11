import html
import json
import math
import os
from pathlib import Path
from urllib.request import Request, urlopen


QUERY = """
query ($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""


def fetch_contributions(username: str, token: str) -> dict:
    payload = json.dumps({
        "query": QUERY,
        "variables": {"login": username},
    }).encode()

    request = Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "minimal-purple-contribution-landscape",
        },
    )

    with urlopen(request, timeout=30) as response:
        result = json.load(response)

    if result.get("errors"):
        raise RuntimeError(result["errors"])

    user = result["data"]["user"]
    if not user:
        raise RuntimeError(f"Utilisateur GitHub introuvable : {username}")

    return user["contributionsCollection"]["contributionCalendar"]


def shade(color: str, factor: float) -> str:
    color = color.lstrip("#")
    values = [
        min(255, int(int(color[i:i + 2], 16) * factor))
        for i in (0, 2, 4)
    ]
    return "#" + "".join(f"{value:02X}" for value in values)


def polygon(points: list[tuple[float, float]], color: str) -> str:
    coordinates = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{coordinates}" fill="{color}"/>'


def generate_svg(calendar: dict, username: str) -> str:
    weeks = calendar["weeks"]
    total = calendar["totalContributions"]

    counts = [
        day["contributionCount"]
        for week in weeks
        for day in week["contributionDays"]
    ]
    maximum = max(counts, default=1) or 1

    colors = ["#241A35", "#5B21B6", "#7C3AED", "#A78BFA", "#DDD6FE"]
    heights = [0, 7, 13, 20, 28]

    width, height = 980, 540
    origin_x, origin_y = 115, 115
    step_x, step_y = 14.5, 5.7
    tile_width, tile_height = 18, 10

    cells = []
    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week["contributionDays"]):
            cells.append((
                week_index,
                day_index,
                day["contributionCount"],
                day["date"],
            ))

    cells.sort(key=lambda cell: (cell[0] + cell[1], cell[0]))

    svg = [f"""
<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0F0919"/>
      <stop offset="100%" stop-color="#180D29"/>
    </linearGradient>

    <radialGradient id="glow">
      <stop offset="0%" stop-color="#7C3AED" stop-opacity=".24"/>
      <stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/>
    </radialGradient>

    <filter id="shadow">
      <feDropShadow dx="0" dy="5" stdDeviation="6"
                    flood-color="#000000" flood-opacity=".35"/>
    </filter>
  </defs>

  <rect x="1" y="1" width="{width - 2}" height="{height - 2}"
        rx="24" fill="url(#background)" stroke="#302044"/>

  <ellipse cx="500" cy="290" rx="390" ry="220" fill="url(#glow)"/>

  <text x="42" y="47" fill="#F5F3FF"
        font-family="Inter, Segoe UI, Arial, sans-serif"
        font-size="21" font-weight="700" letter-spacing="2">
    CONTRIBUTION LANDSCAPE
  </text>

  <text x="42" y="72" fill="#A78BFA"
        font-family="Inter, Segoe UI, Arial, sans-serif"
        font-size="13">
    @{html.escape(username)}
  </text>

  <text x="930" y="46" text-anchor="end" fill="#F5F3FF"
        font-family="Inter, Segoe UI, Arial, sans-serif"
        font-size="25" font-weight="700">
    {total}
  </text>

  <text x="930" y="68" text-anchor="end" fill="#8B7A9F"
        font-family="Inter, Segoe UI, Arial, sans-serif"
        font-size="11" letter-spacing="1.4">
    CONTRIBUTIONS
  </text>

  <g filter="url(#shadow)">
"""]

    for week_index, day_index, count, date in cells:
        center_x = origin_x + (week_index - day_index) * step_x
        center_y = origin_y + (week_index + day_index) * step_y

        if count == 0:
            level = 0
        else:
            ratio = math.log1p(count) / math.log1p(maximum)
            level = min(4, max(1, math.ceil(ratio * 4)))

        block_height = heights[level]
        color = colors[level]

        top = [
            (center_x, center_y - block_height),
            (center_x + tile_width / 2, center_y + tile_height / 2 - block_height),
            (center_x, center_y + tile_height - block_height),
            (center_x - tile_width / 2, center_y + tile_height / 2 - block_height),
        ]

        if level == 0:
            svg.append(polygon(top, color))
            continue

        bottom = [(x, y + block_height) for x, y in top]

        left_face = [top[2], top[3], bottom[3], bottom[2]]
        right_face = [top[1], top[2], bottom[2], bottom[1]]

        svg.append(f"<g><title>{date}: {count} contributions</title>")
        svg.append(polygon(left_face, shade(color, 0.48)))
        svg.append(polygon(right_face, shade(color, 0.68)))
        svg.append(polygon(top, color))
        svg.append("</g>")

    svg.append(f"""
  </g>

  <line x1="42" y1="482" x2="938" y2="482"
        stroke="#39264F" stroke-width="1"/>

  <circle cx="50" cy="510" r="4" fill="#7C3AED"/>

  <text x="64" y="515" fill="#C4B5D5"
        font-family="Inter, Segoe UI, Arial, sans-serif"
        font-size="13">
    {total} contributions
  </text>

  <text x="930" y="515" text-anchor="end" fill="#8B7A9F"
        font-family="Inter, Segoe UI, Arial, sans-serif"
        font-size="11" letter-spacing="1.4">
    LAST 12 MONTHS
  </text>
</svg>
""")

    return "".join(svg)


def main() -> None:
    username = os.environ["GITHUB_USERNAME"]
    token = os.environ["GITHUB_TOKEN"]

    calendar = fetch_contributions(username, token)
    svg = generate_svg(calendar, username)

    output = Path("assets/contribution-landscape.svg")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")

    print(f"Generated {output} for @{username}")


if __name__ == "__main__":
    main()
