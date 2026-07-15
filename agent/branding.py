"""Product branding — LeadGen AI by Gyan Ranjan."""

APP_NAME = "LeadGen AI"
APP_TAGLINE = "Search any keywords → get real sales leads (any AI API)"
DEVELOPER = "Gyan Ranjan"
CREDIT = f"Developed by {DEVELOPER}"
VERSION = "1.2.1"


def banner_lines() -> str:
    return (
        f"[bold cyan]{APP_NAME}[/]  v{VERSION}\n"
        f"[dim]{APP_TAGLINE}[/]\n"
        f"[magenta]{CREDIT}[/]"
    )
