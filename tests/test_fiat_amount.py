from decimal import Decimal

from cdp.client.models.fiat_amount import FiatAmount as FiatAmountModel
from cdp.fiat_amount import FiatAmount


def test_fiat_amount_from_model():
    """Test converting a FiatAmount model to a FiatAmount."""
    model = FiatAmountModel(amount="100.50", currency="USD")
    fiat_amount = FiatAmount.from_model(model)

    assert fiat_amount.amount == Decimal("100.50")
    assert fiat_amount.currency == "USD"


def test_fiat_amount_properties():
    """Test FiatAmount properties."""
    fiat_amount = FiatAmount(amount=Decimal("50.25"), currency="USD")

    assert fiat_amount.amount == Decimal("50.25")
    assert fiat_amount.currency == "USD"


def test_fiat_amount_str_representation():
    """Test string representation of FiatAmount."""
    fiat_amount = FiatAmount(amount=Decimal("75.00"), currency="USD")
    expected_str = "FiatAmount(amount: '75', currency: 'USD')"

    assert str(fiat_amount) == expected_str
    assert repr(fiat_amount) == expected_str


def test_fiat_amount_repr():
    """Test repr of FiatAmount."""
    fiat_amount = FiatAmount(amount=Decimal("75.00"), currency="USD")
    assert repr(fiat_amount) == "FiatAmount(amount: '75', currency: 'USD')"
