from redteam.core.models import Asset, Endpoint
from redteam.core.workspace import get_db
from redteam.core.scope_guard import validate_url

def add_asset(name: str, kind: str, value: str, source: str = "manual", notes: str = ""):
    item = Asset(kind=kind, value=value, source=source, notes=notes)
    get_db(name).insert("assets", item.model_dump())
    return item

def add_endpoint(name: str, method: str, url: str, source: str = "manual", notes: str = ""):
    validate_url(name, url)
    item = Endpoint(method=method.upper(), url=url, source=source, notes=notes)
    get_db(name).insert("endpoints", item.model_dump())
    return item
