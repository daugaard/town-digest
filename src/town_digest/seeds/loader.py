from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from town_digest.db import get_session_factory
from town_digest.models import Edition, EmailAlias

DEV_SEED_DATA: dict[str, tuple[dict[str, str | None | tuple[str, ...]], ...]] = {
    "editions": (
        {
            "name": "East Windsor / Hightstown / Twin Rivers",
            "slug": "east-windsor",
            "state": "NJ",
            "description": "The latest news and events from East Windsor, Hightstown, and the Twin Rivers community in New Jersey.",
            "aliases": ("tdigest+east-windsor@run.box",),
        },
    )
}


def seed_dev_database() -> dict[str, int]:
    """Load baseline development seed data into the configured database."""
    session_factory = get_session_factory()
    with session_factory() as session:
        result = _seed_dev_data(session)
        session.commit()
    return result


def _seed_dev_data(session: Session) -> dict[str, int]:
    editions_created = 0
    aliases_created = 0

    for edition_seed in DEV_SEED_DATA["editions"]:
        name = edition_seed["name"]
        slug = edition_seed["slug"]
        state = edition_seed["state"]
        description = edition_seed["description"]
        aliases = edition_seed["aliases"]

        existing_edition = session.execute(
            select(Edition.id).where(Edition.slug == slug)
        ).scalar_one_or_none()
        if existing_edition is not None:
            raise ValueError(f"Seed aborted: edition with slug '{slug}' already exists.")

        edition = Edition(
            name=name,
            slug=slug,
            state=state,
            description=description,
        )
        session.add(edition)
        session.flush()
        editions_created += 1

        for alias_address in aliases:
            existing_alias = session.execute(
                select(EmailAlias.id).where(EmailAlias.address == alias_address)
            ).scalar_one_or_none()
            if existing_alias is not None:
                raise ValueError(f"Seed aborted: email alias '{alias_address}' already exists.")
            session.add(EmailAlias(edition_id=edition.id, address=alias_address))
            aliases_created += 1

    return {
        "editions_created": editions_created,
        "aliases_created": aliases_created,
    }
