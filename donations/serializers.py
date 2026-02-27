from decimal import Decimal

from rest_framework import serializers

from .models import Donation


class DonationSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(write_only=True, required=False)
    lastName = serializers.CharField(write_only=True, required=False)
    paymentMethod = serializers.CharField(write_only=True, required=False)
    paymentToken = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "donor_name",
            "email",
            "phone",
            "amount",
            "currency",
            "payment_method",
            "anonymous",
            "message",
            "status",
            "provider",
            "external_reference",
            "gateway_event_id",
            "completed_at",
            "failed_reason",
            "created_at",
            "firstName",
            "lastName",
            "paymentMethod",
            "paymentToken",
        ]
        read_only_fields = [
            "status",
            "provider",
            "external_reference",
            "gateway_event_id",
            "completed_at",
            "failed_reason",
            "created_at",
        ]
        extra_kwargs = {
            "donor_name": {"required": False},
            "payment_method": {"required": False},
            "phone": {"required": False},
            "anonymous": {"required": False},
            "message": {"required": False},
        }

    def validate_amount(self, value):
        if value is None or Decimal(value) <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_currency(self, value):
        allowed = {"USD", "KES", "EUR", "GBP"}
        next_value = (value or "").upper().strip()
        if next_value not in allowed:
            raise serializers.ValidationError("Currency must be one of USD, KES, EUR, GBP.")
        return next_value

    def validate(self, attrs):
        first_name = attrs.pop("firstName", "").strip()
        last_name = attrs.pop("lastName", "").strip()
        payment_method_input = attrs.pop("paymentMethod", "").strip().lower()
        payment_token = attrs.pop("paymentToken", "").strip()

        if not attrs.get("donor_name"):
            full_name = f"{first_name} {last_name}".strip()
            attrs["donor_name"] = full_name or "Anonymous Donor"

        method_map = {
            "visa": "card",
            "card": "card",
            "paypal": "paypal",
            "mpesa": "mpesa",
            "m-pesa": "mpesa",
            "bank": "bank",
        }

        if payment_method_input and not attrs.get("payment_method"):
            attrs["payment_method"] = method_map.get(payment_method_input, "mpesa")

        attrs.setdefault("payment_method", "mpesa")
        attrs.setdefault("anonymous", False)

        # Frontend may send M-Pesa phone through paymentToken.
        if attrs.get("payment_method") == "mpesa" and not attrs.get("phone") and payment_token:
            attrs["phone"] = payment_token

        if payment_token:
            note = attrs.get("message", "")
            prefix = "Gateway token"
            token_note = f"{prefix}: {payment_token}"
            attrs["message"] = f"{note}\n{token_note}".strip()

        return attrs
