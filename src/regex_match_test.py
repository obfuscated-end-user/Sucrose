import re

pl_id_list = [
    "https://www.youtube.com/playlist?list=PLMXUGj9FrochduGNZ_pzvaSZfLM26euNs",
    "https://www.youtube.com/playlist?list=PL6dLhflRXzKJPJGaJZovXqfjtXszakH-W",
    "https://www.youtube.com/playlist?list=PLAEbmFxcPciNUCG03fpi_sQ-XtPYuy0G_",
    "https://www.youtube.com/playlist?list=PLqYzJxUXOdUgGjMUgiJngx3UWH06coaLl",
    "https://www.youtube.com/watch?v=l4QrqO-bKLs&list=PLMXUGj9FrochduGNZ_pzvaSZfLM26euNs",
    "https://www.youtube.com/playlist?list=PLxoHK1S7LhWSU230SAT7fDUsLiXCwaBMo",
    "https://www.youtube.com/playlist?list=PLZK-y6Qrw3qN-AVavawYyH-fezNmXRoXx",
    "https://www.youtube.com/playlist?list=PLB88A2A0C911E18EF",
    "https://www.youtube.com/playlist?list=PLC-7UzzHTRvUgjPL1i3KI-KaWAlZSfYQt",
    "https://www.youtube.com/playlist?list=PLXDG0TgiA_kVBTbPuy-YZocFWTSdNOykW",
    "https://www.youtube.com/playlist?list=PLVx6HpgGCDbGspTo7ECzjq6KykGXBmbVn",
    "https://www.youtube.com/playlist?list=PLjNlQ2vXx1xbt30X8TcUfNzw_akVISXEu",
    "https://www.youtube.com/playlist?list=PLyAn2Ml1WRpa6O6FXr2nioRlwy7CVqgwC",
    "https://www.youtube.com/playlist?list=PLCVu_0ug01adtvdyZohCGSyu5Nr2237C2",
    "https://www.youtube.com/playlist?list=PLL2MvChfOyJom9X8TQkc0A_y39_YJjB5K",
    "https://www.youtube.com/playlist?list=PLbAFXJC0J5GaVjPNNw_i-oLNKc7bVQcFk",
    "https://www.youtube.com/playlist?list=PLIigXhZ7nJMmbrhGGtloocqfCVYHfoJrU",
    "https://www.youtube.com/playlist?list=PLWewvbjz7T-cvngENAn6eL4rcNAWaU8Tm",
    "https://www.youtube.com/playlist?list=PLgNjCSGFfYetqrZxlYiU8yWaBs-XMmdqg",
    "https://www.youtube.com/playlist?list=PLZx6GB7keq3mPIm4N0flJMPQF66ft0FRL",
    "https://www.youtube.com/playlist?list=PL6LSbBVD-WXPrT9zlI5l0UcmnahqINNZr",
    "https://www.youtube.com/playlist?list=PLQ0SvZmJ_LqBb3pjwmcQf2jLbXvrHU-Q6",
]

for id in pl_id_list:
    match = re.search("([\w-]{41}|[\w-]{34}|[\w-]{18})", id).groups()[0]
    print(f"{id} ({len(id)}) - {match} ({len(match)})")