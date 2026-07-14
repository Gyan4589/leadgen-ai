"""Product branding — LeadGen by Gyan Ranjan."""

APP_NAME = "LeadGen AI"
APP_TAGLINE = "Search any keywords → get real sales leads"
DEVELOPER = "Gyan Ranjan"
CREDIT = f"Developed by {DEVELOPER}"
VERSION = "1.1.0"


def banner_lines() -> str:
    return (
        f"[bold cyan]{APP_NAME}[/]  v{VERSION}\n"
        f"[dim]{APP_TAGLINE}[/]\n"
        f"[magenta]{CREDIT}[/]"
    )
