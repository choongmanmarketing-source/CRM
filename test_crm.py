from pathlib import Path

from crm import RestaurantCRM


def test_point_accumulation_and_redeem(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    crm = RestaurantCRM(db)

    c = crm.add_customer("Nina", "0999999999")
    assert c.points == 0
    assert c.tier == "Member"

    c = crm.record_purchase("0999999999", amount=250, earn_rate=10)
    assert c.points == 25

    c = crm.record_purchase("0999999999", amount=1000, earn_rate=10, use_points=20)
    assert c.points == 105


def test_tier_upgrade(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    crm = RestaurantCRM(db)
    crm.add_customer("Aom", "0888888888")

    c = crm.record_purchase("0888888888", amount=2500, earn_rate=10)
    assert c.points == 250
    assert c.tier == "Silver"
