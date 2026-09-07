"""
CLI entry point — run the daily scan from the command line.
"""
from scans.daily_runner import run_daily_scan, format_discord_report


def main():
    import sys
    import json

    result = run_daily_scan()
    report = format_discord_report(result)

    # If --json flag, output structured data
    if "--json" in sys.argv:
        output = json.dumps(result, indent=2, default=str)
        print(output)
    else:
        print(report)


if __name__ == "__main__":
    main()