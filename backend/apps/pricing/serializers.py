from rest_framework import serializers
from .models import PricingRule


class PricingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingRule
        fields = [
            "id",
            "tenant",
            "provider",
            "name",
            "mode",
            "type",
            "currency",
            "config",
            "conditions",
            "priority",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]
