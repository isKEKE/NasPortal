from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import psutil
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_current_user_optional
from app.crud import website as crud_website
from app.models.database import get_db
from app.schemas.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

RESOURCE_PATTERNS = [
    (("nas", "storage", "drive"), "fa-solid fa-hard-drive", "service"),
    (("jellyfin", "media", "plex"), "fa-solid fa-circle-play", "media"),
    (("grafana", "monitor", "metrics"), "fa-solid fa-gauge-high", "monitor"),
    (("portainer", "docker", "container"), "fa-brands fa-docker", "docker"),
    (("paperless", "docs", "document"), "fa-solid fa-leaf", "docs"),
    (("openai", "chatgpt", "ai"), "fa-solid fa-sparkles", "ai"),
    (("wiki", "book", "notion"), "fa-solid fa-book-open", "notes"),
    (("github", "gitlab", "code"), "fa-brands fa-github", "code"),
    (("finance", "money", "bank"), "fa-solid fa-coins", "links"),
    (("learning", "school", "course"), "fa-solid fa-graduation-cap", "docs"),
    (("backup", "archive"), "fa-solid fa-floppy-disk", "check"),
    (("router", "network", "wifi"), "fa-solid fa-wifi", "network"),
]


def _resource_meta(title: str, url: str, description: Optional[str]) -> dict[str, str]:
    parsed = urlparse(url)
    domain = (parsed.netloc or parsed.path).replace("www.", "")
    text = f"{title} {description or ''} {domain}".lower()

    icon_class = "fa-solid fa-globe"
    category = "resource"
    for keywords, candidate_icon, candidate_category in RESOURCE_PATTERNS:
        if any(keyword in text for keyword in keywords):
            icon_class = candidate_icon
            category = candidate_category
            break

    subtitle = (description or "").strip() or category
    return {
        "domain": domain or "resource.local",
        "icon_class": icon_class,
        "category": category,
        "subtitle": subtitle,
    }


def _portal_items(websites) -> list[dict]:
    items = []
    for site in websites:
        meta = _resource_meta(site.title, site.url, site.description)
        items.append(
            {
                "id": site.id,
                "title": site.title,
                "url": site.url,
                "description": site.description
                or "Launch this resource from your terminal portal.",
                "is_public": bool(site.is_public),
                "owner_username": getattr(site.owner, "username", None),
                **meta,
            }
        )
    return items


def _vps_status() -> dict:
    cpu_percent = round(psutil.cpu_percent(interval=None), 1)
    memory = psutil.virtual_memory()
    storage = psutil.disk_usage("/")
    latency_ms = max(1, round(psutil.cpu_times_percent(interval=None).idle / 5))
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_seconds = max(0, int((datetime.now() - boot_time).total_seconds()))
    uptime_hours = uptime_seconds // 3600
    uptime_days = uptime_hours // 24
    uptime_label = (
        f"{uptime_days}d {uptime_hours % 24}h"
        if uptime_days
        else f"{uptime_hours}h"
    )

    return {
        "updated_at": datetime.now().strftime("%H:%M:%S"),
        "metrics": [
            {
                "key": "cpu",
                "label": "CPU Load",
                "value": cpu_percent,
                "display": f"{cpu_percent:g}",
                "unit": "%",
                "accent": "blue",
                "progress": min(max(cpu_percent, 0), 100),
                "icon_class": "fa-solid fa-microchip",
            },
            {
                "key": "memory",
                "label": "Memory",
                "value": round(memory.used / 1024**3, 1),
                "display": f"{memory.used / 1024**3:.1f}",
                "unit": f"GB / {memory.total / 1024**3:.0f}GB",
                "accent": "green",
                "progress": min(max(memory.percent, 0), 100),
                "icon_class": "fa-solid fa-memory",
            },
            {
                "key": "storage",
                "label": "Storage",
                "value": round(storage.percent, 1),
                "display": f"{storage.percent:g}",
                "unit": "% used",
                "accent": "amber",
                "progress": min(max(storage.percent, 0), 100),
                "icon_class": "fa-solid fa-hard-drive",
            },
            {
                "key": "latency",
                "label": "Latency",
                "value": latency_ms,
                "display": str(latency_ms),
                "unit": "ms local",
                "accent": "blue",
                "progress": min(max(latency_ms * 4, 8), 100),
                "icon_class": "fa-solid fa-wave-square",
            },
        ],
        "monitor": {
            "title": "VPS monitor",
            "lines": [
                f"CPU cores: {psutil.cpu_count(logical=True)} online",
                f"Memory used: {memory.percent:g}%",
                f"Uptime: {uptime_label}",
                f"Updated: {datetime.now().strftime('%H:%M:%S')}",
            ],
        },
    }


@router.get("/", response_class=HTMLResponse)
async def read_portal(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if current_user is None:
        return RedirectResponse(url="/auth/login", status_code=303)

    websites = crud_website.get_websites_by_user(db, user_id=current_user.id)
    portal_items = _portal_items(websites)
    status = _vps_status()

    hero_links = [
        {"label": "Terminal", "href": "#terminal-section"},
        {"label": "Apps", "href": "#apps-section"},
    ]

    return templates.TemplateResponse(
        request,
        "portal.html",
        {
            "request": request,
            "websites": websites,
            "portal_items": portal_items,
            "metrics": status["metrics"],
            "portal_status": status["monitor"]["lines"],
            "hero_links": hero_links,
            "current_username": current_user.username,
            "current_user": current_user,
        },
    )


@router.get("/api/vps/status")
async def get_vps_status(current_user: User = Depends(get_current_user)):
    return _vps_status()
