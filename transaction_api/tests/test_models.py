import pytest
from transaction_api.models import *
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db


class TestAPIModel:

    def test_tier_can_be_created(self):
        tier1 = mixer.blend(Tier, tier_name="Basic")
        tier_result = Tier.objects.last()  # getting the last tier
        assert tier_result.tier_name == "Basic"

    def test_tier_str_return(self):
        tier1 = mixer.blend(Tier, tier_name="Basic")
        tier_result = Tier.objects.last()  # getting the last tier
        assert str(tier_result) == "Basic"





    